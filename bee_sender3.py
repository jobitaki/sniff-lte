import serial
import time

# Configure serial connection to XBee
SERIAL_PORT = '/dev/tty.usbserial-D30H6XKE'  # macOS serial port
BAUD_RATE = 9600
TCP_HOST = '18.224.162.240'  # Replace with your public IP or ngrok address
TCP_PORT = 10151

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
        print("\nSending TCP packets...")
        # Send TCP packets
        for i in range(5):
            message = f"Hello from XBee! Packet {i+1}"
            ser.write(message.encode())
            print(f"Sent: {message}")
            time.sleep(2)
        
        ser.write(b'+++')
        send_at_command(ser, 'ATCN')  # Exit command mode
        ser.close()
        print("\nDone!")
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
