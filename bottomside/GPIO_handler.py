import copy
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
        get_devices(): Get all devices in the GPIOHandler.
        cleanup(): Clean up the GPIOHandler, turning off all pins and stopping the GPIO instance.
    """
    def __init__(self, gpio: pigpio.pi = pigpio.pi()) -> None:
        """Class for handling GPIO devices.

        Args:
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Defaults to a new instance of pigpio.pi().
        """
        self.GPIO = gpio

        self.devices = {}

    def new_device(self, device: 'GPIODevice'):
        """Add a new device to the GPIOHandler. Any device added needs to have a unique name, else it will overwrite an
        existing device.

        Args:
            device (GPIODevice):
                The device to add.
        """
        self.devices[device.name] = device
        self.devices[device.name].setup(self.GPIO)

    def remove_device(self, device: 'GPIODevice'):
        """Remove a device from the GPIOHandler.

        Args:
            device (GPIODevice):
                The device to remove.
        """
        self.devices.pop(device.name)

    def get_device(self, name: str) -> 'GPIODevice':
        """Get a device from the GPIOHandler.

        Args:
            name (str):
                The name of the device to get.

        Returns:
            GPIODevice: The device with the specified name.
        """
        return self.devices[name]

    def get_devices(self) -> dict[str, 'GPIODevice']:
        """Get all devices in the GPIOHandler.

        Returns:
            dict[str, GPIODevice]: All devices in the GPIOHandler.
        """
        return self.devices

    def cleanup(self):
        """Clean up the GPIOHandler, turning off all pins and stopping the GPIO instance."""
        for device in self.devices.values():
            device.off()

        self.GPIO.stop()


class PinDirs(Enum):
    """Enum for pin directions. IN for input/reading, OUT for output/writing.

    Properties:
        IN (int): The input direction.
        OUT (int): The output direction.
    """
    IN = 0
    OUT = 1


class Colors(Enum):
    """Enum for common colors.

    Properties:
        RED (tuple[int, int, int]): The color red.
        GREEN (tuple[int, int, int]): The color green.
        BLUE (tuple[int, int, int]): The color blue.
        YELLOW (tuple[int, int, int]): The color yellow.
        CYAN (tuple[int, int, int]): The color cyan.
        MAGENTA (tuple[int, int, int]): The color magenta.
        WHITE (tuple[int, int, int]): The color white.
        BLACK (tuple[int, int, int]): The color black.
    """
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    WHITE = (150, 200, 255)
    BLACK = (0, 0, 0)

    def __str__(self):
        return self.name.lower() + str(self.value)

    def __repr__(self):
        return self.name.lower()

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, item):
        return self.value[item]

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class GPIODevice:
    """Class for a GPIO device.

    Properties:
        name (str): The name of the GPIO device.
    """
    def __init__(self, name: str, gpio: pigpio.pi = None) -> None:
        """Class for a GPIO device.

        Args:
            name (str):
                The name of the GPIO device.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Only needed for devices that are not to be used with a GPIOHandler.
                Defaults to None.
        """
        self._name = name
        self.GPIO = gpio

    @property
    def name(self):
        return self._name

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name


class Pin(GPIODevice):
    """Class for a GPIO pin.

    Properties:
        pin (int): The pin number.
        direction (PinDirs): The direction of the pin.

    Methods:
        setup(gpio: pigpio.pi): Set up the pin.
    """
    def __init__(self, name: str, pin: int, gpio: pigpio.pi = None, direction: PinDirs = PinDirs.OUT) -> None:
        """Class for a GPIO pin.

        Args:
            name (str):
                The name of the pin.
            pin (int):
                The pin number.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Only needed for devices that are not to be used with a GPIOHandler.
                Defaults to None.
            direction (PinDirs, optional):
                The direction of the pin. IN for input/reading, OUT for output/writing.
                Defaults to PinDirs.OUT.
        """
        super().__init__(name, gpio)
        self._pin = pin
        self._direction = direction

    def setup(self, gpio: pigpio.pi) -> None:
        try:
            self.GPIO.set_mode(self._pin, self._direction.value)
        except pigpio.error:
            print(f"Error setting up pin {self._pin}! Was the socket connection unsuccessful?")
            self.GPIO = pigpio.pi()
            self.GPIO.set_mode(self._pin, self._direction.value)

        self.GPIO = gpio

    @property
    def pin(self):
        return self._pin

    @property
    def direction(self):
        return self._direction


class LED(Pin):
    """Class for controlling an LED.

    Properties:
        value (bool): The state of the LED.

    Methods:
        on(): Turn the LED on.
        off(): Turn the LED off.
        toggle(): Toggle the LED's state on or off.
        get(): Get the LED's state.
        set(value: bool): Set the LED's state.
    """
    def __init__(self, pin: int, name: str, gpio: pigpio.pi = pigpio.pi()) -> None:
        """Class for controlling an LED.
        
        Args:
            pin (int):
                The pin the LED is connected to.
            name (str):
                The name of the LED.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Defaults to a new instance of pigpio.pi().
        """
        super().__init__(name, pin, gpio, PinDirs.OUT)

        self._value: bool = False

    def on(self) -> None:
        """Turn the LED on."""
        self._value = True
        self.GPIO.write(self._pin, self._value)

    def off(self) -> None:
        """Turn the LED off."""
        self._value = False
        self.GPIO.write(self._pin, self._value)

    def toggle(self) -> bool:
        """Toggle the LED's state on or off.

        Returns:
            bool: The new state of the LED.
        """
        self._value = not self._value
        self.GPIO.write(self._pin, not self.GPIO.read(self._pin))

        return self._value

    def get(self) -> bool:
        """Get the LED's state.

        Returns:
            bool: The state of the LED.
        """
        return self._value

    def set(self, value: bool) -> None:
        """Set the LED's state.

        Args:
            value (bool):
                The state to set the LED to.
        """
        self._value = value
        self.GPIO.write(self._pin, value)


class Button(Pin):
    """Class for a button.

    Properties:
        value (int): The state of the button.

    Methods:
        get(): Get the button's state.
        wait_for_press(): Wait for the button to be pressed.
        wait_for_release(): Wait for the button to be released.
        wait_for_change(): Wait for the button to change state.
    """
    def __init__(self, pin: int, name: str, gpio: pigpio.pi = None) -> None:
        """Class for a button.

        Args:
            pin (int):
                The pin the button is connected to.
            name (str):
                The name of the button.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Only needed for devices that are not to be used with a GPIOHandler.
                Defaults to None.
        """
        super().__init__(name, pin, gpio, PinDirs.IN)

        self._value: int = 0

    def get(self) -> int:
        """Get the button's state.

        Returns:
            int: The state of the button.
        """
        return self.GPIO.read(self._pin)

    def wait_for_press(self) -> None:
        """Wait for the button to be pressed."""
        self.GPIO.wait_for_edge(self._pin, pigpio.RISING_EDGE)

    def wait_for_release(self) -> None:
        """Wait for the button to be released."""
        self.GPIO.wait_for_edge(self._pin, pigpio.FALLING_EDGE)

    def wait_for_change(self) -> None:
        """Wait for the button to change state."""
        self.GPIO.wait_for_edge(self._pin, pigpio.EITHER_EDGE)


class PWMLED(Pin):
    """Class for controlling a PWM LED.

    Properties:
        value (int): The PWM value of the LED.

    Methods:
        resume(): Resume the PWM signal of the LED. The LED will resume with the last set PWM value if it was paused.
        pause(): Pause the PWM signal of the LED. The LED will hold the last set PWM value until resumed.
        off(): Turn the PWM signal off.
        set(value: int): Set the PWM duty cycle value of the LED.
        get(): Get the PWM value of the
    """

    def __init__(self, pin: int, name: str, gpio: pigpio.pi = None) -> None:
        """Class for controlling a PWM LED.

        Args:
            pin (int):
                The pin the LED is connected to.
            name (str):
                The name of the LED.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Only needed for devices that are not to be used with a GPIOHandler.
                Defaults to None.
        """
        super().__init__(name, pin, gpio, PinDirs.OUT)

        self._value: int = 0

    def resume(self) -> None:
        """Resume the PWM signal of the LED. The LED will resume with the last set PWM value if it was paused."""
        self.GPIO.set_PWM_dutycycle(self._pin, self._value)

    def pause(self) -> None:
        """Pause the PWM signal of the LED. The LED will hold the last set PWM value until resumed."""
        self.GPIO.set_PWM_dutycycle(self._pin, 0)

    def off(self) -> None:
        """Turn the PWM signal off."""
        self.GPIO.set_PWM_dutycycle(self._pin, 0)
        self._value = 0

    def set(self, value: int) -> None:
        """Set the PWM duty cycle value of the LED.

        Args:
            value (int):
                The duty cycle value to set. Between 0 and 255.
        """
        self._value = value
        self.GPIO.set_PWM_dutycycle(self._pin, value)

    def get(self) -> int:
        """Get the PWM value of the LED.

        Returns:
            int: The PWM value of the LED. Between 0 and 255.
        """
        return self._value


class RGBLED(GPIODevice):
    """Class for controlling an RGB LED.

    Properties:
        red (int): The red value of the RGB LED.
        green (int): The green value of the RGB LED.
        blue (int): The blue value of the RGB LED.

    Methods:
        set_color(color: tuple[int, int, int] | Colors): Set the color of the RGB LED.
        get_color(): Get the color of the RGB LED.
        off(): Turn the RGB LED off.
        pause(): Pause the RGB LED. The LED will hold the last set color until resumed.
        resume(): Resume the RGB LED. The LED will resume with the last set color if it was paused.
    """
    def __init__(self, name: str, red_pin: int, green_pin: int, blue_pin: int, gpio: pigpio.pi = None) -> None:
        """Class for controlling an RGB LED.

        Args:
            red_pin (int):
                The pin the red LED is connected to.
            green_pin (int):
                The pin the green LED is connected to.
            blue_pin (int):
                The pin the blue LED is connected to.
            name (str):
                The name of the RGB LED.
        """
        super().__init__(name, gpio)
        
        self._red_led = PWMLED(red_pin, f"{name}_red")
        self._green_led = PWMLED(green_pin, f"{name}_green")
        self._blue_led = PWMLED(blue_pin, f"{name}_blue")

        self._color = (0, 0, 0)

    def set_color(self, color: tuple[int, int, int] | Colors) -> None:
        """Set the color of the RGB LED.

        Args:
            color (tuple[int, int, int] | Colors):
                The color to set the RGB LED to. Each value in the tuple should be between 0 and 255.
        """
        self._red_led.set(color[0])
        self._green_led.set(color[1])
        self._blue_led.set(color[2])

        self._color = copy.deepcopy(color)

    def get_color(self) -> tuple[int, int, int]:
        """Get the color of the RGB LED.

        Returns:
            tuple[int, int, int]: The color of the RGB LED.
        """
        return self._color

    def off(self) -> None:
        """Turn the RGB LED off."""
        self.set_color((0, 0, 0))

    def pause(self) -> None:
        """Pause the RGB LED. The LED will hold the last set color until resumed."""
        self._red_led.pause()
        self._green_led.pause()
        self._blue_led.pause()

    def resume(self) -> None:
        """Resume the RGB LED. The LED will resume with the last set color if it was paused."""
        self._red_led.resume()
        self._green_led.resume()
        self._blue_led.resume()

    def setup(self, gpio: pigpio.pi) -> None:
        """Set up the RGB LED.

        Args:
            gpio (pigpio.pi):
                The pigpio instance to use.
        """
        self.GPIO = gpio

        self._red_led.setup(self.GPIO)
        self._green_led.setup(self.GPIO)
        self._blue_led.setup(self.GPIO)

    @property
    def red(self):
        return self._red_led.get()

    @property
    def green(self):
        return self._green_led.get()

    @property
    def blue(self):
        return self._blue_led.get()

    @red.setter
    def red(self, value: int):
        self._red_led.set(value)

    @green.setter
    def green(self, value: int):
        self._green_led.set(value)

    @blue.setter
    def blue(self, value: int):
        self._blue_led.set(value)


class Servo(Pin):
    """Class for controlling a servo.

    Properties:
        safe_pulsewidth (int): The safe pulse width for the servo.
        pulsewidth_range (tuple[int, int]): The range of pulse widths the servo can accept.
        angle_range (tuple[int, int]): The range of angles the servo can rotate to.

    Methods:
        set_pulsewidth(value: int): Set the pulse width sent to the servo.
        get_pulsewidth(): Get the pulse width sent to the servo.
        off(): Turn the PWM signal off.
        pause(): Pause the servo. The servo will hold the last set pulse width until resumed.
        resume(): Resume the servo. The servo will resume with the last set pulse width if it was paused.
        set_angle(angle: int): Set the angle of the servo.
        get_angle(): Get the angle of the servo.
        set_safe(): Set the servo to the safe pulse width.
    """

    def __init__(self, pin: int, name: str, gpio: pigpio.pi = None, safe_pulsewidth: int = 1500,
                 pulsewidth_range: tuple[int, int] = (1100, 1900), angle_range: tuple[int, int] = (0, 180)) -> None:
        """Class for controlling a servo.

        Args:
            pin (int):
                The pin the servo is connected to.
            name (str):
                The name of the servo.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Only needed for devices that are not to be used with a GPIOHandler.
                Defaults to None.
            safe_pulsewidth (int, optional):
                The safe pulse width for the servo.
                Defaults to 1500.
            pulsewidth_range (tuple[int, int], optional):
                The range of pulse widths the servo can accept.
                Defaults to (1100, 1900).
            angle_range (tuple[int, int], optional):
                The range of angles the servo can rotate to.
                Defaults to (0, 180).
        """
        super().__init__(name, pin, gpio, PinDirs.OUT)

        self._safe_pulsewidth = safe_pulsewidth
        self._pulsewidth_range = pulsewidth_range
        self._angle_range = angle_range

        self._value: int = 0

    def set_pulsewidth(self, value: int) -> None:
        """Set the pulse width sent to the servo.

        Args:
            value (int): The pulse width to set. Generally between 500 and 2500. 0 is off.
        """
        self._value = value
        self.GPIO.set_servo_pulsewidth(self._pin, value)

    def get_pulsewidth(self) -> int:
        """Get the pulse width sent to the servo.

        Returns:
            int: The pulse width sent to the servo.
        """
        return self._value

    def off(self) -> None:
        """Turn the PWM signal off."""
        self.set_pulsewidth(0)
        self._value = 0

    def pause(self) -> None:
        """Pause the servo. The servo will hold the last set pulse width until resumed."""
        self.GPIO.set_servo_pulsewidth(self._pin, 0)

    def resume(self) -> None:
        """Resume the servo. The servo will resume with the last set pulse width if it was paused."""
        self.GPIO.set_servo_pulsewidth(self._pin, self._value)

    def set_angle(self, angle: int) -> None:
        """Set the angle of the servo.

        Args:
            angle (int): The angle to set the servo to. Between 0 and 180.
        """
        pulsewidth = _angle_to_pulsewidth(angle, self._angle_range, self._pulsewidth_range)
        self.set_pulsewidth(pulsewidth)

    def get_angle(self) -> int:
        """Get the angle of the servo.

        Returns:
            int: The angle of the servo.
        """
        return _pulsewidth_to_angle(self._value, self._angle_range, self._pulsewidth_range)

    def set_safe(self) -> None:
        """Set the servo to the safe pulse width."""
        self.set_pulsewidth(self._safe_pulsewidth)

    @property
    def safe_pulsewidth(self):
        return self._safe_pulsewidth

    @property
    def pulsewidth_range(self):
        return self._pulsewidth_range

    @property
    def angle_range(self):
        return self._angle_range

    @safe_pulsewidth.setter
    def safe_pulsewidth(self, value: int):
        self._safe_pulsewidth = value

    @pulsewidth_range.setter
    def pulsewidth_range(self, value: tuple[int, int]):
        self._pulsewidth_range = value

    @angle_range.setter
    def angle_range(self, value: tuple[int, int]):
        self._angle_range = value


def _angle_to_pulsewidth(angle: int, angle_range: tuple[int, int], pulsewidth_range: tuple[int, int]) -> int:
    """Convert an angle to a pulse width.

    Args:
        angle (int):
            The angle to convert.
        angle_range (tuple[int, int]):
            The range of angles the servo can rotate to.
        pulsewidth_range (tuple[int, int]):
            The range of pulse widths the servo can accept.

    Returns:
        int: The pulse width for the angle.
    """
    angle_normalized = float(angle - angle_range[0]) / (angle_range[1] - angle_range[0])
    pulsewidth_range_diff = pulsewidth_range[1] - pulsewidth_range[0]
    val = int(pulsewidth_range[0] + (angle_normalized * pulsewidth_range_diff))

    return val


def _pulsewidth_to_angle(pulsewidth: int, angle_range: tuple[int, int], pulsewidth_range: tuple[int, int]) -> int:
    """Convert a pulse width to an angle.

    Args:
        pulsewidth (int):
            The pulse width to convert.
        angle_range (tuple[int, int]):
            The range of angles the servo can rotate to.
        pulsewidth_range (tuple[int, int]):
            The range of pulse widths the servo can accept.

    Returns:
        int: The angle for the pulse width.
    """
    pulsewidth_normalized = float(pulsewidth - pulsewidth_range[0]) / (pulsewidth_range[1] - pulsewidth_range[0])
    angle_range_diff = angle_range[1] - angle_range[0]
    val = int(angle_range[0] + (pulsewidth_normalized * angle_range_diff))

    return val


class Relay(Pin):
    """Class for controlling a relay.

    Properties:
        value (bool): The state of the relay.

    Methods:
        on(): Turn the relay on.
        off(): Turn the relay off.
        toggle(): Toggle the relay's state on or off.
        get(): Get the relay's state.
        set(value: bool): Set the relay's state.
    """

    def __init__(self, pin: int, name: str, gpio: pigpio.pi = None) -> None:
        """Class for a relay.

        Args:
            pin (int):
                The pin the relay is connected to.
            name (str):
                The name of the relay.
            gpio (pigpio.pi, optional):
                The pigpio instance to use. Only needed for devices that are not to be used with a GPIOHandler.
                Defaults to None.
        """
        super().__init__(name, pin, gpio, PinDirs.OUT)

        self._value: bool = False

    def on(self) -> None:
        """Turn the relay on."""
        self._value = True
        self.GPIO.write(self._pin, self._value)

    def off(self) -> None:
        """Turn the relay off."""
        self._value = False
        self.GPIO.write(self._pin, self._value)

    def toggle(self) -> bool:
        """Toggle the relay's state on or off.

        Returns:
            bool: The new state of the relay.
        """
        self._value = not self._value
        self.GPIO.write(self._pin, not self.GPIO.read(self._pin))

        return self._value

    def get(self) -> bool:
        """Get the relay's state.

        Returns:
            bool: The state of the relay.
        """
        return self._value

    def set(self, value: bool) -> None:
        """Set the relay's state.

        Args:
            value (bool):
                The state to set the relay to.
        """
        self._value = value
        self.GPIO.write(self._pin, value)


if __name__ == "__main__":
    gpio_handler = GPIOHandler()

    led = LED(17, "led")
    button = Button(18, "button")
    pwm_led = PWMLED(27, "pwm_led")
    rgb_led = RGBLED("rgb_led", 22, 23, 24)
    servo = Servo(25, "servo")

    gpio_handler.new_device(led)
    gpio_handler.new_device(button)
    gpio_handler.new_device(pwm_led)
    gpio_handler.new_device(rgb_led)
    gpio_handler.new_device(servo)

    for dev in gpio_handler.devices.values():
        dev.setup(gpio_handler.GPIO)

    led.on()
    button.wait_for_press()
    pwm_led.set(128)
    rgb_led.set_color(Colors.RED)
    servo.set_angle(90)

    led.off()
    button.wait_for_release()
    pwm_led.pause()
    rgb_led.off()
    servo.off()

    gpio_handler.GPIO.stop()
