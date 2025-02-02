from enum import Enum

import pigpio


# TODO: Break this up into separate files.
class GPIOHandler:
    """Class for handling GPIO devices.

    Properties:
        GPIO (pigpio.pi): The pigpio instance used by the GPIOHandler.
        devices (dict[str, GPIODevice]): The devices in the GPIOHandler.

    Methods:
        new_device(device: GPIODevice): Add a new device to the GPIOHandler.
        remove_device(device: GPIODevice): Remove a device from the GPIOHandler.
        get_device(name: str): Get a device from the GPIOHandler.
        cleanup(): Clean up the GPIOHandler, turning off all pins and stopping the GPIO instance.
    """
    def __init__(self, gpio: pigpio.pi = pigpio.pi()) -> None:
        """Class for handling GPIO devices.

        Args:
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Defaults to a new instance of pigpio.pi().
        """
        self.GPIO = gpio

        self.devices: dict[str, 'Pin'] = {}

    def new_device(self, device: 'Pin') -> None:
        """Add a new device to the GPIOHandler. Any device added needs to have a unique name, else it will overwrite an
        existing device.

        Args:
            device (Pin):
                The device to add.
        """
        self.devices[device.name] = device
        self.devices[device.name].setup(self.GPIO)

    def remove_device(self, device: 'Pin') -> None:
        """Remove a device from the GPIOHandler.

        Args:
            device (Pin):
                The device to remove.
        """
        self.devices.pop(device.name)

    def update_devices(self) -> None:
        """Update the devices. TODO: Implement."""
        for device in self.devices.values():
            device.update()

    def read_devices(self) -> dict[str, int]:
        """Read the devices.

        Returns:
            dict[str, int]: The values of the devices.
        """
        return_dict = {}
        for device in self.devices.values():
            device_val = device.read()
            if device_val is not None:
                return_dict[device.name] = device_val

        return return_dict

    def cleanup(self) -> None:
        """Clean up the GPIOHandler, turning off all pins and stopping the GPIO instance."""
        for device in self.devices.values():
            device.off()

        self.GPIO.stop()


class PinMode(Enum):
    WriteDigital = "Steady"
    PWMMicroseconds = "PWMus"
    PWMPercent = "PWM%"
    # Flicker = "Flicker"
    ReadDigital = "ReadDigital"
    ReadAnalog = "ReadAnalog"


