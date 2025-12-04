import socket
import sys

# UDP configuration
HOST = '127.0.0.1'  # localhost
PORT = 18500

def main():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Bind to the port
        sock.bind((HOST, PORT))
        print(f"UDP listener started on {HOST}:{PORT}")
        print("Waiting for packets... (Press Ctrl+C to stop)\n")
        
        # Listen for packets
        while True:
            data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
            print(f"Received from {addr}: {data.decode('utf-8', errors='ignore')}")
            
    except KeyboardInterrupt:
        print("\n\nListener stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed")

if __name__ == "__main__":
    main()
