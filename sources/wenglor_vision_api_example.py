import socket
import time
import sys

# -------------------- User configuration -------------------

# Define parameters related to vision system and calibration
# These parameters should be customized based on the specific use case

# Choose between "camera_on_robot" or "camera_not_on_robot"
g_use_case = "camera_on_robot"

# Choose between "zvzj001", "zvzj002", "zvzj003", "zvzj004"
# choose "zvzj001" instead of "zvzj005" and "zvzj002" instead of "zvzj006"
g_calibration_target = "zvzj003"

# Define the IP address and port of the vision system
g_vision_device_ip = "192.168.100.1"
g_vision_device_port = 32006

g_detection_job = "find_objects.u3p"
g_calibration_job = "calibration.u3p"

# Define calibration poses and the detection pose, set to zero to do "unset checks"
g_calib_pose_1 = [0, 0, 0, 0, 0, 0]
g_calib_pose_2 = [0, 0, 0, 0, 0, 0]
g_calib_pose_3 = [0, 0, 0, 0, 0, 0]
g_calib_pose_4 = [0, 0, 0, 0, 0, 0]
g_calib_pose_5 = [0, 0, 0, 0, 0, 0]
# X, Y, Z in meters, angles of rotation vector in radians

detection_pose = [0, 0, 0, 0, 0, 0]

g_cam_error_state = ""          # Stores error state of the vision system
g_calibration_done = False      # Indicates whether calibration is completed

# -------------------- Utilities ----------------------------

# Global socket
vision_socket = None

""" Utility functions for user interaction and robot control """

def ui_message(text):
    """ Simulate a message in the user interface """
    print("[UI]:", text)

def user_dialog(message):
    """ Simulate a user dialog for confirmation """
    print("[Prompt]:", message)
    return True

def exit_program():
    print("Exiting program.")
    sys.exit()

def wait_seconds(seconds):
    time.sleep(seconds)

def get_tcp_pose():
    """ Simulate getting the current TCP pose of the robot"""
    # here we just use a fake pose
    return [0.1, 0.2, 0.3, 3.14, 1.57, 1.57]

def to_string(pose):
    """ Convert a pose to a string representation, to be sent to the vision device """
    pose_data = ','.join(map(str, pose))
    # Add brackets to match the expected format
    pose_string = f"[{pose_data}]"
    return pose_string

def str_to_int(response):
    try:
        val = int(response.strip())
        return val, True
    except:
        return 0, False

def str_to_float(response):
    try:
        val = float(response.strip())
        return val, True
    except:
        return 0.0, False

def are_calibration_poses_set():
    """ Check if calibration poses are set to non-zero values """
    global g_calib_pose_1, g_calib_pose_2, g_calib_pose_3, g_calib_pose_4, g_calib_pose_5
    if (g_calib_pose_1 == [0, 0, 0, 0, 0, 0] or
            g_calib_pose_2 == [0, 0, 0, 0, 0, 0] or
            g_calib_pose_3 == [0, 0, 0, 0, 0, 0] or
            g_calib_pose_4 == [0, 0, 0, 0, 0, 0] or
            g_calib_pose_5 == [0, 0, 0, 0, 0, 0]):
        return False
    return True


def to_pose(response):
    """ Convert the response string from the vision device to a pose """
    return [100, 200, 300, 0, 0, 0]

def move_j(pose):
    """ Simulate moving the robot to a position with joint interpolation """
    print("MoveJ to:", pose)

def move_l(pose):
    """ Simulate moving the robot to a position with linear interpolation """
    print("MoveL to:", pose)

# -------------------- TCP Socket Handling --------------------

def open_socket():
    global vision_socket
    try:
        vision_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        vision_socket.settimeout(2)
        vision_socket.connect((g_vision_device_ip, g_vision_device_port))
    except Exception as e:
        ui_message(f"Socket error: {e}")
        vision_socket = None

def close_socket():
    global vision_socket
    if vision_socket:
        vision_socket.close()
        vision_socket = None

def recover_connection():
    """ Attempt to recover the connection to the vision system """
    global vision_socket
    if vision_socket:
        ui_message("Connection is already open")
        return True
    for _ in range(3):  # Try 3 times
        close_socket()
        wait_seconds(0.5)  # Wait before retrying
        open_socket()
        if vision_socket:
            return True
    ui_message("Failed to reconnect to vision device")
    return False

