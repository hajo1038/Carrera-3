# This is server code to send video frames over UDP
import socket
import network
import time
import binascii
import sensor
import pyb
from lsm6dsox import LSM6DSOX
from machine import I2C, SPI, Pin
import gc
from Motor import Motor

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
    wlan.ifconfig(('192.168.1.2', '255.255.255.0', '192.168.1.1', '192.168.1.1'))
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


#lsm = LSM6DSOX(SPI(5), cs_pin=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)) # initialize acc/gyro
connect_to_AP()

server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # setup socket with UDP
#server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

port = 9999
socket_address = (HOST_IP, port) # own socket adress
#server_socket.bind(socket_address)
#print('Listening at:',socket_address)

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

img = sensor.snapshot()
part_counter = 1
motor = Motor(PWM_frequency=2000)
motor_percentage = 40
while True:
    #start = pyb.micros()
    if motor_percentage < 80:
        motor_percentage += 1
    #motor.drive_forward(motor_percentage)
    img = sensor.snapshot()
    #base64_data = binascii.b2a_base64(img)
    #img.compress()
    test_data = binascii.b2a_base64(img)
    #print(test_data)
    #print(len(binascii.a2b_base64(test_data)))
    img_data = bytearray(binascii.a2b_base64(test_data))

    for part_counter in range(1,5):
            lower_index = int((len(img_data)/4)*(part_counter-1))
            upper_index = int((len(img_data)/4)*(part_counter))
            packet = img_data[lower_index:upper_index]
            packet.extend(part_counter.to_bytes(1,'big'))
            #print(f"{lower_index} : {upper_index}")
            server_socket.sendto(packet,("192.168.1.3",4210))
    #msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    #print('GOT connection from ',client_addr)
    #print(pyb.micros() - start)
