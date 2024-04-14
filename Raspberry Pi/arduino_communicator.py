"""Handle serial communication between pi and arduino."""

import serial
import time

MAX_4BYTE_INT = 2 ** (4 * 8) - 1


def int_to_bytes(byte_array: int) -> bytes:
    """Convert an integer to a 4-byte byte array.

    Args:
        byte_array (int):
            The integer to convert.

    Returns:
        bytes: The byte array.
    """
    byte_array: int = int(byte_array)

    if byte_array < 0:
        byte_array = 0
    if byte_array > MAX_4BYTE_INT:
        byte_array = MAX_4BYTE_INT

    byte_list: list = []

    for _ in range(4):
        byte_list.append(byte_array & 0xff)
        byte_array >>= 8

    return bytes(byte_list)


def bytes_to_int(byte_array: bytes) -> int:
    """Convert a 4-byte byte array to an integer.

    Args:
        byte_array (bytes):
            The byte array to convert.

    Returns:
        int: The integer.
    """
    item: bytes | int = byte_array[0]
    offset: int = 8

    for character in byte_array[1:]:
        character <<= offset
        item += character
        offset += 8

    return item


def nums_to_bytes(numbers: tuple[int, int, int, int, int, int]) -> bytes:
    """Convert a tuple of integers to a byte array.

    Args:
        numbers (tuple[int, int, int, int, int, int]):
            The tuple of integers to convert.

    Returns:
        bytes: The byte array.
    """
    byte_array: bytes = b""

    for n in numbers:
        byte_array += int_to_bytes(n)

    return byte_array


class Arduino:
    def __init__(self, port: str = '/dev/ttyACM0', baud_rate: int = 115200) -> None:
        self.serial_port = serial.Serial(port, baud_rate)

    def is_open(self) -> bool:
        """Check if the serial connection is open.

        Returns:
            bool: True if the connection is open, False otherwise.
        """
        return self.serial_port.isOpen()

    def open(self) -> None:
        """Open the serial connection."""
        self.serial_port.open()

    def get_message(self) -> str:
        """Get a message from the Arduino and decodes it.

        Returns:
            str: The message from the Arduino.
        """
        message: bytes | str = self.serial_port.readline()

        # if not message.isspace():
        message = message.decode()

        return message

    def send_pwm(self, pwm_values: tuple[int, int, int, int, int, int]) -> None:
        """Send PWM values to the Arduino.

        Args:
            pwm_values (tuple[int, int, int, int, int, int]):
                The PWM values to send to the Arduino.
        """
        msg: bytes = nums_to_bytes(pwm_values)

        self.serial_port.write(msg)

    def close(self):
        """Close the serial connection."""
        self.serial_port.close()

    def setup(self):
        """Set up the Arduino for communication.

        This method should be called before any other communication with the Arduino and takes approximately 5 seconds
        to complete.
        """
        if not self.is_open():
            self.open()

        # The Arduino is reset after enabling the serial connection, therefore we have to wait some seconds
        time.sleep(5)


if __name__ == "__main__":
    ard = Arduino()

    # if (ard.isOpen() == False):
    #     ard.open()
    #
    # time.sleep(5)  # the Arduino is reset after enabling the serial connection, therefore we have to wait some seconds

    ard.setup()

    try:
        while 1:
            response: str = ard.get_message()
            pwm_values: tuple[int, int, int, int, int, int] = (1600, 1700, 1700, 1700, 1700, 1700)
            ard.send_pwm(pwm_values)
    except KeyboardInterrupt:
        pass

    ard.close()
