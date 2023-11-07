from machine import Pin
from pyb import Timer
import time
from machine import I2C
from ina219 import INA219

I2C_INTERFACE_NO = 1
SHUNT_OHMS = 0.1  # Check value of shunt used with your INA219

ina = INA219(SHUNT_OHMS, I2C(I2C_INTERFACE_NO))
ina.configure(ina.RANGE_16V)
print("Bus Voltage: %.3f V" % ina.voltage())
print("Current: %.3f mA" % ina.current())
print("Power: %.3f mW" % ina.power())

while True:
    print("Current: %.3f mA" % ina.current())
