# Untitled - By: jonathanhaller - Sa. Nov. 11 2023
from lsm6dsox import LSM6DSOX
from machine import SPI, Pin

class IMU:
    def __init__(self):
        self.lsm = LSM6DSOX(SPI(5), cs_pin=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)) # initialize acc/gyro

    def read_acc_xyz(self):
         acc_data = self.lsm.read_accel()

         acc_xy = list(acc_data)
         acc_xy[0] = acc_xy[0] * (-9.740856635) + 0.05092865    # calculate a_x in m/s^2
         acc_xy[1] = acc_xy[1] * (-9.612617632) + 0.17292818    # calculate a_y in m/s^2
         acc_xy[2] = acc_xy[2] * 9.94603749974 - 0.090163185
         return acc_xy

    def read_gyro_z(self):
        gyro_data = self.lsm.read_gyro()
        gyro_z = gyro_data[2] * 1.3 + 0.0704      # calculate gyro_z with offset
        return gyro_z