def send_command(command):
    global vision_socket
    if not vision_socket:
        open_socket()
        if not vision_socket:
            return False
    try:
        vision_socket.sendall((command + "\n").encode())
        return True
    except:
        recover_connection()
        if vision_socket:
            try:
                vision_socket.sendall((command + "\n").encode())
                return True
            except:
                return False
        return False

def receive_response():
    global vision_socket
    try:
        data = vision_socket.recv(1024)
        return data.decode().strip(), True
    except:
        recover_connection()
        if vision_socket:
            try:
                data = vision_socket.recv(1024)
                return data.decode().strip(), True
            except:
                return "", False
        return "", False

def send_and_receive(command):
    if not send_command(command):
        return "", False
    return receive_response()

# -------------------- Error Handling --------------------

def set_error_code(error_code):
    global g_cam_error_state
    code = abs(error_code)

    if code == 5001:
        g_cam_error_state = "General Error"
    elif code == 5002:
        g_cam_error_state = "Badly formatted request"
    elif code == 5003:
        g_cam_error_state = "No connection to uniVision"
    elif code == 5004:
        g_cam_error_state = "Unknown uniVision job name"
    elif code == 5005:
        g_cam_error_state = "Badly configured uniVision job"
    elif code == 5006:
        g_cam_error_state = "Calibration failed"
    elif code == 5007:
        g_cam_error_state = "No calibration data"
    elif code == 5008:
        g_cam_error_state = "No object found"
    elif code == 5009:
        g_cam_error_state = "Bad or empty device message"
    elif code == 5010:
        g_cam_error_state = "Index error"
    else:
        g_cam_error_state = "Unknown error"

    ui_message("Vision system error: " + g_cam_error_state)

def check_reply(response):
    global g_cam_error_state
    if response == "":
        g_cam_error_state = "General Error"
        return False

    error_code, ok = str_to_int(response)
    if ok and error_code < 0:
        set_error_code(error_code)
        exit_program()
        return False
    return True

# -------------------- Vision Functions --------------------

def load_job(job_name):
    """ Load a uniVision job on the vision system. """
    response, ok = send_and_receive("job:change[" + job_name + "];")
    if not ok:
        ui_message("Job load failed")
    return check_reply(response)

def update_camera_status():
    """Checks the current status of the vision system and updates calibration state."""
    global g_calibration_done, g_cam_error_state
    response, ok = send_and_receive("state[" + g_use_case + "];")
    if not ok or len(response) < 2:
        g_cam_error_state = "Camera in error"
        return

    if response[0] == '0':
        g_cam_error_state = ""
    else:
        g_cam_error_state = "Camera error"

    if response[1] == '0':
        g_calibration_done = False
    else:
        g_calibration_done = True

def run_calibration():
    """Executes a calibration procedure for the vision system."""
    global detection_pose

    if not are_calibration_poses_set():
        ui_message("Calibration poses not set. Please set them before calibration.")
        exit_program()
        return

    update_camera_status()

    if g_calibration_done:
        answer = user_dialog("Calibration already done. Redo?")
        if not answer:
            ui_message("Calibration skipped")
            return

    send_and_receive("calibration:clear;")
    load_job(g_calibration_job)

    # Prompt user dialog, based on camera placement
    if g_use_case == "camera_on_robot":
        prompt = "Place calibration board. Ready?"
    elif g_use_case == "camera_not_on_robot":
        prompt = "Mount calibration board and select tool. Ready?"
    else:
        ui_message("Invalid use case")
        exit_program()

    answer = user_dialog(prompt)
    if not answer:
        ui_message("Calibration aborted")
        return

    # Move through calibration poses
    move_j(g_calib_pose_1)
    tcp_pose = to_string(get_tcp_pose())
    send_and_receive(f"calibration:add[{tcp_pose}];")

    move_j(g_calib_pose_2)
    tcp_pose = to_string(get_tcp_pose())
    send_and_receive(f"calibration:add[{tcp_pose}];")

    move_j(g_calib_pose_3)
    tcp_pose = to_string(get_tcp_pose())
    send_and_receive(f"calibration:add[{tcp_pose}];")

    move_j(g_calib_pose_4)
    tcp_pose = to_string(get_tcp_pose())
    send_and_receive(f"calibration:add[{tcp_pose}];")

    move_j(g_calib_pose_5)
    tcp_pose = to_string(get_tcp_pose())
    send_and_receive(f"calibration:add[{tcp_pose}];")

    # Compute calibration results
    cmd = "calibration:calculate[" + g_use_case + "," + g_calibration_target + "];"
    response, ok = send_and_receive(cmd)
    check_reply(response)

    val, ok = str_to_float(response)
    if not ok:
        ui_message("Invalid calibration result")
        exit_program()

    # First calibration poses estimates relation from cam to ground,
    # so it has to be set as the detection pose
    if g_use_case == "camera_on_robot":
        detection_pose[:] = g_calib_pose_1[:]
    elif g_use_case == "camera_not_on_robot":
        # For the second calibration step the calibration board is placed on the object plane.
        # Therefore the robot needs to move to the detection pose to not cover it
        if detection_pose == [0, 0, 0, 0, 0, 0]:
            ui_message("Detection pose not set. Please set it before calibration.")
            exit_program()
        move_j(detection_pose)
        answer = user_dialog("Confirm when calibration board was placed on object ground.")
        if answer:
            response, ok = send_and_receive("calibration:ground[" + g_calibration_target + "];")
            check_reply(response)
        else:
            ui_message("Calibration step 2 aborted")
            exit_program()

