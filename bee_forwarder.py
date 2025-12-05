import serial
import time
from datetime import datetime, timezone
import json
import socket
from queue import Queue

# Configure serial connection to XBee
SERIAL_PORT = '/dev/tty.usbserial-D30H6XKE'  # macOS serial port
BAUD_RATE = 9600
TCP_HOST = '13.56.119.10'  # Replace with your public IP or ngrok address
TCP_PORT = 1700

# Gateway EUI (8 bytes) - replace with your gateway's EUI
GATEWAY_EUI = bytes.fromhex('0016C001FF13BD44')  # Example: AA555A0000000101

def send_at_command(ser, command, wait_time=1):
    """Send AT command and return response"""
    ser.write((command + '\r').encode())
    time.sleep(wait_time)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Command: {command}")
    print(f"Response: {response}")
    return response


def downlink_interceptor(sock):
    """Listens for incoming UDP packets on localhost:1700 for downlink"""
    print("Listening for downlink UDP packets on localhost:1700...")
    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Received downlink packet from {addr}: {data}")
        # Process downlink packet as needed


def uplink_interceptor(sock, packet_queue):
    """Listens to localhost:18500 for incoming UDP packets"""
    print("Listening for incoming UDP packets on localhost:18500...")
    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Received packet from {addr}")
        packet_queue.put(data)


def process_and_send_packet(packet):
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
        send_at_command(ser, f'ATDL {TCP_HOST}')  # Set destination IP
        send_at_command(ser, f'ATDE {hex(TCP_PORT)[2:]}')  # Set destination port (hex)
        send_at_command(ser, 'ATIP 0')  # Set to UDP mode
        send_at_command(ser, 'ATWR')  # Write settings
        send_at_command(ser, 'ATCN')  # Exit command mode

        print("\nSending UDP packets...")
        # Send UDP packets
        message = packet
        ser.write(message)
        print(f"Sent: {message}")
        time.sleep(2)
        for i in range(5):
            message = create_push_data_packet()
            ser.write(message)
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


def forwarder(packet_queue):
    """Processes and forwards packets from the queue via XBee"""
    while True:
        if not packet_queue.empty():
            packet = packet_queue.get()
            process_and_send_packet(packet)


if __name__ == "__main__":
    downlink_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    downlink_sock.bind(('localhost', 1700))
    uplink_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    uplink_sock.bind(('localhost', 18500))
    packet_queue = Queue()

    uplink_thread = threading.Thread(target=uplink_interceptor, args=(uplink_sock, packet_queue,))
    uplink_thread.daemon = True
    downlink_thread = threading.Thread(target=downlink_interceptor, args=(downlink_sock,))
    downlink_thread.daemon = True
    forwarder_thread = threading.Thread(target=forwarder, args=(packet_queue,))
    forwarder_thread.daemon = True

    uplink_thread.start()
    downlink_thread.start()
    forwarder_thread.start()
