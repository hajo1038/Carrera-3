# This is server code to send video frames over UDP
from Network import Network
import time
import binascii
import sensor
import pyb
from lsm6dsox import LSM6DSOX
from machine import I2C, SPI, Pin
import gc
from Motor import Motor

LED3 = Pin("PE12", Pin.OUT_PP)
LED3.value(0)

my_network = Network()  # connect to wlan and create udp socket

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

img = sensor.snapshot()

part_counter = 1
motor = Motor(PWM_frequency=200)
motor_percentage = 40
LED3.value(1)
while True:
    #start = pyb.micros()
    if motor_percentage < 80:
        motor_percentage += 1
    #motor.drive_forward(motor_percentage)
    img = sensor.snapshot()
    #base64_data = binascii.b2a_base64(img)
    #start = pyb.micros()
    img.compress()
    #print(pyb.micros() - start)
    test_data = binascii.b2a_base64(img)
    #print(len(binascii.a2b_base64(test_data)))
    img_data = bytearray(binascii.a2b_base64(test_data))
    try:
        network.send_packet(img_data,("192.168.1.2",4210))
    except:
        LED3.value(0)
    #print(img_data)
    # for part_counter in range(1,5):
    #         lower_index = int((len(img_data)/4)*(part_counter-1))
    #         upper_index = int((len(img_data)/4)*(part_counter))
    #         packet = img_data[lower_index:upper_index]
    #         packet.extend(part_counter.to_bytes(1,'big'))
            #print(f"{lower_index} : {upper_index}")
            # server_socket.sendto(packet,("192.168.1.2",4210))
    #msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    #print('GOT connection from ',client_addr)
    #print(pyb.micros() - start)
