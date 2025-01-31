from smbus2 import SMBus


class I2CObject:

    def __init__(self, name: str, bus: SMBus | None = None) -> None:
        """Initialize the I2C object.

        Args:
            name (str):
                The name of the object
        """
        self.name: str = name

        self.bus: SMBus | None = bus

        self.address: int | None = None

        # dict[Register name, tuple[register address, # of bytes]
        self.read_registers: dict[str, tuple[int, int]] = {}
        # dict[Register address, byte]
        self.write_registers: dict[int, int] = {}
        # dict[Register address, byte]
        self.poll_registers: dict[int, int] = {}


    def read_and_write(self) -> dict[int, dict[int, int]]:
        """Automatically write to read from the object and return the read data.

        Returns:
            dict[str, dict[int, int]]: The data read from the object formatted as {register name: dict[register offset: value]}.
        """
        if self.address is None:
            return {}

        return_data = {}

        # Write and remove any one-time messages.
        if self.write_registers:
            for register in self.write_registers:
                print(register, self.write_registers[register])
                self.write_byte(int(register), int(self.write_registers[register]))

            self.write_registers.clear()
        
        # Write but do not remove any reoccuring messages.
        if self.poll_registers:
            for register in self.poll_registers:
                self.write_byte(int(register), int(self.poll_registers[register]))

        # Read any data requested.
        for register in self.read_registers:
            
            # Shorten vars.
            reg = int(self.read_registers[register][0])
            reg_len = int(self.read_registers[register][1])

            # Get the data.
            data = self.read_i2c_block_data(reg, reg_len)

            # Put all items requested into a dictionary
            return_nums = {}
            for i, datum in enumerate(data):
                return_nums[i] = datum

            # Add it to the list of register data.
            return_data[register] = return_nums

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
        self.bus: int = SMBus(bus_number)

        self.objects: dict[str, I2CObject] = {}

    def add_object(self, obj: I2CObject) -> None:
        """Add an object to the I2C handler.

        Args:
            obj (I2CObject):
                The object to add.
        """
        obj.bus = self.bus
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

    def read_objects(self) -> dict[str, dict[int, dict[int, int]]]:
        """Read all objects if they are set to read and return the data.

        Returns:
            dict[str, dict[int, dict[int, int]]]: The data read from the objects formatted as {object_name: {register: value}}.
        """
        return_data = {}

        for obj in self.objects:
            return_data[obj] = self.objects[obj].read_and_write()

        return return_data
