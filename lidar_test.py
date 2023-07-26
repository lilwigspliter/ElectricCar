import serial
import time

# Open the serial port
ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)

# Start the lidar motor
ser.write(b'\xA5\xF0')

# Wait for the lidar to spin up
time.sleep(2)

# Request scan data
ser.write(b'\xA5\x20')

# Read and process scan data
while True:
    raw_data = ser.read(5)  # Read 5 bytes (one measurement)
    # Process the raw data according to the RPLidar protocol

# Stop the lidar motor
ser.write(b'\xA5\x25')

# Close the serial port
ser.close()
