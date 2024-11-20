import time

import rovs.spike.rov_config as rov_config
import bottomside.IMU as IMU
import bottomside.motors as motors
import bottomside.mqtt_connection as mqtt_connection


class ROV:
    def __init__(self):
        """Initialize an instance of the class."""

        # Variable to control whether the main loop of the ROV continues running.
        self.run = True

        # Set the number of loops per second and the number of nanoseconds per loop for rate limiting.
        self._loops_per_second = 60
        self._nanoseconds_per_loop = 1_000_000_000 // self._loops_per_second

        self.imu = IMU.IMU()
        # self.motors = motors.Motors()

        self._rov_config = rov_config.ROVConfig()

        self.mqtt_connection = mqtt_connection.MQTTConnection(
            ip=self._rov_config.ip,
            port=self._rov_config.comms_port,
            client_id=self._rov_config.rov_name
        )

        self.mqtt_connection.connect()

    def loop(self):
        start_loop: int = time.monotonic_ns()
        # self.imu.update()

        # Rate limit the loop to the specified number of loops per second.
        end_loop: int = time.monotonic_ns()
        loop_time: int = end_loop - start_loop
        sleep_time: float = (self._nanoseconds_per_loop - loop_time) / 1_000_000_000
        if sleep_time > 0:
            time.sleep(sleep_time)
            # print(sleep_time)
        pass

    def shutdown(self):
        """Shut down the ROV gracefully."""
        self.run = False
        self.mqtt_connection.disconnect()
