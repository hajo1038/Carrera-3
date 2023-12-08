import math
from IMU import IMU
from Motor import Motor
from hall_sensor import HallSensor
from current_sensor import CurrentSensor
from RGB_LED import RGB_LED
import time
import pyb
import os
from ulab import numpy as np


class KalmanFilter:
    def __init__(self):
        self.x = np.array([0, 0, 0, 0])  # initial state
        self.P = np.eye(4) * 0.0  # initial covariance
        self.Q = np.array([
            [0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1]
        ])  # process noise
        self.R = np.array([
            [100, 0],
            [0, 1]
        ])  # measurement noise
        self.F = np.array([
            [1, 0.005, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0.005],
            [0, 0, 0, 1]
        ])  # state transition matrix
        self.H = np.array([[0, 1, 0, 0], [0, 0, 0, 1]])  # measurement matrix


        self.x = np.array([0, 0])  # initial state
        self.P = np.eye(2) * 0.0  # initial covariance
        self.Q = np.array([[0.1, 0.1], [0.1, 0.1]])  # process noise
        self.R = np.array([100])  # measurement noise
        self.F = np.array([[1, 0.005], [0, 1]])  # state transition matrix
        self.H = np.array([[0, 1]])  # measurement matrix

    def predict(self):
        # Predict state
        self.x = np.dot(self.F, self.x)

        # Predict covariance
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

    def update(self, measurement):
        # Calculate Kalman gain
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(np.dot(np.dot(self.H, self.P), self.H.T) + self.R))

        # Update state
        self.x = self.x + np.dot(K, measurement - np.dot(self.H, self.x))

        # Update covariance
        self.P = self.P - np.dot(np.dot(K, self.H), self.P)


def round_half_up(n, decimals=0):
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier

# Initialize the Kalman filter
kf = KalmanFilter()

AY_THRESH = 2
WINDOW = 4
WHEEL_DIA = 0.0222 # in m (22.2 mm)
PI = 3.14159265359
RADIUS_60 = 0.4
RADIUS_15 = 1.0
MAP_CREATION_ROUNDS = 4
LOGGING = False


acc_v = []
angle = []
angle_acc = []
angle_acc_v = []
mean_angle = []
acc_gyro = []
acc_v_gyro = []
radiuses = []
current_v = 0
current_angle = 0

current_acc_gyro = 0
current_acc_gyro_v = 0
current_acc_angle = 0
current_acc_v_angle = 0

last_time = 0
last_ay = [0, 0, 0, 0]
kf_a = []
kf_v = []
kf_x = []
position = []
kf_gz = []
kf_angle = []
ay_thresh_counter = 0
in_turn = False
turns = []
straights = []
turn_times = []
mean_gyros = []
curve_entry_position = 0
curve_exit_position = 0
curve_entry_angle = 0
gz_count = 0
gz_sum = 0
v_sum = 0
current_position = 0
last_currents = [0.1 , 0.1, 0.1, 0.1]
last_current = 0.1
rounds = 0
round_times = []
rounds_list = []
straights_times = []


myMotor = Motor(200)
myIMU = IMU()
hall_sensor = HallSensor('PG12', 500)
current_sensor = CurrentSensor()
rgb_led = RGB_LED()

# Parameters for step response recording
record_start_time = 100  # mseconds
record_duration = 20000  # mseconds
record_end_time = record_start_time + record_duration

cycle_time = 10000 #microseconds
myMotor.drive_forward(0)
pyb.delay(1000)

print('3...2...1...')
pyb.delay(3000)

