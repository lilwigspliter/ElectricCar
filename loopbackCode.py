import RPi.GPIO as GPIO
import can
import time
import os

# This defines the GPIO pin for the LED 
led = 22

"""
I took this section from the Simple Tx file
This section sets up the GPIO mode and configuration for the LED.
but I'm not sure if I should also need to include the canctrl register or not.
"""
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, True)

# Initalize the count variable
count = 0

print('\n\rCAN Rx loopback test')

try:
    # This will initialize the CAN bus rather than initializing it separately 
    bus = can.interface.Bus(channel='can0', bustype='socketcan')

    # Let's me know that something is wrong with the CAN Bus or the connection to PiCAN
except OSError:
    print('Cannot find PiCAN board.')
    GPIO.output(led, False)
    exit()

print('Press CTL-C to exit')

# Main loop section
try:
    while True:
        GPIO.output(led, True)

        # Create CAN message to send
        msg = can.Message(arbitration_id=0x7de, data=[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, count & 0xff])
        bus.send(msg)

        # Increase count and wait
        count += 1
        time.sleep(0.1)

        # Turns off the LED
        GPIO.output(led, False)
        time.sleep(0.1)
        print(count)

        # Receive loopback message
        rx_msg = bus.recv(timeout=1.0)
        if rx_msg is not None:
            # Extract and process specific data from the received message
            timestamp = rx_msg.timestamp
            arbitration_id = rx_msg.arbitration_id
            data = rx_msg.data
            
            # Example processing: Print specific information
            print(f"Received: Timestamp={timestamp}, ID={arbitration_id}, Data={data}")

except KeyboardInterrupt:
    GPIO.output(led, False)
    print('\n\rKeyboard interrupt')
    
    bus.shutdown()