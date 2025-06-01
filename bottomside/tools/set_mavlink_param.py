import pymavlink

from pymavlink import mavutil


def get_mavlink_param(mav, param_name: str) -> float:
    """Get a MAVLink parameter from the autopilot.

    Args:
        mav (pymavlink.mavutil.mavlink_connection):
            The MAVLink connection object.
        param_name (str):
            The name of the parameter to get.

    Returns:
        float: The value of the parameter, or None if the parameter is not found.
    """
    if mav is None:
        return None

    mav.mav.param_request_read_send(
        mav.target_system,
        mav.target_component,
        param_name.encode('utf-8'),
        -1  # Request all parameters.
    )

    # Wait for the parameter to be received.
    msg = mav.recv_match(type='PARAM_VALUE', blocking=True)
    if msg is None or msg.param_id.decode('utf-8') != param_name:
        return None

    return msg.param_value

def set_mavlink_param(mav, param_name: str, param_value: float, param_type: int) -> None:
    """Set a MAVLink parameter on the autopilot.

    Args:
        mav (pymavlink.mavutil.mavlink_connection):
            The MAVLink connection object.
        param_name (str):
            The name of the parameter to set.
        param_value (float):
            The value to set the parameter to.
    """
    if mav is None:
        return

    mav.mav.param_set_send(
        mav.target_system,
        mav.target_component,
        param_name.encode('utf-8'),
        param_value,
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )
# 1	MAV_PARAM_TYPE_UINT8	8-bit unsigned integer
# 2	MAV_PARAM_TYPE_INT8	8-bit signed integer
# 3	MAV_PARAM_TYPE_UINT16	16-bit unsigned integer
# 4	MAV_PARAM_TYPE_INT16	16-bit signed integer
# 5	MAV_PARAM_TYPE_UINT32	32-bit unsigned integer
# 6	MAV_PARAM_TYPE_INT32	32-bit signed integer
# 7	MAV_PARAM_TYPE_UINT64	64-bit unsigned integer
# 8	MAV_PARAM_TYPE_INT64	64-bit signed integer
# 9	MAV_PARAM_TYPE_REAL32	32-bit floating-point
# 10	MAV_PARAM_TYPE_REAL64	64-bit floating-point


if __name__ == "__main__":
    # Example usage
    port: str = input("Enter the MAVLink connection string (e.g., '/dev/ttyACM0') or nothing to default to the example value: ") or "/dev/ttyACM0"
    mav = mavutil.mavlink_connection(port)
    mav.wait_heartbeat()

    print("MAVLink connection established.")

    # Example parameter name and value
    param_name = input("Enter the MAVLink parameter name to get/set (e.g., 'SENS_BOARD_Y_OFF'): ") or 'SENS_BOARD_Y_OFF'

    param_value = get_mavlink_param(mav, param_name)
    print(f"Current value of {param_name}: {param_value}")

    new_value = float(input(f"Enter a new value for {param_name} (current: {param_value}): ") or param_value)
    print("\nParam types:")
    print("1: MAV_PARAM_TYPE_UINT8")
    print("2: MAV_PARAM_TYPE_INT8")
    print("3: MAV_PARAM_TYPE_UINT16")
    print("4: MAV_PARAM_TYPE_INT16")
    print("5: MAV_PARAM_TYPE_UINT32")
    print("6: MAV_PARAM_TYPE_INT32")
    print("7: MAV_PARAM_TYPE_UINT64")
    print("8: MAV_PARAM_TYPE_INT64")
    print("9: MAV_PARAM_TYPE_REAL32")
    print("10: MAV_PARAM_TYPE_REAL64")

    param_type = max(min(int(input("\nEnter the parameter type (e.g., 1 for ): ") or 1), 10), 1)  # Ensure the type is between 1 and 10

    print(f"Setting {param_name} to {new_value} of type {param_type}.")
    set_mavlink_param(mav, param_name, new_value, param_type)

    updated_value = get_mavlink_param(mav, param_name)
    print(f"Confirmation: Updated value of {param_name}: {updated_value}")
    mav.close()