start_time = pyb.millis()
cycle_timer = pyb.micros()
standing_still = True
finish_line_detected = False
while True:
    current_time = pyb.millis() - start_time
    if record_start_time < current_time < record_end_time:
        myMotor.drive_forward(40)
        rgb_led.red.value(1)
    if current_time > record_start_time + 1000:
        standing_still = False
    #elif current_time >= record_end_time:
    #    myMotor.drive_forward(0)
    #    break

    if (pyb.micros() - cycle_timer) >= cycle_time:
        dt = (pyb.micros() - cycle_timer) / 1_000_000
        rpm = hall_sensor.get_rpm_filtered()
        v_rpm = (rpm/60)*PI*WHEEL_DIA

        acc_xy = myIMU.read_acc_xyz()
        gyro_z = myIMU.read_gyro_z()

        current_sensor.update_current_average()
        avg_current = current_sensor.get_averaged_current()

        cycle_timer = pyb.micros()

        #last_currents[0:3] = last_currents[1:]
        #last_currents[3] = avg_current

        if not standing_still and last_current < 50 and avg_current > 50:
            finish_line_detected = True
        elif not standing_still and last_current > 50 and avg_current > 50:
            finish_line_detected = False
        last_current = avg_current

        kf.F = np.array([
            [1, dt],
            [0, 1]
        ])
        kf.predict()
        # measurement = np.array(v)
        kf.update(np.array([v_rpm]))
        current_angle += gyro_z * dt

        # wenn drehrate über Grenzwert
        if gyro_z >= 50 or gyro_z <= -50:
            # wenn am Kurveneingang, die Position und Winkel speichern und Länge der vorherigen Geraden speichern
            if not in_turn and (kf.x[0] - curve_exit_position) > 0.1:
                in_turn = True
                # curve_entry_angle = current_mean_angle
                curve_entry_angle = current_angle
                curve_entry_time = pyb.millis() - start_time
                curve_entry_position = kf.x[0]
                straights_times.append((pyb.millis() - start_time)/1000)
                straights.append(curve_entry_position - curve_exit_position)
            # wenn in der Kurve Gyro und Geschwindigkeitswerte sammeln um mittlere Werte zu ermitteln
            else:
                gz_count += 1
                gz_sum += gyro_z
                v_sum += kf.x[1]

        else:
            # Wenn am Kurvenausgang den Radius der Kurve mittels mittlerer Geschwindigkeit und Drehrate berechnen
            if in_turn:
                in_turn = False
                curve_exit_position = kf.x[0]
                curve_exit_time = pyb.millis() - start_time
                if math.fabs(current_angle - curve_entry_angle) < 5:
                    pass
                else:
                    turn_times.append((curve_exit_time - curve_entry_time) / 1000)
                    # turn_length = curve_exit_position - curve_entry_position
                    # radius_angle = (turn_length / radius) * (180 / PI) # get the angle through the length of the turn
                    # Berechnung des Kurvenwinkels
                    # turn = [current_mean_angle - curve_entry_angle, curve_exit_position - curve_entry_position]
                    turn = [current_angle - curve_entry_angle, curve_exit_position - curve_entry_position]
                    turns.append(turn)
                    mean_v = v_sum / gz_count
                    mean_gz = gz_sum / gz_count
                    mean_gyros.append(mean_gz)
                    # print(mean_gz)
                    radius = mean_v / (mean_gz * (PI / 180))
                    # Überprüfen ob Radius zu 60° oder 15° Kurve passt
                    if math.fabs(radius - RADIUS_60) < math.fabs(radius - RADIUS_15):
                        radius = RADIUS_60
                    else:
                        radius = RADIUS_15
                    radiuses.append(radius)
            elif finish_line_detected:
                rounds += 1
                round_times.append((pyb.millis() - start_time)/1000)

                straights.append(kf.x[0] - curve_exit_position)
                curve_exit_position = kf.x[0]
                rounds_list.append([turns, straights])
                print("Ziel")
                turns = []
                straights = []
                if rounds == MAP_CREATION_ROUNDS:
                    myMotor.drive_forward(0)
                    rgb_led.green.value(1)
                    rgb_led.red.value(0)
                    rgb_led.blue.value(0)
                    break

file_counter = 0
file_path = f'map_data_{file_counter}.txt'
while file_path in os.listdir():
    file_counter += 1
    file_path = f'map_data_{file_counter}.txt'


with open(file_path, 'w') as file:
    # Write header

    # file.write("Time (ms), acc_x, acc_y, acc_z, gyro_z, rpm, rpm_unfiltered, current, avg_current\n")
    #file.write("turn_angle, turn_length, straight\n")
    #if len(turns) > len(straights):
    #    straights += [''] * (len(turns) - len(straights))
    #elif len(straights) > len(turns):
    #    turns += [['','']] * (len(straights) - len(turns))
    #print(turns)
    #print(len(turns))
    #print(straights)
    #print(len(straights))
    #for turn, straight, straight_time in zip(turns, straights, straights_times):
    #    file.write(f"{turn[0]}, {turn[1]}, {straight}, {straight_time}\n")
    round_straights= []
    round_turn_angles = []
    file.write(f"Number of rounds: {rounds}\n")
    file.write(f"{round_times}\n")
    for round_count, single_round in enumerate(rounds_list):
        file.write(f"----Runde {round_count+1}------\n")
        file.write(f"Kurven: {single_round[0]}\tGeraden: {single_round[1]}\n")
        round_straights.append(single_round[1])
        round_turn_angle = [curves[0] for curves in single_round[0]]
        round_turn_angles.append(round_turn_angle)

    avg_straights = np.mean(np.array(round_straights), axis=0).tolist()
    avg_turn_angles = np.mean(np.array(round_turn_angles), axis=0).tolist()
    file.write(f"\n----Durchschnittsrunde------\n")
    file.write(f"Kurven: {avg_turn_angles}\tGeraden: {avg_straights}\n")

