import smbus


class I2CObject:

    def __init__(self, address: int, name: str) -> None:
        """Initialize the I2C object.

        Args:
            address (int):
                The address of the object.
            name (str):
                The name of the object
        """
        self.address: int = address
        self.name: str = name

        self.bus = None

        self.read_registers: dict[int, int] = {}
        self.write_registers: dict[int, int] = {}

    def read(self, bus: smbus.SMBus) -> dict[int, bytes]:
        """Automatically write to read from the object and return the read data.

        Args:
            bus (smbus.SMBus):
                The bus to read from.

        Returns:
            dict[int, bytes]: The data read from the object formatted as {register: value}.
        """
        return_data = {}

        for register in self.write_registers:
            bus.write_byte(self.address, self.write_registers[register])

        for register in self.read_registers:
            return_data[register] = bus.read_byte(self.address, self.read_registers[register])

        return return_data

    def write_byte(self, register, value):
        self.bus.write_byte_data(self.address, register, value)

    def read_byte(self, register):
        return self.bus.read_byte_data(self.address, register)

    def read_word(self, register):
        return self.bus.read_word_data(self.address, register)

    def read_i2c_block_data(self, register, length):
        return self.bus.read_i2c_block_data(self.address, register, length)

    def write_i2c_block_data(self, register, data):
        self.bus.write_i2c_block_data(self.address, register, data)


class I2CHandler:

    def __init__(self, bus_number: int = 0) -> None:
        """Initialize the I2C handler.

        Args:
            bus_number (int, optional):
                The bus number to use.
                Defaults to 0.
        """
        self.bus: int = smbus.SMBus(bus_number)

        self.objects: dict[str, I2CObject] = {}

    def add_object(self, obj: I2CObject) -> None:
        """Add an object to the I2C handler.

        Args:
            obj (I2CObject):
                The object to add.
        """
        self.objects[obj.name] = obj

    def remove_object(self, obj: I2CObject | str) -> None:
        """Remove an object from the I2C handler.

        Args:
            obj (I2CObject | str):
                The name of the object or object itself to remove.
        """
        if isinstance(obj, str):
            del self.objects[obj]
        else:
            del self.objects[obj.name]

    def read_objects(self) -> dict[str, dict[int, bytes]]:
        """Read all objects if they are set to read and return the data.

        Returns:
            dict[str, dict[int, bytes]]: The data read from the objects formatted as {object_name: {register: value}}.
        """
        return_data = {}

        for obj in self.objects:
            return_data[obj] = self.objects[obj].read(self.bus)

        return return_data
