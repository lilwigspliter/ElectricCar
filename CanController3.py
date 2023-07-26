#Zach Eggeman
#Xander Elea


import RPi.GPIO as GPIO
import can
import time
import os
from evdev import InputDevice, categorize, ecodes
import bluetooth
import sys
import math
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)
GPIO.setup(19, GPIO.OUT)
GPIO.output(19,0)

count = 0
oldRangeMin = 0
oldRangeMax = 42781248 #100% duty cycle
newRangeMin = 0
newRangeMax = 65535 #range of FFFF
propValue = 32512
steeringAngleValue = 32512
dataBuffer = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
messageCount = 0
controller_found = 0


#Range A to range B conversion using linear conversion
def rangeArangeB(oldValue,oldMax,oldMin,newMax,newMin):
    newValue = ((oldValue-oldMin)/(oldMax-oldMin))*(newMax-newMin)+newMin
    return newValue

#Packages an integer value into a 1 byte hex chunk for signal transmission
def hexPackageManager(intValue):
    i = 4
    a = []
    b = []
    if (intValue > 3932.1):
        while i > 0:
            a.append(hex(int(intValue))[-i])
            i-=1
        b = [a[0]+a[1],a[2]+a[3]]
    else:
        b = ['0','0']
    return b

def connect_controller(channel):
    print("Connecting to Bluetooth Controller")
    with open(r'/proc/bus/input/devices','r') as fp:
        lines = fp.readlines()
        device_count = 0
        for row in lines:
            mac = 'e4:17:d8:53:79:79'
            if row.find(mac) != -1:
                print('Controller Found!')
                device_count = 1
                mac_line = lines.index(row)
                handle_line = mac_line+3
                handle = lines[handle_line]
                split_handle = handle.split("event")
                second = split_handle[1]
                event = second.split()
                event_number = event[0]
                controller_handle = "/dev/input/event" + event_number
    controller = InputDevice(controller_handle)
    print(controller)

def update_message(channel):
    st = time.process_time()
    print("Updating Message")
    #propValue = int(input('Enter Propulsion Integer: ')) 
    #prop = rangeArangeB(propValue,oldRangeMax,oldRangeMin,newRangeMax,newRangeMin)
    print(propValue)
    prop = propValue
    propH = hexPackageManager(prop)[0]
    propL = hexPackageManager(prop)[1]
    prop_ec_H = propH
    prop_ec_L = propL
    #steeringAngleValue = int(input('Enter Steering Angle Integer: '))
    #steeringAngle = rangeArangeB(steeringAngleValue,oldRangeMax,oldRangeMin,newRangeMax,newRangeMin)
    print(steeringAngleValue)
    steeringAngle = steeringAngleValue
    #print(steeringAngleValue)
    steeringAngle_H = hexPackageManager(steeringAngle)[0]
    steeringAngle_L = hexPackageManager(steeringAngle)[1]
    steeringAngle_ec_H = steeringAngle_H
    steeringAngle_ec_L = steeringAngle_L
    dataBuffer = [int(propH,16),int(propL,16),int(prop_ec_H,16),int(prop_ec_L,16),int(steeringAngle_H,16),int(steeringAngle_L,16),int(steeringAngle_ec_H,16),int(steeringAngle_ec_L,16)]
    msg = can.Message(arbitration_id=0x123,data=dataBuffer,is_extended_id=True)
    GPIO.output(19,False)
    bus.send(msg)
    time.sleep(0.1)
    GPIO.output(led,True)
    print("Message Sent")
    et = time.process_time()
    res = et-st
    res = res*(10**3)
    #print("Execution Time: ", res, "m-Seconds")
        
        
GPIO.add_event_detect(6, GPIO.RISING, callback=update_message, bouncetime=100)

GPIO.add_event_detect(26, GPIO.FALLING, callback=connect_controller, bouncetime=100)

while (controller_found == 0):
    with open(r'/proc/bus/input/devices','r') as fp:
        lines = fp.readlines()
        for row in lines:
            mac = 'e4:17:d8:53:79:79'
            if row.find(mac) != -1:
                print("Success")
                time.sleep(5)
                controller_found = 1
            else:
                print("Connect Controller")
    fp.close()


print('Bring up CAN0 bus')

# Bring up can0 interface at 500kbps
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
time.sleep(0.1)
print('Press CTRL+C to exit')

try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
except OSError:
    print('CAN0 bus fault, board not connected.')
    GPIO.output(led,False)
    exit()

with open(r'/proc/bus/input/devices','r') as fp:
    lines = fp.readlines()
    device_count = 0
    for row in lines:
        mac = 'e4:17:d8:53:79:79'
        if row.find(mac) != -1:
            print('Controller Found!')
            device_count = 1
            mac_line = lines.index(row)
            handle_line = mac_line+3
            handle = lines[handle_line]
            split_handle = handle.split("event")
            second = split_handle[1]
            event = second.split()
            event_number = event[0]
            controller_handle = "/dev/input/event" + event_number
    controller = InputDevice(controller_handle)

# Main loop
Loop = True
while Loop:
    try:
        for event in controller.read_loop():
            GPIO.output(19,0)
            if event.type == 3:
                if event.code == 0:
                    steeringAngleValue = int(event.value)
                    #print(steeringAngleValue)
                    GPIO.output(19,1)
                    #time.sleep(0.1)
                elif event.code == 1:
                    propValue = int(event.value)
                    #print(propValue)
                    GPIO.output(19,1)
                    #time.sleep(0.1)
    except KeyboardInterrupt:
        #Catch keyboard interrupt
        GPIO.output(led,False)
        GPIO.cleanup()
        print('\n\rKeyboard interrtupt')
        Loop = False
    except ValueError:
        GPIO.output(led,False)
        print('\n\rValue below buffer minimum')
    except OSError:
        print('CAN0 bus fault')
        GPIO.output(led,False)
        GPIO.cleanup()
        Loop = False

os.system("sudo /sbin/ip link set can0 down")
GPIO.cleanup()