print("Finish")

if LOGGING:
    file_counter = 0
    file_path = f'race_measurement_{file_counter}.txt'
    while file_path in os.listdir():
        file_counter += 1
        file_path = f'race_measurement_{file_counter}.txt'
    log_file = open(file_path, "w")
    log_file.write("Time (ms), acc_x, acc_y, acc_z, gyro_z, rpm, position, avg_current, kf_x, kf_v\n")



pyb.delay(2000)

turn_id = 0
straight_id = 0
first_turn = True
cycle_timer = pyb.micros()
rgb_led.green.value(0)
rgb_led.red.value(0)
rgb_led.blue.value(1)
position = 0
start_time = pyb.micros()
while(True):
    current_straight = avg_straights[straight_id]
    next_turn = avg_turn_angles[turn_id]


    if (pyb.micros() - cycle_timer) >= cycle_time:
        dt = (pyb.micros() - cycle_timer) / 1_000_000
        rpm = hall_sensor.get_rpm_filtered()
        v_rpm = (rpm/60)*PI*WHEEL_DIA
        position += v_rpm*dt

        acc_xy = myIMU.read_acc_xyz()
        gyro_z = myIMU.read_gyro_z()

        current_sensor.update_current_average()
        avg_current = current_sensor.get_averaged_current()

        cycle_timer = pyb.micros()

        #last_currents[0:3] = last_currents[1:]
        #last_currents[3] = avg_current

        if not first_turn and last_current < 50 and avg_current > 50:
            finish_line_detected = True
        elif not first_turn and last_current > 50 and avg_current > 50:
            finish_line_detected = False
        last_current = avg_current

        kf.F = np.array([
            [1, dt],
            [0, 1]
        ])
        kf.predict()
        # measurement = np.array(v)
        kf.update(np.array([v_rpm]))
        current_angle += gyro_z * dt
        if LOGGING:
            log_file.write(f"{start_time + dt},{acc_xy[0]},{acc_xy[1]},{acc_xy[2]},{gyro_z},{rpm},{position},{avg_current},{kf.x[0]},{kf.x[1]}\n")
        # Vor erster Kurve langsam fahren
        if first_turn:
            myMotor.drive_forward(40)
        else:
            distance_to_turn = current_straight - kf.x[0]
            if in_turn:
                myMotor.drive_forward(40)
                rgb_led.blue.value(0)
                rgb_led.green.value(1)
                rgb_led.red.value(0)
            elif distance_to_turn < 0.3:
                rgb_led.blue.value(0)
                rgb_led.green.value(0)
                rgb_led.red.value(1)
                myMotor.drive_forward(10)
            else:
                rgb_led.blue.value(1)
                rgb_led.green.value(0)
                rgb_led.red.value(0)
                myMotor.drive_forward(50)

        # wenn drehrate über Grenzwert
        if gyro_z >= 50 or gyro_z <= -50:
            # wenn am Kurveneingang, die Position und Winkel speichern und Länge der vorherigen Geraden speichern
            #if not in_turn and (kf.x[0] - curve_exit_position) > 0.1:
            if not in_turn:
                in_turn = True
                # Wenn es die erste Kurve ist wird die Strecke vor und nach Start/Ziel zusammengefasst
                if first_turn:
                    first_turn = False
                    avg_straights[0] = avg_straights[0] + avg_straights.pop(-1)
        else:
            # Wenn am Kurvenausgang den Radius der Kurve mittels mittlerer Geschwindigkeit und Drehrate berechnen
            if in_turn:
                in_turn = False
                kf.x[0] = 0
                position = 0

                turn_id = (turn_id + 1)%len(avg_turn_angles)
                straight_id = (straight_id + 1)%len(avg_straights)

                #curve_exit_position = kf.x[0]
                #curve_exit_time = pyb.millis() - start_time


