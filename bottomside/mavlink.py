import json
import threading
from enum import Enum
from queue import Queue

from pymavlink import mavutil


class MessageTypes (Enum):
    HEARTBEAT = 0
    SYS_STATUS = 1
    SYSTEM_TIME = 2
    PING = 4
    CHANGE_OPERATOR_CONTROL = 5
    CHANGE_OPERATOR_CONTROL_ACK = 6
    AUTH_KEY = 7
    SET_MODE = 11
    PARAM_REQUEST_READ = 20
    PARAM_REQUEST_LIST = 21
    PARAM_VALUE = 22
    PARAM_SET = 23
    GPS_RAW_INT = 24
    GPS_STATUS = 25
    SCALED_IMU = 26
    RAW_IMU = 27
    RAW_PRESSURE = 28
    SCALED_PRESSURE = 29
    ATTITUDE = 30
    ATTITUDE_QUATERNION = 31
    LOCAL_POSITION_NED = 32
    GLOBAL_POSITION_INT = 33
    RC_CHANNELS_SCALED = 34
    RC_CHANNELS_RAW = 35
    SERVO_OUTPUT_RAW = 36
    MISSION_REQUEST_PARTIAL_LIST = 37
    MISSION_WRITE_PARTIAL_LIST = 38
    MISSION_ITEM = 39
    MISSION_REQUEST = 40
    MISSION_SET_CURRENT = 41
    MISSION_CURRENT = 42
    MISSION_REQUEST_LIST = 43
    MISSION_COUNT = 44
    MISSION_CLEAR_ALL = 45
    MISSION_ITEM_REACHED = 46
    MISSION_ACK = 47
    SET_GPS_GLOBAL_ORIGIN = 48
    GPS_GLOBAL_ORIGIN = 49
    PARAM_MAP_RC = 50
    MISSION_REQUEST_INT = 51
    SAFETY_SET_ALLOWED_AREA = 54
    SAFETY_ALLOWED_AREA = 55
    ATTITUDE_QUATERNION_COV = 61
    NAV_CONTROLLER_OUTPUT = 62
    GLOBAL_POSITION_INT_COV = 63
    LOCAL_POSITION_NED_COV = 64
    RC_CHANNELS = 65
    REQUEST_DATA_STREAM = 66
    DATA_STREAM = 67
    MANUAL_CONTROL = 69
    RC_CHANNELS_OVERRIDE = 70
    MISSION_ITEM_INT = 73
    VFR_HUD = 74
    COMMAND_INT = 75
    COMMAND_LONG = 76
    COMMAND_ACK = 77
    MANUAL_SETPOINT = 81
    SET_ATTITUDE_TARGET = 82
    ATTITUDE_TARGET = 83
    SET_POSITION_TARGET_LOCAL_NED = 84
    POSITION_TARGET_LOCAL_NED = 85
    SET_POSITION_TARGET_GLOBAL_INT = 86
    POSITION_TARGET_GLOBAL_INT = 87
    LOCAL_POSITION_NED_SYSTEM_GLOBAL_OFFSET = 89
    HIL_STATE = 90
    HIL_CONTROLS = 91
    HIL_RC_INPUTS_RAW = 92
    HIL_ACTUATOR_CONTROLS = 93
    OPTICAL_FLOW = 100
    GLOBAL_VISION_POSITION_ESTIMATE = 101
    VISION_POSITION_ESTIMATE = 102
    VISION_SPEED_ESTIMATE = 103
    VICON_POSITION_ESTIMATE = 104
    HIGHRES_IMU = 105
    OPTICAL_FLOW_RAD = 106
    HIL_SENSOR = 107
    SIM_STATE = 108
    RADIO_STATUS = 109
    FILE_TRANSFER_PROTOCOL = 110
    TIMESYNC = 111
    CAMERA_TRIGGER = 112
    HIL_GPS = 113
    HIL_OPTICAL_FLOW = 114
    HIL_STATE_QUATERNION = 115
    SCALED_IMU2 = 116
    LOG_REQUEST_LIST = 117
    LOG_ENTRY = 118
    LOG_REQUEST_DATA = 119
    LOG_DATA = 120
    LOG_ERASE = 121
    LOG_REQUEST_END = 122
    GPS_INJECT_DATA = 123
    GPS2_RAW = 124
    POWER_STATUS = 125
    SERIAL_CONTROL = 126
    GPS_RTK = 127
    GPS2_RTK = 128
    SCALED_IMU3 = 129
    DATA_TRANSMISSION_HANDSHAKE = 130
    ENCAPSULATED_DATA = 131
    DISTANCE_SENSOR = 132
    TERRAIN_REQUEST = 133
    TERRAIN_DATA = 134
    TERRAIN_CHECK = 135
    TERRAIN_REPORT = 136
    SCALED_PRESSURE2 = 137
    ATT_POS_MOCAP = 138
    SET_ACTUATOR_CONTROL_TARGET = 139
    ACTUATOR_CONTROL_TARGET = 140
    ALTITUDE = 141
    RESOURCE_REQUEST = 142
    SCALED_PRESSURE3 = 143
    FOLLOW_TARGET = 144
    CONTROL_SYSTEM_STATE = 146
    BATTERY_STATUS = 147
    AUTOPILOT_VERSION = 148
    LANDING_TARGET = 149
    ESTIMATOR_STATUS = 230
    WIND_COV = 231
    GPS_INPUT = 232
    GPS_RTCM_DATA = 233
    HIGH_LATENCY = 234
    HIGH_LATENCY2 = 235
    VIBRATION = 241
    HOME_POSITION = 242
    SET_HOME_POSITION = 243
    MESSAGE_INTERVAL = 244
    EXTENDED_SYS_STATE = 245
    ADSB_VEHICLE = 246
    COLLISION = 247
    V2_EXTENSION = 248
    MEMORY_VECT = 249
    DEBUG_VECT = 250
    NAMED_VALUE_FLOAT = 251
    NAMED_VALUE_INT = 252
    STATUSTEXT = 253
    DEBUG = 254
    SETUP_SIGNING = 256
    BUTTON_CHANGE = 257
    PLAY_TUNE = 258
    CAMERA_INFORMATION = 259
    CAMERA_SETTINGS = 260
    STORAGE_INFORMATION = 261
    CAMERA_CAPTURE_STATUS = 262
    CAMERA_IMAGE_CAPTURED = 263
    FLIGHT_INFORMATION = 264
    MOUNT_ORIENTATION = 265
    LOGGING_DATA = 266
    LOGGING_DATA_ACKED = 267
    LOGGING_ACK = 268


