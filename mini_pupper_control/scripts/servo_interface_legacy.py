#!/usr/bin/python3

import math
import rospy
from trajectory_msgs.msg import JointTrajectory
import numpy as np
try:
    from MangDang.mini_pupper.ServoCalibration import NEUTRAL_ANGLE_DEGREES
    nvram_pickle = True
except ImportError:
    nvram_pickle = False

servo_pins = [15, 14, 13,  12, 11, 10,  9, 8, 7,  6, 5, 4]  # rf lf rb lb
servo_offset = []


def set_servo_angle(pin, angle):
    duty_cycle = int(500000+11111.11111*angle)
    servo_pin = "/sys/class/pwm/pwmchip0/pwm"+str(pin)+"/duty_cycle"
    with open(servo_pin, "w") as f:
        f.write(str(int(duty_cycle)))


def get_param():
    global servo_offset
    try:
        if nvram_pickle:
            matrix = NEUTRAL_ANGLE_DEGREES
        else:
            with open("/sys/bus/nvmem/devices/3-00500/nvmem", "rb") as nv_f:
                arr1 = np.array(eval(nv_f.readline()))
                arr2 = np.array(eval(nv_f.readline()))
                matrix = np.append(arr1, arr2)
                arr3 = np.array(eval(nv_f.readline()))
                matrix = np.append(matrix, arr3)
                matrix.resize(3, 4)
        rospy.loginfo("Get nv calibration params: "+str(matrix))
    except ValueError:
        matrix = np.array(
            [[0, 0, 0, 0], [45, 45, 45, 45], [-45, -45, -45, -45]])
        rospy.logerr(
            "Get nv calibration params failed, set to default params: "+str(matrix))
    line1 = matrix[0].tolist()
    line2 = matrix[1].tolist()
    line3 = matrix[2].tolist()
    servo_offset.append(90-line1[0])
    servo_offset.append(45+line2[0]+45)
    servo_offset.append(135+line3[0]+45)

    servo_offset.append(90-line1[1])
    servo_offset.append(135-line2[1]-45)
    servo_offset.append(45-line3[1]-45)

    servo_offset.append(90+line1[2])
    servo_offset.append(45+line2[2]+45)
    servo_offset.append(135+line3[2]+45)

    servo_offset.append(90+line1[3])
    servo_offset.append(135-line2[3]-45)
    servo_offset.append(45-line3[3]-45)


def callback(data):
    joint_positions = data.points[0].positions
    lf1_position = math.degrees(joint_positions[0])
    lf2_position = math.degrees(joint_positions[1])
    lf3_position = math.degrees(joint_positions[2])
    rf1_position = math.degrees(joint_positions[3])
    rf2_position = math.degrees(joint_positions[4])
    rf3_position = math.degrees(joint_positions[5])
    lb1_position = math.degrees(joint_positions[6])
    lb2_position = math.degrees(joint_positions[7])
    lb3_position = math.degrees(joint_positions[8])
    rb1_position = math.degrees(joint_positions[9])
    rb2_position = math.degrees(joint_positions[10])
    rb3_position = math.degrees(joint_positions[11])

    set_servo_angle(15, servo_offset[0]+rf1_position)  # 90
    set_servo_angle(14, servo_offset[1]-rf2_position)  # 90
    set_servo_angle(13, servo_offset[2]-90-rf2_position-rf3_position)  # 180

    set_servo_angle(12, servo_offset[3]+lf1_position)  # 90
    set_servo_angle(11, servo_offset[4]+lf2_position)  # 90
    set_servo_angle(10, servo_offset[5]+90+lf2_position+lf3_position)  # 0

    set_servo_angle(9, servo_offset[6]-rb1_position)  # 90
    set_servo_angle(8, servo_offset[7]-rb2_position)  # 90
    set_servo_angle(7, servo_offset[8]-90-rb2_position-rb3_position)  # 180

    set_servo_angle(6, servo_offset[9]-lb1_position)
    set_servo_angle(5, servo_offset[10]+lb2_position)
    set_servo_angle(4, servo_offset[11]+90+lb2_position+lb3_position)


def listener():
    rospy.init_node('servo_interface', anonymous=True)
    get_param()
    rospy.Subscriber("/joint_group_position_controller/command",
                     JointTrajectory, callback, queue_size=1)
    rospy.spin()


if __name__ == '__main__':
    listener()