def validate_calibration(offset_mm):
    if not user_dialog("Do you want to validate the calibration?"):
        ui_message("Calibration validation aborted")
        return

    move_j(detection_pose)

    pose_str = to_string(get_tcp_pose())
    cmd = "validate[" + g_use_case + "," + pose_str + "];"
    response, ok = send_and_receive(cmd)

    error_code, parse_ok = str_to_int(response)
    if parse_ok and error_code < 0:
        set_error_code(error_code)
        exit_program()
        return

    pose = to_pose(response)
    pose[2] = pose[2] + offset_mm  # assume Z is at index 2
    move_l(pose)
    user_dialog("Confirm when calibration result was checked.")


def read_num_objects():
    cmd = "num_objects:get;"
    response, ok = send_and_receive(cmd)
    num_objects, parse_ok = str_to_int(response)
    if not parse_ok or num_objects < 0:
        set_error_code(num_objects)
        return -1
    return num_objects

def read_pose_by_index(index):
    cmd = "pose:get[" + str(index) + "];"
    response, ok = send_and_receive(cmd)

    error_code, parse_ok = str_to_int(response)
    if parse_ok and error_code < 0:
        set_error_code(error_code)
        exit_program()
        return None

    pose = to_pose(response)
    return pose

def read_shape_by_index(index):
    cmd = "shape:get[" + str(index) + "];"
    response, ok = send_and_receive(cmd)
    shape_id, parse_ok = str_to_int(response)
    if not parse_ok or shape_id < 0:
        set_error_code(shape_id)
        return -1
    return shape_id

def read_value_by_index(index):
    cmd = "value:get[" + str(index) + "];"
    response, ok = send_and_receive(cmd)
    if not ok:
        ui_message("Failed to read value")
        return None
    return response  # response is a raw string, format depends on the use case


def detect_objects():
    pose_str = to_string(get_tcp_pose())
    cmd = "detect[" + g_use_case + "," + pose_str + "];"
    response, ok = send_and_receive(cmd)

    val, is_error = str_to_int(response)
    if is_error and val < 0:
        set_error_code(val)
        exit_program()
        return None

    return to_pose(response)

def prepare_detection():
    """ Prepare the robot for detection by updating camera status and loading the job. """
    update_camera_status()

    if not g_calibration_done:
        run_calibration()
        validate_calibration(10)

    load_job(g_detection_job)
    move_j(detection_pose)

def single_detection():
    prepare_detection()

    object_pose = detect_objects()
    move_l(object_pose)

    close_socket()

def multiple_detection():
    prepare_detection()

    num_objects = read_num_objects()
    if num_objects <= 0:
        ui_message("No objects found.")
        close_socket()
        return

    for i in range(num_objects):
        pose = read_pose_by_index(i)
        shape = read_shape_by_index(i)
        value = read_value_by_index(i)

        # Here you can add conditional checks for shape or value

        move_l(pose)

    close_socket()

# -------------------- Main --------------------

def main():
    print("=== EXAMPLE PROGRAM ONLY ===")
    single_detection()
    #multiple_detection()

if __name__ == "__main__":
    main()
