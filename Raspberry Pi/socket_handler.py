import threading
import socket
import json
import time


class SocketHandler:
    """Class for handling socket communication with the Raspberry Pi.

    Methods:
        start_listening:
            Start listening for data from the topside PC.
        get_controller_commands:
            Get the controller commands.
        set_sensor_data:
            Set the sensor data.
    """
    def __init__(self, port: int = 5600, buffer_size: int = 1024) -> None:
        """Initialize the SocketHandler object.

        Args:
            port (int, optional):
                The port number to connect to.
                Defaults to 5600.
            buffer_size (int, optional):
                The size of the reception buffer.
                Defaults to 1024.
        """
        self._port: int = port
        self._buffer_size: int = buffer_size

        self._commands_lock: threading.Lock = threading.Lock()
        self._sensors_lock: threading.Lock = threading.Lock()

        self._controller_commands: dict | None = None
        self._controller_commands_available: bool = False

        self._client_socket: socket.socket | None = None

        self._sensor_data: dict[str, dict] | None = None
        self._sensor_data_available: bool = False

        self._data_to_send: dict | None = None

        self._last_send_time = time.time_ns()

    def get_controller_commands(self) -> dict:
        """Get the controller commands.

        Format:
        {
            "commands": ["command1", "command2"],
            "pwm_values": [0, 0, 0, 0, 0, 0]
        }
        """
        with self._commands_lock:
            commands = self._controller_commands

            self._controller_commands = None
            self._controller_commands_available = False

            return commands

    def set_sensor_data(self, data: dict[str, dict]) -> None:
        """Set the sensor data.

        Format:
        {
            "response": "",
            "sensor1": {"": 0},
            "sensor2": {"": 0},
            "sensor3": {"": 0},
            ...
        }
        """
        with self._sensors_lock:
            self._sensor_data = data
            self._sensor_data_available = True

    def start_listening(self) -> None:
        """Start listening for data from the topside PC."""
        self._listen_for_data()

    def close(self) -> None:
        """Close the socket connection."""
        self._client_socket.shutdown(socket.SHUT_RDWR)
        self._client_socket.close()

    def _receive_data(self) -> dict:
        # Receive data from the socket and decode it.
        command_bytes: bytes = self._client_socket.recv(self._buffer_size)

        data = json.loads(command_bytes.decode())
        print("Data" + str(data))

        return data

    def _listen_for_data(self) -> None:
        """Listen for data from the topside PC on loop and leave the data in a buffer for the main loop to pick up."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

            host: str = "0.0.0.0"

            while True:
                # Wait for a connection.
                server_socket.bind((host, self._port))
                server_socket.listen()
                print(f"Server listening on {host}:{self._port}")

                # Accept the connection.
                client_socket, client_address = server_socket.accept()
                print(f"Accepted connection from {client_address}")

                # Store the client socket.
                self._client_socket = client_socket

                try:
                    while True:
                        # Receive data from the socket.
                        controller_commands: dict = self._receive_data()

                        # Store the commands.
                        with self._commands_lock:
                            self._controller_commands = controller_commands
                            self._controller_commands_available = True

                        # Get sensor data to upload.
                        with self._sensors_lock:
                            self._data_to_send = self._sensor_data

                        # Update the time of sending and delta.
                        delta = time.time_ns() - self._last_send_time
                        self._data_to_send["clock"] = {
                            "time_ns": time.time_ns(),
                            "time_ms": time.time_ns() / 1_000_000,
                            "message_delta_ns": delta,
                            "message_delta_ms": delta / 1_000_000,
                        }
                        self._last_send_time = time.time_ns()

                        # Send the data.
                        print("sending" + str(self._data_to_send))
                        self._send_data(self._data_to_send)
                        print("Sent!")

                except (ConnectionResetError, OSError):
                    print("Inbound connection reset. Reconnecting...")

    def _send_data(self, data: dict) -> None:
        """Encode and send data to the Raspberry Pi.

        Args:
            data (dict):
                The data to send to the Raspberry Pi.
        """
        try:
            # Create and send the packet.
            encoded_data: bytes = json.dumps(data).encode()
            self._client_socket.sendall(encoded_data)

            # Wait for the response.
            response: bytes = self._client_socket.recv(self._buffer_size)
            print(f"Received response: {json.loads(response.decode())}")

        except ConnectionResetError:
            print("Outbound connection reset. Reconnecting...")
