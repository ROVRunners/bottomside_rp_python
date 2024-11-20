""""""


class Motor:
    """Basic motor pwm handler."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def start(self):
        print(f"Starting {self}")

    def stop(self):
        print(f"Stopping {self}")
