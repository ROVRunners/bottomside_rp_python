import json
import time

from GPIO_handler import GPIOHandler as GPIO, Pin
from i2c import I2CHandler as I2C, I2CObject
from mqtt_connection import MQTTConnection as MQTT
from mavlink import Mavlink as MAV

from ROV_config import ROV


class MainSystem:
    def __init__(self, platform: str) -> None:
        """Initialize an instance of the class.

        Args:
            platform (str):
                The platform that the ROV is running on. This is usually either 'Windows' or 'Linux'. Used to determine
                whether to use the GPIO pins or not for debugging purposes.
        """
        self.platform = platform

        # Variable to control whether the main loop of the ROV continues running.
        self.run = True
        self.status = "running"

        # Set the number of loops per second and the number of nanoseconds per loop for rate limiting.
        self._loops_per_second = 60
        self._nanoseconds_per_loop = 1_000_000_000 // self._loops_per_second

        # Initialize the System Objects object.
        self._ROV = ROV()
        self._GPIO = GPIO()
        self._I2C = I2C()
        self._MAV = MAV()
        self._MQTT = MQTT(
            ip=self._ROV.ip,
            port=self._ROV.comms_port,
            client_id=self._ROV.rov_name
        )

        self._MQTT.connect()

    def loop(self):
        start_loop: int = time.monotonic_ns()

        # Get the subscriptions from the MQTT connection.
        sub_dict_updates = self._MQTT.get_new_subscription_dict()

        for key, value in sub_dict_updates.items():
            sender = key.split("/")[0]
            general_category = key.split("/")[1]
            specific_category = key.split("/")[2]

            # If the sender is not the PC, ignore the message.
            if sender != "PC":
                continue

            match general_category:

                # If the general category is "commands", process the command.
                case "commands":
                    match specific_category:
                        case "shutdown":
                            self.shutdown()
                            break
                        # TODO: Add a proper restart command.
                        case "restart":
                            self.shutdown()
                            self.__init__(self.platform)
                            break
                        # TODO: Expand the stop command to block all input except for "command" category messages.
                        case "stop":
                            self.status = "stopped"
                            for device in self._GPIO.devices.values():
                                device.duty_cycle = 0
                            break
                        case _:
                            break
                # If the key is pins, update the relevant GPIO pin.
                case "pins":
                    if not self.status == "stopped":
                        pin_name = specific_category  # id, mode, val, freq
                        # Check if the pin is already in the GPIO devices dictionary.
                        # If it is, update the relevant value.
                        if pin_name in self._GPIO.devices.keys():
                            match key.split("/")[3]:
                                case "id":
                                    self._GPIO.devices[pin_name].pin_number = value
                                case "mode":
                                    self._GPIO.devices[pin_name].mode = value
                                case "val":
                                    self._GPIO.devices[pin_name].duty_cycle = value
                                case "freq":
                                    self._GPIO.devices[pin_name].frequency = value
                        # If the pin is not in the GPIO devices dictionary, create a new pin and add it to the
                        # dictionary with the given value.
                        else:
                            new_pin = Pin(pin_name)

                            self._GPIO.new_device(new_pin)

                            # Depending on what value arrived first, add that value upon creation.
                            match key.split("/")[-1]:
                                case "id":
                                    new_pin.pin_number = int(value)
                                case "mode":
                                    new_pin.mode = value
                                case "val":
                                    new_pin.duty_cycle = int(value)
                                case "freq":
                                    new_pin.frequency = int(value)

                # If the key is an I2C object, update the relevant I2C object.
                case "i2c":
                    if not self.status == "stopped":
                        obj_name = specific_category
                        # Check if the object is already in the I2C objects dictionary.
                        # If it is, update the relevant value.
                        if obj_name in self._I2C.objects.keys():
                            match key.split("/")[-1]:
                                case "addr":
                                    self._I2C.objects[obj_name].address = int(value)
                                case "send_vals":
                                    self._I2C.objects[obj_name].write_registers = json.loads(value)
                                case "read_regs":
                                    self._I2C.objects[obj_name].read_registers = json.loads(value)
                                case "poll_vals":
                                    self._I2C.objects[obj_name].poll_registers = json.loads(value)

                        # If the object is not in the I2C objects dictionary, create a new object and add it to the
                        # dictionary with the given value.
                        else:
                            new_obj = I2CObject(obj_name)
                            print(obj_name)

                            match key.split("/")[-1]:
                                case "addr":
                                    new_obj.address = int(value)
                                case "send_vals":
                                    new_obj.write_registers = json.loads(value)
                                case "read_regs":
                                    new_obj.read_registers = json.loads(value)
                                case "poll_vals":
                                    new_obj.poll_registers = json.loads(value)

                            self._I2C.add_object(new_obj)
                case "mavlink":
                    if not self.status == "stopped":
                        match specific_category:
                            case "req_id":
                                self._MAV.request_data(value)
                            case "send_msg":
                                self._MAV.send_command(*json.loads(value))
                            case _:
                                break

        # Get the data from the sensors.
        gpio_data = self._GPIO.read_devices()
        i2c_data = self._I2C.read_objects()

        # Publish the data to the MQTT connection.
        self._MQTT.send_data(gpio_data, i2c_data, self.status)

        # Rate limit the loop to the specified number of loops per second.
        end_loop: int = time.monotonic_ns()
        loop_time: int = end_loop - start_loop
        sleep_time: float = (self._nanoseconds_per_loop - loop_time) / 1_000_000_000
        if sleep_time > 0:
            time.sleep(sleep_time)

    def shutdown(self):
        """Shut down the ROV gracefully."""
        self.run = False
        self._MQTT.disconnect()
