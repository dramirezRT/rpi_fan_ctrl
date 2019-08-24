import os.path as op
import numpy as np
import re

# Default values if not configured
RPI_CTRL_PIN=21         # BCM control pin number
FAN_JMP_START_MIN=50    # Minimum to get the fan spinning (%)
FAN_MIN=20              # Minimun to get the fan spinning (%)
REFRESH_RATE=1          # How often fan speep is updated (s)
PWM_FREQ=25             # Signal frequency (Hz)
HYSTERESIS=1            # Readings to average the temperature and avoid sudden speed changes

"""
    Reading from file. Gets the format of:
    [   [Temp1 (C), Fan Percentage1 (%)],
        [Temp2 (C), Fan Percentage2 (%)],
        ...
        ...
    ]

    Default is a linear approach
"""
FAN_SPEED_MAP=[ [50, 40], [70, 100] ]

cfgDir = op.dirname(__file__)
with open (op.join(cfgDir, 'fan.cfg'), 'r') as f:
    for line in f.readlines():

        regex = "([\w|_]+)\s*=\s*(\d+)|([\w|_]+)\s*=\s*(\[\s*[\[\d+,\s*\d+\],{0,1}]+\s*\])"
        if ( re.match(regex, line) ):
            groups = re.match(regex, line).groups()
            if (groups[0] == "RPI_CTRL_PIN"):
                RPI_CTRL_PIN = int(groups[1])
            elif (groups[0] == "FAN_JMP_START_MIN"):
                FAN_JMP_START_MIN = int(groups[1])
            elif (groups[0] == "FAN_MIN"):
                FAN_MIN = int(groups[1])
            elif (groups[0] == "REFRESH_RATE"):
                REFRESH_RATE = int(groups[1])
            elif (groups[0] == "PWM_FREQ"):
                PWM_FREQ = int(groups[1])
            elif (groups[0] == "HYSTERESIS"):
                HYSTERESIS = int(groups[1])
            elif (groups[2] == "FAN_SPEED_MAP"):
                FAN_SPEED_MAP = []
                map = groups[3].replace('[', '').replace(']', '').replace(' ', '').split(',')
                tmpMap = np.reshape(map, (len(map) // 2, 2))
                for pair in tmpMap:
                    tmpPair = []
                    for value in pair:
                        tmpPair.append(float(value))
                    FAN_SPEED_MAP.append(tmpPair)


def variable_disclose ():
    print("RPI_CTRL_PIN: %d" % RPI_CTRL_PIN)
    print("FAN_JMP_START_MIN: %d" % FAN_JMP_START_MIN)
    print("FAN_MIN: %d" % FAN_MIN)
    print("REFRESH_RATE: %d" % REFRESH_RATE)
    print("PWM_FREQ: %d" % PWM_FREQ)
    print("HYSTERESIS: %d" % HYSTERESIS)
    print("FAN_SPEED_MAP: %s" % FAN_SPEED_MAP)
    
variable_disclose()