class Mavlink:
    """A class to handle MAVLink communication with an autopilot.

    Attributes:
        data_queue (Queue):
            A queue to store received data.
        data_dict (dict):
            A dictionary to store the most recent data for each category.

    Methods:
        get_data() -> dict:
            Get the most recent data for each received category from the queue.
        request_data(message_id: int, interval: int = 10_000) -> None:
            Request data from the autopilot.
        send_command(command: int, param1: float = 0, param2: float = 0, param3: float = 0, param4: float = 0,
                     param5: float = 0, param6: float = 0, param7: float = 0) -> None:
            Send a command to the autopilot.
    """
    def __init__(self, port: str = "/dev/ttyACM0") -> None:
        """Initialize the MAVLink connection.

        Args:
            port (str, optional):
                The port to connect to.
                Defaults to "/dev/ttyACM0".
        """
        self.data_queue = Queue()
        self.data_dict = {}

        # Establish the connection.
        try:
            self._mav = mavutil.mavlink_connection(port, baud=115200, source_system=255)
        except Exception as e:
            self._mav = None
            print(f"Failed to connect to MAVLink: {e}")
            return
        self._mav.wait_heartbeat()

        # Initialize the data queue and receiving thread.
        receiving_thread = threading.Thread(target=self._receive_data, args=[self.data_queue], daemon=True)

        # Start the receiving thread.
        receiving_thread.start()

    def get_data(self) -> dict[str, dict]:
        """Get the most recent data for each received category from the queue.

        Returns:
            dict: The most recent data for each category.
        """
        while not self.data_queue.empty():
            data = json.loads(self.data_queue.get())
            self.data_dict[data[0]] = data[1]

        return self.data_dict

    def request_data(self, message_id: int, interval: int = 10_000) -> None:
        """Request data from the autopilot.

        Args:
            message_id (int):
                The ID of the message to request.
            interval (int, optional):
                The interval at which to request the message in microseconds.
                Defaults to 10_000. (100 hertz)
        """
        if self._mav is None:
            return

        self._mav.mav.command_long_send(
            self._mav.target_system,
            self._mav.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
            0,  # Confirmation.
            message_id,  # Message ID to request.
            interval,  # Interval in microseconds.
            0, 0, 0, 0, 0  # Unused parameters.
        )

    def send_command(self, command: int, param1: float = 0, param2: float = 0, param3: float = 0, param4: float = 0,
                     param5: float = 0, param6: float = 0, param7: float = 0) -> None:
        """Send a command to the autopilot.

        Args:
            command (int):
                The command to send.
            param1 (float, optional):
                The first parameter.
                Defaults to 0.
            param2 (float, optional):
                The second parameter.
                Defaults to 0.
            param3 (float, optional):
                The third parameter.
                Defaults to 0.
            param4 (float, optional):
                The fourth parameter.
                Defaults to 0.
            param5 (float, optional):
                The fifth parameter.
                Defaults to 0.
            param6 (float, optional):
                The sixth parameter.
                Defaults to 0.
            param7 (float, optional):
                The seventh parameter.
                Defaults to 0.
        """
        if self._mav is None:
            return

        self._mav.mav.command_long_send(
            self._mav.target_system,
            self._mav.target_component,
            command,
            0,  # Confirmation.
            param1, param2, param3, param4, param5, param6, param7
        )

    def _receive_data(self, queue: Queue) -> None:
        """Receive data from the autopilot.

        Args:
            queue (Queue):
                The queue to store the data in.
        """
        while True:
            msg = self._mav.recv_match(blocking=True)
            queue.put({msg.get_type(): json.dumps(msg.to_dict())})
