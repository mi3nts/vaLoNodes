import serial

# Set up the serial connection
ser = serial.Serial('/dev/ttyS1', 115200)  # Replace 'COM1' with the appropriate port and baud rate

while True:
    # Read a line of data from the serial port
    line = ser.readline()
    
    # Decode the line assuming it's encoded in UTF-8
    decoded_line = line.decode('utf-8').strip()
    
    # Print the received data
    print(decoded_line)
    
    # Break the loop if some condition is met
    if decoded_line == 'quit':
        break

# Close the serial connection
ser.close()
