import smbus


class I2CObject:

    def __init__(self, name: str) -> None:
        """Initialize the I2C object.

        Args:
            name (str):
                The name of the object
        """
        self.name: str = name

        self.bus = None

        self.address: int | None = None

        # dict[Register name, tuple[register address, # of bytes]
        self.read_registers: dict[str, tuple[int, int]] = {}
        # dict[Register address, byte]
        self.write_registers: dict[int, int] = {}
        # dict[Register address, byte]
        self.poll_registers: dict[int, int] = {}

        # self.register_names: dict[int, str] = {}


    def read(self, bus: smbus.SMBus) -> dict[int, bytes]:
        """Automatically write to read from the object and return the read data.

        Args:
            bus (smbus.SMBus):
                The bus to read from.

        Returns:
            dict[str, bytes]: The data read from the object formatted as {register name: value}.
        """
        return_data = {}

        # Write and remove any one-time messages.
        for register in self.write_registers:
            bus.write_byte(self.address, self.write_registers[register])
            self.write_registers.pop(register)
        
        # Write but do not remove any reoccuring messages.
        for register in self.poll_registers:
            bus.write_byte(self.address, self.poll_registers[register])

        # Read any data requested.
        for register in self.read_registers:
            
            # Shorten vars.
            reg = self.read_registers[register][0]
            reg_len = self.read_registers[register][1]

            # Get the data.
            data = self.read_i2c_block_data(reg, reg_len)

            # Repeatedly append all data collected from this register list into a single big conatenated
            # binary string in the form of an int. If only a single number, this has no effect.
            return_num = 0
            for i, datum in enumerate(data):
                return_num |= datum >> (8*i)
            
            # Add it to the list of register data.
            return_data[register] = return_num

        return return_data

    def write_byte(self, register: int, value: int) -> int:
        self.bus.write_byte_data(self.address, register, value)

    def read_byte(self, register: int) -> int:
        return self.bus.read_byte_data(self.address, register)

    def read_word(self, register: int) -> int:
        return self.bus.read_word_data(self.address, register)

    def read_i2c_block_data(self, register: int, length: int) -> int:
        return self.bus.read_i2c_block_data(self.address, register, length)

    def write_i2c_block_data(self, register: int, data: int) -> int:
        self.bus.write_i2c_block_data(self.address, register, data)


class I2CHandler:

    def __init__(self, bus_number: int = 1) -> None:
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
