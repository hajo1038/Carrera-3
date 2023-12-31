from machine import Pin
import time

class HallSensor:
    def __init__(self, hall_pin, timeout_ms=500):
        self.hall_pin = Pin(hall_pin, Pin.IN)
        self.hall_pin.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING, handler=self.hall_ISR)

        self.current_micros = 0
        self.last_micros = 0
        self.rpm_unfiltered = 0
        self.rpm_filtered = 0

        self.counter = 0

        self.windows_size = 4
        self.avg_sum = 0
        self.readings = [0] * self.windows_size
        self.reading_index = 0
        self.timeout_ms = timeout_ms
        self.last_pulse_time = time.ticks_ms()  # Initialize with the current time
        self.averaged_current_flag = False # Flag gets checked in main and triggers moving average current
        print("Hall Sensor erstellt")

    def hall_ISR(self, pin):
        self.current_micros = time.ticks_us()
        #print(self.current_micros - self.last_micros)
        if self.current_micros - self.last_micros < 500:
            pass
        else:
            self.rpm_unfiltered = int(60000000 / (12 * (self.current_micros - self.last_micros))) # durch 12 da 6 Löcher und Risung und Falling Edge
            self.counter += 1
            #print(self.counter)
            #print(self.current_micros - self.last_micros)
            self.last_micros = self.current_micros
            #print(time.ticks_ms() - self.last_pulse_time)
            self.last_pulse_time = time.ticks_ms()  # Update with the current time
            self.readings[self.reading_index] = self.rpm_unfiltered
            self.reading_index = (self.reading_index + 1) % self.windows_size
            self.rpm_filtered = int(sum(self.readings) / (self.windows_size))
            self.averaged_current_flag = True
        #print(self.rpm_filtered)
        #print(time.ticks_us() - self.current_micros)

    def get_rpm_unfiltered(self):
        # Check for a timeout and reset RPM if necessary
        current_time = time.ticks_ms()
        if (current_time - self.last_pulse_time) > self.timeout_ms:
            self.rpm_unfiltered = 0
        return self.rpm_unfiltered


    def get_rpm_filtered(self):
        current_time = time.ticks_ms()
        if (current_time - self.last_pulse_time) > self.timeout_ms:
            self.rpm_filtered = 0

        return self.rpm_filtered
