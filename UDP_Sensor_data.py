# This is server code to send video frames over UDP
import socket
import network
import time
import binascii
import sensor
import pyb
from lsm6dsox import LSM6DSOX
from machine import I2C, SPI, Pin
from Motor import Motor


SSID='ESP32' # Network SSID
KEY='12345678'  # Network key

HOST_IP = "192.168.1.3"
UDP_PORT = 4210
MESSAGE = b"Hello, Joni!"
WIDTH=400

BUFF_SIZE = 65536

def hall_ISR(pin):
    #start = pyb.micros()
    global currentMicros, lastMicros, rpmMeasured, readingsIndex, moving_average
    currentMicros = time.ticks_us()
    rpmMeasured = int(60000000/(4*(currentMicros-lastMicros)))
    #print(rpmMeasured)
    lastMicros = currentMicros
    readings[readingsIndex] = rpmMeasured
    readingsIndex = (readingsIndex + 1) % windowSize  # Circular buffer
    moving_average = sum(readings)/windowSize
    time_diff = pyb.micros() - start
    #print("Pyb: ", time_diff)
    #print("")
    #print("Current RPM:", rpmMeasured)
    #print("Moving Average RPM:", moving_average)

def moving_average():
    global readingsIndex
    readings[readingsIndex] = rpmMeasured
    readingsIndex = (readingsIndex + 1) % windowSize  # Circular buffer
    moving_average = sum(readings)/windowSize
    print("Current RPM:", rpmMeasured)
    #print("Moving Average RPM:", moving_average)
    return moving_average

def connect_to_AP():
    # Init wlan module and connect to network
    print("Trying to connect. Note this may take a while...")
    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()
    #wlan.ifconfig(('192.168.1.2', '255.255.255.0', '192.168.1.1', '192.168.1.1'))
    wlan.active(True)
    connection_counter = 1
    while not wlan.isconnected():
        try:
            print("Try ", connection_counter)
            wlan.connect(SSID, KEY, timeout=30000)
        except OSError:
            connection_counter += 1
            wlan.active(False)
            wlan.deinit()
            wlan.active(True)
    # We should have a valid IP now via DHCP
    print("WiFi Connected ", wlan.ifconfig())
    LED3.value(1)

hallSensorPin = Pin('PE14', Pin.IN)
LED3 = Pin("PE12", Pin.OUT_PP)
LED3.value(0)

#variables for rpm measurement
curenntMicros = 0
lastMicros = 0
rpmMeasured = 0

#moving average
moving_average= 0

windowSize = 4
avgSum = 0
readings = [0] * windowSize #initialize the readings array with zeros
readingsIndex = 0

lsm = LSM6DSOX(SPI(5), cs_pin=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)) # initialize acc/gyro
connect_to_AP()

server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # setup socket with UDP

port = 9999
# socket_address = (HOST_IP, port) # own socket adress
# server_socket.bind(socket_address)
# print('Listening at:',socket_address)

#configures an interrupt for hallSensorPin
#triggers interrupt when Pin changes from LOW to HIGH (rising edge)
#handler calls the function hall_ISR
hallSensorPin.irq(trigger=Pin.IRQ_RISING, handler=hall_ISR)
myMotor = Motor(2000)

clock = time.clock()                # Create a clock object to track the FPS.
start = pyb.millis()
motor_on = False
while True:
    #myMotor.drive_forward(100)
    #start = pyb.millis()
    #if pyb.millis() - start > 750 and motor_on:
    #    start = pyb.millis()
        #rpmMeasured = 0
        #moving_average = 0
    #    myMotor.drive_forward(0)
    #    motor_on = False
    #elif pyb.millis() - start > 5000 and not motor_on:
    #    start = pyb.millis()
    #    myMotor.drive_forward(100)
    #    motor_on = True
    rpm_average = int(moving_average)
    acc_data = lsm.read_accel()
    gyro_data = lsm.read_gyro()
    #print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*acc_data)))
    #print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*gyro_data))
    #print("")
    # convert the data to int
    scaled_acc_data = [int(data * 100) for data in acc_data]
    #scaled_gyro_data = [int(data * 100) for data in gyro_data]
    scaled_gyro_z = int(gyro_data[2] * 100)
    # convert data to bytes
    acc_bytes = [datapoint.to_bytes(4, 'big')for datapoint in scaled_acc_data]
    #gyro_bytes = [datapoint.to_bytes(4, 'big')for datapoint in scaled_gyro_data]
    gyro_z_bytes = scaled_gyro_z.to_bytes(4,'big')
    rpm_measured_bytes = int(rpmMeasured).to_bytes(4,'big')
    rpm_average_bytes = rpm_average.to_bytes(4,'big')

    send_buffer = bytearray(b''.join(acc_bytes))
    #send_buffer.extend(bytearray(b''.join(gyro_bytes)))
    send_buffer.extend(bytearray(gyro_z_bytes))
    send_buffer.extend(bytearray(rpm_measured_bytes))
    send_buffer.extend(bytearray(rpm_average_bytes))

    server_socket.sendto(send_buffer,("192.168.1.2",4210))
    #msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    #print('GOT connection from ',client_addr)
    #print(pyb.micros() - start)
