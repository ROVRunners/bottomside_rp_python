from dataclasses import dataclass


@dataclass
class ROV:
    rov_name: str = "ROV"
    ip: str = "192.168.2.3"
    video_port: int = 5600
    comms_port: int = 1883
