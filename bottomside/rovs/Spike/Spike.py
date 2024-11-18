class Spike:
    """Main class for the Spike ROV."""

    def __init__(self) -> None:
        """Initialize an instance of the class."""
        self.run = True

    def loop(self):
        pass

    def receive_commands(self, data: dict[str, object]) -> None:
        """Receive a packet from the surface with the specified data.

        Args:
            data (dict[str, object]):
                The data received from the surface.
        """
        pass

    def stop(self):
        pass
