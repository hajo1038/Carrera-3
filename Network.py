# Untitled - By: jonathanhaller - Sa. Nov. 11 2023
import socket
import network

class Network:
    def __init__(self):
        # the constructor tries to connect to the ESP WLAN and creates a UDP socket
        SSID='ESP32' # Network SSID
        KEY='12345678'  # Network key

        HOST_IP = "192.168.1.3"
        RECEIVER_IP = "192.168.1.2"
        UDP_PORT = 4210

        BUFF_SIZE = 65536

        print("Trying to connect. Note this may take a while...")
        self.wlan = network.WLAN(network.STA_IF)
        #wlan.ifconfig(('192.168.1.2', '255.255.255.0', '192.168.1.1', '192.168.1.1'))
        self.wlan.deinit()
        self.wlan.active(True)
        connection_counter = 1
        while not self.wlan.isconnected():
            try:
                print("Try ", connection_counter)
                self.wlan.connect(SSID, KEY, timeout=30000)
            except OSError:
                connection_counter += 1
                self.wlan.active(False)
                self.wlan.deinit()
                self.wlan.active(True)
        # We should have a valid IP now via DHCP
        print("WiFi Connected ", self.wlan.ifconfig())
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        print("Created UDP socket")


    def send_packet(self, packet, address):
        self.server_socket.sendto(packet, address)
