#from hall_sensor import HallSensor
#from current_sensor import CurrentSensor
from IMU import IMU
from Motor import Motor
from hall_sensor import HallSensor
from current_sensor import CurrentSensor
import time
import pyb
import os

# create objects
# hall_sensor = HallSensor('PE14')
#current_sensor = CurrentSensor()
myMotor = Motor(200)
myIMU = IMU()
hall_sensor = HallSensor('PG12', 500)
current_sensor = CurrentSensor()


# Parameters for step response recording
record_start_time = 100  # mseconds
record_duration = 30000  # mseconds
record_end_time = record_start_time + record_duration
rpm_timer = 0

file_counter = 0
file_path = f'imu_measurement_{file_counter}.txt'
while file_path in os.listdir():
    file_counter += 1
    file_path = f'imu_measurement_{file_counter}.txt'

myMotor.drive_forward(0)
pyb.delay(1000)
# Open the file for writing
with open(file_path, 'w') as file:
    # Write header
    file.write("Time (ms), acc_x, acc_y, acc_z, gyro_z, rpm, rpm_unfiltered, current, avg_current\n")

    # Start the motor
    print('3...2...1...')
    pyb.delay(3000)

    start_time = pyb.millis()
    while True:
        current_time = pyb.millis() - start_time
        if current_time > record_start_time and current_time < record_end_time:
           myMotor.drive_forward(40)
        elif current_time >= record_end_time:
            myMotor.drive_forward(0)
            break
        if pyb.millis() - rpm_timer >= 5:
            acc_xy = myIMU.read_acc_xyz()
            gyro_z = myIMU.read_gyro_z()

            rpm = hall_sensor.get_rpm_filtered()
            rpm_unfiltered = hall_sensor.get_rpm_unfiltered()

            current_sensor.update_current_average()
            avg_current = current_sensor.get_averaged_current()
            current = current_sensor.get_actual_current()

            file.write(f"{current_time},{acc_xy[0]},{acc_xy[1]},{acc_xy[2]},{gyro_z},{rpm},{rpm_unfiltered},{current},{avg_current}\n")
            rpm_timer = pyb.millis()
