class GenericSensor:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_data(self) -> dict[str, float]:
        raise NotImplementedError(f"Sensor {self.name} get_data() method not implemented.")
