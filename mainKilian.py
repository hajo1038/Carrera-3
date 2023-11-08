from hall_sensor import HallSensor
from current_sensor import CurrentSensor
from Motor import Motor
import time

#create objects
hall_sensor = HallSensor('PE14')
current_sensor = CurrentSensor()
myMotor = Motor(200)
myMotor.drive_forward(0)

while True:
    act_current = current_sensor.get_actual_current()
    filterd_current = current_sensor.get_averaged_current()
    print(filterd_current)
    if (hall_sensor.averaged_current_flag == True):
        current_sensor.update_current_average()
        averaged_current_flag = False
    time.sleep(0.1)

