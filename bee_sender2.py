import serial
import time
from datetime import datetime, timezone
import json
import secrets

# Configure serial connection to XBee
SERIAL_PORT = '/dev/tty.usbserial-D30H6XKE'  # macOS serial port
BAUD_RATE = 9600
TCP_HOST = '13.56.119.10'  # Replace with your public IP or ngrok address
TCP_PORT = 1700

# Gateway EUI (8 bytes) - replace with your gateway's EUI
GATEWAY_EUI = bytes.fromhex('0016C001FF13BD44')  # Example: AA555A0000000101

def generate_token():
    """Generate a random 2-byte token"""
    return secrets.randbits(16).to_bytes(2, 'big')

def create_pull_data_packet():
    """Create a PULL_DATA packet (gateway alive signal)"""
    # Format: 0x02 [token] 0x02 [gateway_eui]
    version = b'\x02'
    token = generate_token()
    identifier = b'\x02'  # PULL_DATA
    packet = version + token + identifier + GATEWAY_EUI
    return packet

def generate_unique_id():
    """Generate a unique ID similar to ULID format"""
    # Generate 26 character alphanumeric ID (simplified ULID-like)
    chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    return ''.join(secrets.choice(chars) for _ in range(26))

def create_push_data_packet():
    """Create a PUSH_DATA packet with status information"""
    # Format: 0x02 [token] 0x00 [gateway_eui] [JSON]
    version = b'\x02'
    token = generate_token()
    identifier = b'\x00'  # PUSH_DATA
    
    # Status JSON payload
    stat = {
        "stat": {
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S GMT"),
            "lati": 40.4406,  # Example coordinates (Pittsburgh)
            "long": -79.9959,
            "alti": 0,
            "rxnb": 0,  # Number of packets received
            "rxok": 0,  # Number of packets received OK
            "rxfw": 0,  # Number of packets forwarded
            "ackr": 100.0,  # Percentage of acknowledgements
            "dwnb": 0,  # Number of downlink packets
            "txnb": 0   # Number of packets transmitted
        }
    }
    
    json_data = json.dumps(stat).encode('utf-8')
    packet = version + token + identifier + GATEWAY_EUI + json_data
    return packet

def generate_lorawan_packet():
    """Generate a LoRaWAN-style status packet with current timestamp"""
    packet = {
        "name": "gs.up.receive",
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "identifiers": [
            {
                "gateway_ids": {
                    "gateway_id": "sniff-station-0"
                }
            }
        ],
        "context": {
            "tenant-id": "CgN0dG4="
        },
        "visibility": {
            "rights": [
                "RIGHT_GATEWAY_TRAFFIC_READ"
            ]
        },
        "unique_id": generate_unique_id(),
    }
    return json.dumps(packet)

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
        send_at_command(ser, f'ATDL {TCP_HOST}')  # Set destination IP
        send_at_command(ser, f'ATDE {hex(TCP_PORT)[2:]}')  # Set destination port (hex)
        send_at_command(ser, 'ATIP 0')  # Set to UDP mode
        send_at_command(ser, 'ATWR')  # Write settings
        send_at_command(ser, 'ATCN')  # Exit command mode

        print("\nSending TCP packets...")
        # Send TCP packets
        message = create_pull_data_packet()
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

if __name__ == "__main__":
    main()
