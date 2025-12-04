import serial
import time

# Configure serial connection to XBee
SERIAL_PORT = '/dev/tty.usbserial-D30H6XKE'  # Change to your port (e.g., '/dev/ttyUSB0' on Linux)
BAUD_RATE = 9600
UDP_HOST = '18.224.162.240'  # localhost
UDP_PORT = 10151

def send_at_command(ser, command, wait_time=1):
    """Send AT command and return response"""
    ser.write((command + '\r').encode())
    time.sleep(wait_time)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Command: {command}")
    print(f"Response: {response}")
    return response

def main():
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        time.sleep(2)
        
        # Enter AT command mode
        time.sleep(1)
        ser.write(b'+++')
        time.sleep(1.5)
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        print(f"Command mode response: {response}")
        
        # Configure UDP settings
        send_at_command(ser, f'ATDL {UDP_HOST}')  # Set destination IP
        send_at_command(ser, f'ATDE {hex(UDP_PORT)[2:]}')  # Set destination port (hex)
        send_at_command(ser, 'ATIP 1')  # Set to UDP mode
        send_at_command(ser, 'ATWR')  # Write settings
        send_at_command(ser, 'ATCN')  # Exit command mode
        
        print("\nSending UDP packets...")
        # Send UDP packets
        for i in range(5):
            message = f"Hello from XBee! Packet {i+1}"
            ser.write(message.encode())
            print(f"Sent: {message}")
            time.sleep(2)
        
        ser.close()
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
