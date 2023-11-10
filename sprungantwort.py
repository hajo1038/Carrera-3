from hall_sensor import HallSensor
from current_sensor import CurrentSensor
from Motor import Motor
import time
import pyb
import os

# create objects
hall_sensor = HallSensor('PE14')
#current_sensor = CurrentSensor()
myMotor = Motor(200)

# Parameters for step response recording
record_start_time = 500  # mseconds
record_duration = 1000  # mseconds
record_end_time = record_start_time + record_duration
rpm_timer = 0

file_counter = 0
file_path = f'step_response_data_{file_counter}.txt'
while file_path in os.listdir():
    file_counter += 1
    file_path = f'step_response_data_{file_counter}.txt'

myMotor.drive_forward(0)
pyb.delay(1000)
# Open the file for writing
with open(file_path, 'w') as file:
    # Write header
    file.write("Time (s), RPM\n")

    # Start the motor
    print('3...2...1...')
    pyb.delay(3000)

    start_time = pyb.millis()
    while True:
        current_time = pyb.millis() - start_time
        if current_time > record_start_time and current_time < record_end_time:
           myMotor.drive_forward(100)
        elif current_time >= record_end_time:
            myMotor.drive_forward(0)
            break

        if pyb.millis() - rpm_timer > 15:
            rpm_filtered = hall_sensor.get_rpm_filtered()
            file.write(f"{current_time},{rpm_filtered}\n")
            rpm_timer = pyb.millis()



