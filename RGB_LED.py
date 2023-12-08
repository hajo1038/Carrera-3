from machine import I2C, SPI, Pin
import pyb

class RGB_LED:
    def __init__(self):
        self.red = Pin("PA9", Pin.OUT_PP)
        self.green = Pin("PA10", Pin.OUT_PP)
        self.blue = Pin("PG1", Pin.OUT_PP)

        self.red.value(0)
        self.green.value(0)
        self.blue.value(0)
