from time import sleep
from pymavlink import mavutil

# Set up the connection
port = "com16"  # "com16"  # Change this to the port that the pi is connected
connection = mavutil.mavlink_connection(port)

# Wait for the heartbeat to confirm the connection.
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (connection.target_system,
                                                          connection.target_component))

sleep(.5)

#
# def set_pwm(pwm_value: int, output) -> None:
#     # print("Arming motors")
#     # connection.arducopter_arm()
#     # connection.arducopter_arm()
#     # connection.arducopter_arm()
#     # print("waiting for motors to arm")
#     # connection.motors_armed_wait()
#     # print("Motors armed")


data = connection.recv_match(blocking=True, type="SERVO_OUTPUT_RAW")
print(data)

pwm = 1900
output = 9
print("setting PWM: 1600")

connection.arducopter_arm()
data = connection.recv_match(blocking=True, type=["COMMAND_NACK", "COMMAND_ACK"])
print(data)
connection.set_mode("MANUAL")
data = connection.recv_match(blocking=True, type=["COMMAND_NACK", "COMMAND_ACK"])
print(data)

connection.set_servo(output, pwm)
connection.mav.command_long_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
    0,
    output,
    pwm,
    0, 0, 0, 0, 0
)

data = connection.recv_match(blocking=True, type=["SERVO_OUTPUT_RAW", "COMMAND_ACK", "COMMAND_NACK"])
print(data)
data = connection.recv_match(blocking=True, type=["SERVO_OUTPUT_RAW", "COMMAND_ACK", "COMMAND_NACK"])
print(data)

