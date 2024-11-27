"""Handle serial communication between pi and arduino."""

import serial
import time
import json


class Arduino:
    def __init__(self, port: str = '/dev/ttyACM0', baud_rate: int = 115200) -> None:
        """Initialize an instance of the class.

        Args:
            port (str, optional):
                The port to connect to the Arduino on.
                Defaults to '/dev/ttyACM0'.
            baud_rate (int, optional):
                The baud rate to use for the serial connection.
                Defaults to 115200.
        """
        self.serial_port = serial.Serial(port, baud_rate)

    def is_open(self) -> bool:
        """Check if the serial connection is open.

        Returns:
            bool: True if the connection is open, False otherwise.
        """
        return self.serial_port.is_open

    def open(self) -> None:
        """Open the serial connection."""
        self.serial_port.open()

    def get_message(self) -> str:
        """Get a message from the Arduino and decodes it.

        Returns:
            str: The message from the Arduino.
        """
        message = self.serial_port.readline()

        if not message.isspace():
            message = message.decode()

        return message

    def send_pwm(self, pwm_values: dict[str, int]) -> None:
        """Send PWM values to the Arduino.

        Args:
            pwm_values (dict[str, int]):
                The PWM values to send to the Arduino.
        """
        msg: str = json.dumps(pwm_values)

        self.serial_port.write(msg.encode())

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
            test_pwm_values: dict[str, int] = {
                "FL": 1600,
                "FR": 1400,
                "BL": 1500,
                "BR": 1700,
                "FLV": 1600,
                "FRV": 1400,
                "BLV": 1500,
                "BRV": 1700,
            }
            ard.send_pwm(test_pwm_values)
    except KeyboardInterrupt:
        pass

    ard.close()




"""
	   GPIO  | pin | pin |  GPIO 	
3V3 	-   	1 	  2 	 - 	     5V
SDA 	2   	3 	  4 	 - 	     5V
SCL 	3   	5 	  6 	 - 	 Ground
	    4   	7 	  8 	 14 	TXD
Ground 	-   	9 	  10 	 15 	RXD
ce1 	17   	11 	  12 	 18 	ce0
	    27   	13 	  14 	 - 	 Ground
	    22   	15 	  16 	 23 	
3V3 	-       17 	  18 	 24 	
MOSI 	10   	19 	  20 	 - 	 Ground
MISO 	9   	21 	  22 	 25 	
SCLK 	11   	23 	  24 	 8 	    CE0
Ground 	-   	25 	  26 	 7 	    CE1
ID_SD 	0   	27 	  28 	 1 	  ID_SC
	    5   	29 	  30 	 - 	 Ground
	    6   	31 	  32 	 12 	
	    13   	33 	  34 	 - 	 Ground
miso 	19   	35 	  36 	 16 	ce2
	    26   	37 	  38 	 20    mosi
Ground 	-   	39 	  40 	 21    sclk
"""