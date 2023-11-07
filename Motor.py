# Script for:
# - driving the motor
# - measure rpm with moving average
# - implement pi controller

from machine import Pin #needed for controll the GPIO pins
from pyb import Timer
import time
from machine import I2C
from ina219 import INA219

class Motor:
    def __init__(self, PWM_frequency):
        #Pin assignments
        AIN1 = Pin("PE11", Pin.OUT_PP)
        AIN2 = Pin("PF3", Pin.OUT_PP)
        PWM_pin = Pin("PE13")
        #STBY = Pin(6, Pin.OUT_PP)

        tim = Timer(1, freq=PWM_frequency)
        pwm_channel = tim.channel(3, Timer.PWM, pin=PWM_pin)
        AIN1.value(0)
        AIN2.value(0)

    def drive_forward(self, percentage):
        AIN1.value(1)
        AIN2.value(0)
        pwm_channel.pulse_width_percent(percentage)
