import RPi.GPIO as GPIO
import datetime
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

revolution_time=datetime.datetime.now()

def print_speed(channel):
    global revolution_time
    now = datetime.datetime.now()
    freq = 1/(now - revolution_time).total_seconds()
    rpm = freq / 2 * 60
    revolution_time = now
    print("Current rpm: {:4.0f}".format(rpm), end='\r')


GPIO.add_event_detect(18, GPIO.RISING, callback=print_speed)  # add rising edge detection on a channel

while(True):
    time.sleep(1)