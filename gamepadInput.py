import RPi.GPIO as GPIO
import can
import time
from evdev import InputDevice, categorize, ecodes

# This defines the GPIO pin for the LED
led = 22

# Set up GPIO for LED
def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, True)

# Function to initialize the CAN bus if not initalize
def initialize_can_bus():
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan')
        return bus
    except OSError:
        print('Cannot find PiCAN board.')
        GPIO.output(led, False)
        exit()

# Function to read gamepad events and handle inputs
def read_gamepad_inputs(gamepad):
    # These are all of the event codes to the gamecontroller 
    
    # These are the digital button variables 
    bBtn = ecodes.BTN_SOUTH
    aBtn = ecodes.BTN_EAST
    yBtn = ecodes.BTN_C
    xBtn = ecodes.BTN_NORTH
    lBtn = ecodes.BTN_WEST
    rBtn = ecodes.BTN_Z
    l2Btn = ecodes.BTN_TL2
    r2Btn = ecodes.BTN_TR2
    startBtn = ecodes.KEY_MENU
    
    # These are the analong variables 
    l2Axis = ecodes.ABS_Z
    r2Axis = ecodes.ABS_RZ
    dpadXAxis = ecodes.ABS_HAT0X
    dpadYAxis = ecodes.ABS_HAT0Y
    leftJoystickXAxis = ecodes.ABS_X
    leftJoystickYAxis = ecodes.ABS_Y
    rightJoystickXAxis = ecodes.ABS_RX
    rightJoystickYAxis = ecodes.ABS_RY
    
    # This creates an empty list for this varibale 
    button_values = []

    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                # this handles the digital button events
                if event.code == aBtn:
                    print("Button A Pressed")
                    button_values = 1;
                elif event.code == bBtn:
                    print("Button B Pressed")
                    button_values = 2;
                elif event.code == xBtn:
                    print("Button X Pressed")
                elif event.code == yBtn:
                    print("Button Y Pressed")
                elif event.code == lBtn:
                    print("Left Shoulder Button Pressed")
                elif event.code == rBtn:
                    print("Right Shoulder Button Pressed")
                elif event.code == l2Btn:
                    print("L2 Button Pressed")
                elif event.code == r2Btn:
                    print("R2 Button Pressed")
                elif event.code == startBtn:
                    print("Start Button Pressed")
                return bytes(button_values) 
        elif event.type == ecodes.EV_ABS:
            # This handles the analog events
            if event.code == l2Axis:
                l2_value = event.value
                print("L2 Analog Value:", l2_value)
            elif event.code == r2Axis:
                r2_value = event.value
                print("R2 Analog Value:", r2_value)
            
            elif event.code == dpadXAxis:
                dpad_x = event.value
                print("D-pad X-Axis Value:", dpad_x)
            elif event.code == dpadYAxis:
                dpad_y = event.value
                print("D-pad Y-Axis Value:", dpad_y)
            elif event.code == leftJoystickXAxis:
                left_joystick_x = event.value
                print("Left Joystick X-Axis Value:", left_joystick_x)
            elif event.code == leftJoystickYAxis:
                left_joystick_y = event.value
                print("Left Joystick Y-Axis Value:", left_joystick_y)
            elif event.code == rightJoystickXAxis:
                right_joystick_x = event.value
                print("Right Joystick X-Axis Value:", right_joystick_x)
            elif event.code == rightJoystickYAxis:
                right_joystick_y = event.value
                print("Right Joystick Y-Axis Value:", right_joystick_y)
            """
            I added this line return bytes for it to show the value in can
            As of now I know that the CAN message all seem the same but Im unsure if I should assign
            Each button a particular message in this case.
            """
            return bytes(button_values)
        
# Function to send gamepad input via CAN
def send_gamepad_input(bus, button_values):
    """
    This is the part I'am a little stuck at since I'm not sure if I set this up correctly, 
    this is supposed to create a CAN message after the input signal, along with a different CAN message 
    each time
    """
    msg = can.Message(arbitration_id=0x7de, data=button_values)
    print(f"Sending CAN message: {msg}") 
    bus.send(msg)

# Main function
def main():
    # Initialize GPIO function
    initialize_gpio()

    # Initialize the CAN bus function if needed
    bus = initialize_can_bus()

    print('\n\rGamecontroller test')
    print('Press CTRL-C to exit')

    # event11 is where the gamepad falls under, this makes the code recoginze the game pad
    gamepad = InputDevice('/dev/input/event6')

    try:
        while True:
            # This makes sure it reads gamepad inputs
            button_values = read_gamepad_inputs(gamepad)

            GPIO.output(led, True)

            """
            I took some of the code from the CAN loopback and put it into this code, 
            the problem that it does show that the messaged is received, I'm not sure if it should be 
            in the format that it is (from the screen shot in the weekly report)
            """

            # Create CAN message to send
            send_gamepad_input(bus, button_values)

            GPIO.output(led, False)
            time.sleep(0.1)

            # Receive loopback message
            rx_msg = bus.recv(timeout=1.0)
            if rx_msg is not None:
                print(f"Received: {rx_msg}")

    except KeyboardInterrupt:
        GPIO.output(led, False)
        print('\n\rKeyboard interrupt')

        bus.shutdown()

if __name__ == '__main__':
    main()
