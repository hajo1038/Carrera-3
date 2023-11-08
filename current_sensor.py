from machine import Pin, I2C
import time
from ina219 import INA219

class CurrentSensor:
    def __init__(self):
        self.I2C_INTERFACE_NO = 1 #select I2C Interface
        self.SHUNT_OHMS = 0.1 #value of shunt resistor in ohm
        self.ina = INA219(self.SHUNT_OHMS, I2C(self.I2C_INTERFACE_NO)) #creates instance of class
        self.ina.configure(self.ina.RANGE_16V)

         # Moving average for current measurement
        self.current_windows_size = 4
        self.current_avg_sum = 0
        self.current_readings = [0] * self.current_windows_size
        self.current_reading_index = 0
        self.averaged_current = 0
        print("Current Sensor wurde angelegt")


    def get_actual_current(self):
        return self.ina.current()



    def get_averaged_current(self):
        return self.averaged_current



    def update_current_average(self):
        current_measurement = self.get_actual_current()
        self.current_avg_sum -= self.current_readings[self.current_reading_index]
        self.current_readings[self.current_reading_index] = current_measurement
        self.current_avg_sum += current_measurement
        self.current_reading_index = (self.current_reading_index + 1) % self.current_windows_size
        self.averaged_current = self.current_avg_sum / (self.current_windows_size * 1.0)
