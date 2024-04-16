import threading
import time

import socket_handler
import arduino_communicator
import flight_controller_communicator


class PiLoop:
    """Main system class for the Raspberry Pi."""
    def __init__(self):
        self.socket_handler = socket_handler.SocketHandler()
        self.arduino = arduino_communicator.Arduino()
        self.FC = flight_controller_communicator.FC("/dev/ttyUSB0")  # Change this to the correct port.

        # Initialize the data dictionaries.
        self.sensor_data = {}

        self.controller_data: dict | None = None

        # Boot up the Arduino and start the socket handler.
        self.arduino.setup()
        threading.Thread(target=self.socket_handler.start_listening).start()

    def loop(self):
        """Main loop for the Raspberry Pi."""
        # Get controller inputs.
        self.controller_data = self.socket_handler.get_controller_commands()

        # Only continue if there is controller data.
        if self.controller_data:
            print("Controller data" + str(self.controller_data))

            # Handle the controller data.
            self.handle_controller_data(self.controller_data)

        else:
            print("No controller data")

        # Get sensor data.
        self.get_sensor_data()

        # Hand the data over to the socket handler.
        self.socket_handler.set_sensor_data(self.sensor_data)

    def get_sensor_data(self):
        """Get the sensor data from the flight controller."""
        self.sensor_data = self.FC.get_sensor_data()

    def handle_controller_data(self, data: dict) -> str:
        """Handle the controller data.

        Args:
            data (dict):
                The controller data to handle.
        """
        self.arduino.send_pwm(data["pwm_values"])
        self.FC.set_pwm(data["pwm_values"])

        command_dict = {
            "quit": self.quit,
        }

        return self.arduino.get_message()

    def quit(self):
        """Quit the program."""
        self.arduino.close()
        self.socket_handler.close()
        exit(0)


if __name__ == "__main__":
    pi_loop = PiLoop()
    # socket_handler.start_listening()
    while True:
        pi_loop.loop()
