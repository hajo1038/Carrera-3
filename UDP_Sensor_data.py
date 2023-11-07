# This is server code to send video frames over UDP
import socket
import network
import time
import binascii
import sensor
import pyb
from lsm6dsox import LSM6DSOX
from machine import I2C, SPI, Pin


SSID='ESP32' # Network SSID
KEY='12345678'  # Network key

HOST_IP = "192.168.1.3"
UDP_PORT = 4210
MESSAGE = b"Hello, Joni!"
WIDTH=400

BUFF_SIZE = 65536

def connect_to_AP():
    # Init wlan module and connect to network
    print("Trying to connect. Note this may take a while...")
    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()
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


lsm = LSM6DSOX(SPI(5), cs_pin=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)) # initialize acc/gyro
connect_to_AP()

server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # setup socket with UDP
#server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

port = 9999
socket_address = (HOST_IP, port) # own socket adress
server_socket.bind(socket_address)
print('Listening at:',socket_address)

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

img = sensor.snapshot()

while True:
    #start = pyb.micros()
    acc_data = lsm.read_accel()
    gyro_data = lsm.read_gyro()
    #print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*acc_data)))
    #print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*gyro_data))
    #print("")
    scaled_acc_data = [int(data * 100) for data in acc_data]
    scaled_gyro_data = [int(data * 100) for data in gyro_data]
    acc_bytes = [datapoint.to_bytes(4, 'big')for datapoint in scaled_acc_data]
    gyro_bytes = [datapoint.to_bytes(4, 'big')for datapoint in scaled_gyro_data]
    send_buffer = bytearray(b''.join(acc_bytes))
    send_buffer.extend(bytearray(b''.join(gyro_bytes)))
    sensor_data = []
    sensor_data = scaled_acc_data.extend(scaled_gyro_data)
    #print(scaled_acc_data)
    img = sensor.snapshot()
    base64_data = binascii.b2a_base64(img.compress(quality=10))
    print(len(base64_data))
    send_buffer.extend(base64_data)
    #print(len(base64_data))
    server_socket.sendto(send_buffer,("192.168.1.2",4210))
    #msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    #print('GOT connection from ',client_addr)
    #print(pyb.micros() - start)
