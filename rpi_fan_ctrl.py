import RPi.GPIO as GPIO
import datetime
import time
import os
import re
import rpi_fan_config as rfc

scriptDir = os.path.dirname(__file__)

cpuTemps = [0] * rfc.HYSTERESIS
gpuTemps = [0] * rfc.HYSTERESIS

GPIO.setmode(GPIO.BCM)
GPIO.setup(rfc.RPI_CTRL_PIN, GPIO.OUT, initial=GPIO.LOW)
fan = GPIO.PWM(rfc.RPI_CTRL_PIN, rfc.PWM_FREQ)

if(rfc.PWM_NUM_PINS == 4):
    rpm = 0
    GPIO.setup(rfc.RPI_SENSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    revolution_time=datetime.datetime.now()
    def updateRpm(pin):
        global revolution_time, rpm
        now = datetime.datetime.now()
        freq = 1/(now - revolution_time).total_seconds()
        rpm = freq / 2 * 60
        revolution_time = now
        # print("Current rpm: {}".format(rpm), end='\r')
    GPIO.add_event_detect(rfc.RPI_SENSE_PIN, GPIO.RISING, callback=updateRpm)  # add rising edge detection on a channel
fan.start(0)


"""
Gets the average temperature from the samples
"""
def getHystTemp(temps):
    return round(sum(temps) / rfc.HYSTERESIS, 1)
"""
Gets the highest values between CPU and GPU
"""
def getMITemp():
    return max(getHystTemp(gpuTemps), getHystTemp(cpuTemps))
"""
Calculates the Fan Percentage based in the provided points
in the cfg file
"""
def getFanPct(temp):
    p1 = (0,0)
    p2 = (0,0)

    for pair in rfc.FAN_SPEED_MAP:
        # if(temp < pair[0] and p1 == (0,0)):
        #     break
        if(temp < pair[0]):
            p2 = pair
            break
        p1 = pair
    # if(p1 == (0,0)): return 0 # Turn fan off

    # Linear approach between two points
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p2[1] - m*p2[0]
    y = (m*temp + b)
    return y if (y <= 100) else 100
"""
Jump starts the fan from off state
"""
def jumpStart():
    #print("Boosting the fan")
    fan.ChangeDutyCycle(rfc.FAN_JMP_START_MIN)
    time.sleep(2)
"""
Gets the current CPU temperature
"""
def getCPUtemp():
    cpuTempFile = "/sys/class/thermal/thermal_zone0/temp"
    with open(cpuTempFile, 'r') as f:
        temp = f.readline()
    return round(int(temp) / 1000, 1)
"""
Gets the current GPU temperature
"""
def getGPUtemp():
    cmd = "/opt/vc/bin/vcgencmd measure_temp"
    gpuTemp = os.popen(cmd).readline()
    temp = re.match("temp=(\d+.\d*)", gpuTemp).group(1)
    return round(float(temp), 1)

def log(temp, speed, rpm):
    with open (os.path.join(scriptDir, 'fan_status'), 'w') as f:
        if(rfc.PWM_NUM_PINS == 4):
            f.write("Current fan speed is: {:3.1f}% @ {:4.0f}rpm <---> Current MITemp is: {:3.1f}\n".format(speed,
                    rpm if speed != 0 else 0, temp))
        else:
            f.write("Current fan speed is: {:3.1f}\% <---> Current MITemp is: {:3.1f}\n".format(speed, temp))

def main():
    curFanSpeed = 0
    try:
        while (True):
            cpuTemps.pop(0) ; cpuTemps.append(getCPUtemp())
            gpuTemps.pop(0) ; gpuTemps.append(getGPUtemp())
            #print("cpuTemps: {}".format(cpuTemps))
            #print("gpuTemps: {}".format(gpuTemps))

            curTemp = getMITemp()
            newFanSpeed = getFanPct(curTemp)
            if(curFanSpeed < rfc.FAN_MIN and newFanSpeed > rfc.FAN_MIN): jumpStart()
            if(newFanSpeed > rfc.FAN_MIN):
                curFanSpeed = newFanSpeed
                fan.ChangeDutyCycle(curFanSpeed)
            else:
                curFanSpeed = 0
                fan.ChangeDutyCycle(curFanSpeed)
            log(curTemp, curFanSpeed, rpm)
            #print("Current fan speed is: {:3.1f} --- Current MITemp is: {:3.1f}".format(curFanSpeed, curTemp), end='\r')

            time.sleep(rfc.REFRESH_RATE)
    finally:
        GPIO.cleanup()

if __name__=='__main__':
    rfc.variable_disclose()
    main()
