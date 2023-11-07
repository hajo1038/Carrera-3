# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!
# Drehzahl schwankt bei 3.3V zwischen +-100 U/min -> Vermutlich m
from Motor import Motor, Pin
import time

hallSensorPin = Pin('PE14', Pin.IN)

#variables for rpm measurement
curenntMicros = 0
lastMicros = 0
rpmMeasured = 0

#moving average
windowSize = 4
avgSum = 0
readings = [0] * windowSize #initialize the readings array with zeros
readingsIndex = 0

def hall_ISR(pin):
    global currentMicros, lastMicros, rpmMeasured
    currentMicros = time.ticks_us()
    rpmMeasured = 60000000/(4*(currentMicros-lastMicros))
    lastMicros = currentMicros


def moving_average():
    global readingsIndex
    readings[readingsIndex] = rpmMeasured
    readingsIndex = (readingsIndex + 1) % windowSize  # Circular buffer
    moving_average = sum(readings)/windowSize
    print("Current RPM:", rpmMeasured)
    print("Moving Average RPM:", moving_average)


#configures an interrupt for hallSensorPin
#triggers interrupt when Pin changes from LOW to HIGH (rising edge)
#handler calls the function hall_ISR
hallSensorPin.irq(trigger=Pin.IRQ_RISING, handler=hall_ISR)


#creates object of motor
myMotor = Motor(2000)

while True:
    myMotor.drive_forward(0)
    moving_average()
    time.sleep(5)
    myMotor.drive_forward(100)
    time.sleep(5)

