import RPi.GPIO as GPIO
import can
import time

led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, True)

count = 0

print('\n\rCAN Rx test')

try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
except OSError:
    print('Cannot find PiCAN board.')
    GPIO.output(led, False)
    exit()

print('Press CTL-C to exit')

# Main loop
try:
    while True:
        GPIO.output(led, True)
        msg = can.Message(arbitration_id=0x7de, data=[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, count & 0xff])
        bus.send(msg)
        count += 1
        time.sleep(0.1)
        GPIO.output(led, False)
        time.sleep(0.1)
        print(count)

        # Receive loopback message
        rx_msg = bus.recv(timeout=1.0)
        if rx_msg is not None:
            print(f"Received: {rx_msg.data}")

except KeyboardInterrupt:
    # Catch keyboard interrupt
    GPIO.output(led, False)
    print('\n\rKeyboard interrupt')