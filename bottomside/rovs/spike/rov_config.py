import enum


# Define the Thrusters and Orientations
class ThrusterPositions(enum.StrEnum):
    """The thrusters and associated names available to this ROV.

    Implements:
        enum.StrEnum

    Properties:
        FRONT_RIGHT (str):
            The front right thruster.
        FRONT_LEFT (str):
            The front left thruster.
        REAR_RIGHT (str):
            The rear right thruster.
        REAR_LEFT (str):
            The rear left thruster.
        FRONT_RIGHT_VERTICAL (str):
            The front right vertical thruster.
        FRONT_LEFT_VERTICAL (str):
            The front left vertical thruster.
        REAR_RIGHT_VERTICAL (str):
            The rear right vertical thruster.
        REAR_LEFT_VERTICAL (str):
            The rear left vertical thruster.
    """
    FRONT_RIGHT = "FRONT_RIGHT",
    FRONT_LEFT = "FRONT_LEFT",
    REAR_RIGHT = "REAR_RIGHT",
    REAR_LEFT = "REAR_LEFT",
    FRONT_RIGHT_VERTICAL = "FRONT_RIGHT_VERTICAL",
    FRONT_LEFT_VERTICAL = "FRONT_LEFT_VERTICAL",
    REAR_RIGHT_VERTICAL = "REAR_RIGHT_VERTICAL",
    REAR_LEFT_VERTICAL = "REAR_LEFT_VERTICAL",

    def __repr__(self):
        return self.value


class ROVConfig:

    def __init__(self):
        self.rov_name = "Spike"
        self.ip = "localhost"
        self.video_port = 5600
        self.comms_port = 1883