class Pin:

    def __init__(self, name: str, pin_number: int | None = None, mode: PinMode | None = None, duty_cycle: int = 0,
                 frequency: int = 50, gpio: pigpio.pi = None) -> None:
        """Initialize the Pin.

        Args:
            name (str):
                The name of the device.
            pin_number (int, optional):
                The pin the device is connected to.
                Defaults to None.
            mode (PinMode, optional):
                The mode of the device.
                Defaults to None.
            duty_cycle (int, optional):
                The duty cycle of the device.
                Defaults to 0.
            frequency (int, optional):
                The frequency of the device.
                Defaults to 50.
            gpio (pigpio.pi, optional):
                The pigpio instance to use.
                Defaults to None.
        """
        self._name: str = name
        self._pin_number: int = pin_number
        self._mode: PinMode = mode
        self._duty_cycle: int = duty_cycle
        self._frequency: int = frequency
        self._gpio: pigpio.pi = gpio

    def setup(self, gpio: pigpio.pi) -> None:
        """Set up the pin."""
        self._gpio = gpio
        self._refresh()

    def update(self) -> None:
        """Update the pin. TODO: Implement."""
        # self._refresh()
        pass

    def read(self) -> int | None:
        """Read the pin.

        Returns:
            int: The value of the pin.
        """
        if self._gpio is None or self._pin_number is None:
            return None

        # TODO: Implement ReadAnalog vs digital
        if self._mode == PinMode.ReadDigital:
            return int(self._gpio.read(self._pin_number))
        elif self._mode == PinMode.ReadAnalog:
            return self._gpio.read(self._pin_number)

        return None

    def _refresh(self) -> None:
        """Refresh the pin."""
        # print(self._name, self._pin_number, self._mode, self._duty_cycle, self._frequency)
        if self._gpio is None or self._pin_number is None:
            print("GPIO or pin number not set")
            return

        # print(PinMode.PWMMicroseconds, self._mode)
        try:
            if self._mode == PinMode.WriteDigital.value:
                self._gpio.set_mode(int(self._pin_number), pigpio.OUTPUT)
                self._gpio.write(int(self._pin_number), int(self._duty_cycle))
            elif self._mode == PinMode.PWMMicroseconds.value:
                # self._gpio.set_mode(int(self._pin_number), pigpio.OUTPUT)
                # self._gpio.hardware_PWM(int(self._pin_number), self._frequency, int(self._duty_cycle) * 10000)
                print(self._gpio, int(self._pin_number), int(self._duty_cycle))
                self._gpio.set_servo_pulsewidth(int(self._pin_number), int(self._duty_cycle))
            # TODO: Implement PWMPercent
            elif self._mode == PinMode.PWMPercent.value:
                self._gpio.set_mode(int(self._pin_number), pigpio.OUTPUT)
                self._gpio.hardware_PWM(int(self._pin_number), int(self._frequency), int(self._duty_cycle) * 10000)
            elif self._mode == PinMode.ReadDigital.value:
                self._gpio.set_mode(int(self._pin_number), pigpio.INPUT)
            elif self._mode == PinMode.ReadAnalog.value:
                self._gpio.set_mode(int(self._pin_number), pigpio.INPUT)
                # gpio.set_pull_up_down(self._pin_number, pigpio.PUD_OFF)
        except pigpio.error as e:
            print(
                "There was an error in setting a pin value with the following details:\n\n",
                f"Name: {self._name}\n",
                f"Pin Number: {self._pin_number}\n",
                f"Mode: {self._mode}\n",
                f"Duty Cycle: {self._duty_cycle}\n",
                f"Frequency: {self._frequency}\n",
                f"Error: {e}\n\n",
                )

    @property
    def name(self) -> str:
        """Return the name of the device.

        Returns:
            str: The name of the device.
        """
        return self._name

    @property
    def pin_number(self) -> int:
        """Return the pin number.

        Returns:
            int: The pin number.
        """
        return self._pin_number

    @pin_number.setter
    def pin_number(self, new_pin_number: int) -> None:
        """Set the pin number.

        Args:
            new_pin_number (int):
                The new pin number.
        """
        if new_pin_number != self._pin_number:
            self._pin_number = new_pin_number
            self._refresh()

    @property
    def mode(self) -> PinMode:
        """Return the mode of the device.

        Returns:
            PinMode: The mode of the device.
        """
        return self._mode

    @mode.setter
    def mode(self, new_mode: PinMode) -> None:
        """Set the mode of the device.

        Args:
            new_mode (PinMode):
                The new mode of the device.
        """
        if new_mode != self._mode:
            self._mode = new_mode
            self._refresh()

    @property
    def duty_cycle(self) -> int:
        """Return the duty cycle of the device.

        Returns:
            int: The duty cycle of the device.
        """
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, new_duty_cycle: int) -> None:
        """Set the duty cycle of the device.

        Args:
            new_duty_cycle (int):
                The new duty cycle of the device.
        """
        if new_duty_cycle != self._duty_cycle:
            self._duty_cycle = new_duty_cycle
            self._refresh()

    @property
    def frequency(self) -> int:
        """Return the frequency of the device.

        Returns:
            int: The frequency of the device.
        """
        return self._frequency

    @frequency.setter
    def frequency(self, new_frequency: int) -> None:
        """Set the frequency of the device.

        Args:
            new_frequency (int):
                The new frequency of the device.
        """
        if new_frequency != self._frequency:
            self._frequency = new_frequency
            self._refresh()

    def on(self) -> None:
        """Turn the device on."""
        self._duty_cycle = 1
        self._refresh()

    def off(self) -> None:
        """Turn the device off."""
        self._duty_cycle = 0
        self._refresh()

    def toggle(self) -> None:
        """Toggle the device."""
        self._duty_cycle = 1 - self._duty_cycle
        self._refresh()

    def cleanup(self) -> None:
        """Clean up the device."""
        self.off()
