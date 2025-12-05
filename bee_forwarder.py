import serial
import time
import socket
from queue import Queue
import threading

# Configure serial connection to XBee
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
TCP_HOST = 'nam1.cloud.thethings.network'  # Replace with your public IP
TCP_PORT = 1700

# Queue for incoming packets
packet_queue = Queue()

def send_at_command(ser, command, wait_time=1):
    """Send AT command and return response"""
    ser.write((command + '\r').encode())
    time.sleep(wait_time)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"AT Command: {command} => Response: {response.strip()}")
    return response.strip()


def initialize_xbee(ser):
    """Configure XBee destination IP and port once at startup"""
    try:
        print("Entering AT command mode...")
        time.sleep(1)
        ser.write(b'+++')
        time.sleep(1.5)
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        print(f"Command mode response: {response.strip()}")

        # Configure UDP settings
        send_at_command(ser, f'ATDL {TCP_HOST}')  # Destination IP
        send_at_command(ser, f'ATDE {hex(TCP_PORT)[2:]}')  # Destination port (hex)
        send_at_command(ser, 'ATIP 0')  # UDP mode
        send_at_command(ser, 'ATWR')  # Write settings
        send_at_command(ser, 'ATCN')  # Exit command mode
        print("XBee initialized successfully!\n")
    except serial.SerialException as e:
        print(f"Serial initialization error: {e}")


def uplink_interceptor(sock):
    """Listen for incoming UDP packets"""
    print("Listening for incoming UDP packets on localhost:18500...")
    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Received packet from {addr}")
        packet_queue.put(data)


def downlink_interceptor(sock):
    """Listen for downlink UDP packets (optional)"""
    print("Listening for downlink UDP packets on localhost:1700...")
    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Received downlink packet from {addr}: {data}")


def forwarder_old(ser):
    """Forward queued packets via XBee"""
    while True:
        packet = packet_queue.get()
        try:
            # Ensure packet is bytes
            if isinstance(packet, str):
                packet = packet.encode('utf-8')
            ser.write(packet)
            print(f"Sent: {packet}")
        except serial.SerialException as e:
            print(f"Serial write error: {e}")
        time.sleep(0.5)  # Avoid overwhelming the XBee

def forwarder(ser):
    """Forward queued packets via XBee safely"""
    while True:
        packet = packet_queue.get()
        try:
            # Ensure packet is bytes
            if isinstance(packet, str):
                packet = packet.encode('utf-8')
            
            # Split packet into smaller chunks (max 100 bytes)
            MAX_CHUNK = 90
            for i in range(0, len(packet), MAX_CHUNK):
                chunk = packet[i:i+MAX_CHUNK]
                ser.write(chunk)
                print(f"Sent chunk: {chunk}")
                time.sleep(0.5)  # Give XBee time to process
        except serial.SerialException as e:
            print(f"Serial write error: {e}")
            # Optionally: reinitialize XBee if connection lost
            try:
                initialize_xbee(ser)
            except:
                print("Failed to reinitialize XBee, skipping packet.")

if __name__ == "__main__":
    # Initialize serial
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        exit(1)

    # Initialize XBee once
    initialize_xbee(ser)

    # Setup UDP sockets
    uplink_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    uplink_sock.bind(('localhost', 18500))

    downlink_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    downlink_sock.bind(('localhost', 1700))

    # Start threads
    threading.Thread(target=uplink_interceptor, args=(uplink_sock,), daemon=True).start()
    threading.Thread(target=downlink_interceptor, args=(downlink_sock,), daemon=True).start()
    threading.Thread(target=forwarder, args=(ser,), daemon=True).start()

    # Keep main thread alive
    print("Gateway running. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)

