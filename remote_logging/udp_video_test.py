# This is client code to receive video frames over UDP
import cv2,socket
import numpy as np
import time
import base64

LABEL = "finish"
BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '192.168.1.3'
client_socket.bind((host_ip, 4210))
print(host_ip)

frame_data = np.zeros([])
initial = True
err_counter = 0
last_value = -1
image_counter = 0
while True:
	packet,_ = client_socket.recvfrom(BUFF_SIZE)
	#data = base64.b64decode(packet,' /')
	npdata = np.frombuffer(packet, dtype=np.uint8)
	if initial and npdata[-1] == 1:
		last_value = npdata[-1]
		initial = False
		frame_data = npdata[0:-1]

	elif initial:
		continue

	elif last_value == 4 and npdata[-1] == 1:
		frame_data = npdata[0:-1]

	elif npdata[-1] - last_value == 1:
		frame_data = np.append(frame_data, npdata[0:-1])
		if npdata[-1] == 4:
			frame_data_reshape = np.reshape(frame_data, (120, 160))
			cv2.imshow("RECEIVING VIDEO", frame_data_reshape)
			cv2.imwrite(f"{LABEL}_{image_counter}.jpg", frame_data_reshape)
			image_counter += 1
			key = cv2.waitKey(1) & 0xFF
			if key == ord('q'):
				client_socket.close()
				break
	else:
		err_counter += 1
		print("-----------FEHLER-------------")
		print(err_counter)
		initial = True
		last_value = -1

	last_value = npdata[-1]