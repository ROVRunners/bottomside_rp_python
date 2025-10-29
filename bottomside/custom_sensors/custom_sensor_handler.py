from custom_sensors.depth_sensor import DepthSensor
from custom_sensors.generic_sensor import GenericSensor


class CustomSensorHandler:
    def __init__(self) -> None:
        """Initialize the custom sensor handler."""
        self.sensors: list[GenericSensor] = [DepthSensor()]

    def get_data(self) -> dict:
        """Get the data from all the sensors."""
        data = {}
        for sensor in self.sensors:
            data[sensor.name] = sensor.get_data()
        return data
