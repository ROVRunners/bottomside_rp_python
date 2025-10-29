import ms5837
from custom_sensors.generic_sensor import GenericSensor


class DepthSensor(GenericSensor):
    def __init__(self):
        """Initialize the DepthSensor object."""
        super().__init__(name="depth_sensor")

        self.sensor = ms5837.MS5837_02BA()  # Default I2C bus is 1 (Raspberry Pi 3)

        # We must initialize the sensor before reading it
        if not self.sensor.init():
            print("Sensor could not be initialized")
        else:
            print(f"Sensor {self.sensor} initialized successfully")

    def get_data(self) -> dict[str, float]:
        """Get the depth, pressure, and temperature from the sensor.

        Returns:
            dict[str, float]: The depth, pressure, and temperature.
        """
        # Print readings
        try:
            if self.sensor.read():
                return {
                    "depth": self.sensor.depth(),
                    "pressure_atm": self.sensor.pressure(ms5837.UNITS_atm),  # Default is mbar (no arguments)
                    "temperature_C": self.sensor.temperature(),  # Default is degrees C (no arguments)
                }
            else:
                print("Sensor read failed!")
                return {
                    "depth": 0,
                    "pressure_mbar": 0,
                    "temperature_C": 0,
                }
        except Exception as e:
            print(f"Error reading sensor: {e}")
            return {
                "depth": 0,
                "pressure_mbar": 0,
                "temperature_C": 0,
            }
