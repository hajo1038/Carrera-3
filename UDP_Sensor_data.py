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
from hall_sensor import HallSensor
from current_sensor import CurrentSensor


SSID='ESP32' # Network SSID
KEY='12345678'  # Network key

HOST_IP = "192.168.1.2"
UDP_PORT = 4210
MESSAGE = b"Hello, Joni!"
WIDTH=400

BUFF_SIZE = 65536

#create objects
hall_sensor = HallSensor('PE14', 500) #Pin PE14, 500ms Timeout
current_sensor = CurrentSensor()
myMotor = Motor(2000)


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

LED3 = Pin("PE12", Pin.OUT_PP)
LED3.value(0)


lsm = LSM6DSOX(SPI(5), cs_pin=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)) # initialize acc/gyro
# -----connect_to_AP()

server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # setup socket with UDP

port = 9999
# socket_address = (HOST_IP, port) # own socket adress
# server_socket.bind(socket_address)
# print('Listening at:',socket_address)

clock = time.clock()                # Create a clock object to track the FPS.
start = pyb.millis()

myMotor.drive_forward(0)

while True:
    rpm_unfiltered = int(hall_sensor.get_rpm_unfiltered())
    rpm_filtered = int(hall_sensor.get_rpm_filtered())
    current_averaged = int(current_sensor.get_averaged_current()*1000)

    acc_data = lsm.read_accel()
    gyro_data = lsm.read_gyro()
    #print('Accelerometer: x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*acc_data)))
    #print('Gyroscope:     x:{:>8.3f} y:{:>8.3f} z:{:>8.3f}'.format(*gyro_data))
    #print("")
    # convert the data to int
    scaled_acc_data = [int(data * 100) for data in acc_data[0:2]]
    #scaled_gyro_data = [int(data * 100) for data in gyro_data]
    scaled_gyro_z = int(gyro_data[2] * 100)
    # convert data to bytes
    acc_bytes = [datapoint.to_bytes(4, 'big')for datapoint in scaled_acc_data]
    #gyro_bytes = [datapoint.to_bytes(4, 'big')for datapoint in scaled_gyro_data]
    gyro_z_bytes = scaled_gyro_z.to_bytes(4,'big')
    rpm_unfiltered_bytes = int(rpm_unfiltered).to_bytes(4,'big')
    rpm_filtered_bytes = int(rpm_filtered).to_bytes(4,'big')
    current_averaged_bytes = int(current_averaged).to_bytes(4,'big')


    send_buffer = bytearray(b''.join(acc_bytes))
    #send_buffer.extend(bytearray(b''.join(gyro_bytes)))
    send_buffer.extend(bytearray(gyro_z_bytes))
    send_buffer.extend(bytearray(rpm_unfiltered_bytes))
    send_buffer.extend(bytearray(rpm_filtered_bytes))
    send_buffer.extend(bytearray(current_averaged_bytes))


    if (hall_sensor.averaged_current_flag == True):
        current_sensor.update_current_average()
        averaged_current_flag = False

    # ----- debug
    print(f"non filtered RPM: {rpm_unfiltered}")
    print(f"filtered rpm : {rpm_filtered}")
    print(f"filtered current : {current_averaged}")

    time.sleep(0.1)
    # -----server_socket.sendto(send_buffer,("192.168.1.2",4210))
    #msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    #print('GOT connection from ',client_addr)
    #print(pyb.micros() - start)
