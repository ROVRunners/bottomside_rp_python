from pymavlink import mavutil
import threading


def parse_message(message: str) -> list[str]:
    sensor_data = {}
    sensor_name = "FLIGHT_CONTROLLER_" + message.split("{")[0]

    message = message.split("{")[1].split("}")[0]
    message_array = message.split(", ")

    for item in message_array:
        key, value = item.split(": ")
        sensor_data[key] = value

    return [sensor_name, sensor_data]


class FC:
    def __init__(self, port: str = "com16") -> None:
        # Set up the connection
        self.port = port  # "com16"  # Change this to the port that the pi is connected
        self.connection = mavutil.mavlink_connection(self.port)

        # Wait for the heartbeat to confirm the connection.
        self.connection.wait_heartbeat()
        print("Heartbeat from system (system %u component %u)" % (self.connection.target_system,
                                                                  self.connection.target_component))

        self._sensor_data = {}
        self.data_lock = threading.Lock()

        # Define the command types. (informational)
        # self.command_types = ['ATTITUDE_TARGET', 'SERVO_OUTPUT_RAW', 'VIBRATION', 'ESTIMATOR_STATUS', 'PING',
        #                       'SYS_STATUS', 'ACTUATOR_CONTROL_TARGET', 'SCALED_IMU2', 'TIMESYNC', 'ATTITUDE',
        #                       'ATTITUDE_QUATERNION', 'EXTENDED_SYS_STATE', 'ALTITUDE', 'BATTERY_STATUS', 'VFR_HUD',
        #                       'SCALED_IMU', 'HIGHRES_IMU', 'SYSTEM_TIME', 'HEARTBEAT', 'ODOMETRY']

    def _get_message(self):
        return parse_message(self.connection.recv_match(blocking=True))

    def send_message(self, message) -> None:
        self.connection.mav.send(message)

    def get_sensor_data(self) -> dict[str: dict]:
        with self.data_lock:
            data = self._sensor_data
        return data

    def set_pwm(self, pwm_values: list[int]) -> None:
        for i in range(len(pwm_values)):
            self.connection.mav.command_long_send(
                target_system=1,  # Replace with your target system ID
                target_component=1,  # Replace with your target component ID
                command=mavutil.mavlink.MAV_CMD_DO_SET_ACTUATOR,
                confirmation=0,
                param1=i + 1,  # Actuator index (channel number)
                param2=pwm_values[i],  # PWM value
                param3=0,
                param4=0,
                param5=0,
                param6=0,
                param7=0
            )

    def data_compiler_loop(self) -> None:
        while True:
            message = self._get_message()
            with self.data_lock:
                self._sensor_data[message[0]] = message[1]

    def __del__(self):
        self.connection.close()
