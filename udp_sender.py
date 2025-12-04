import socket
import time

# UDP configuration
HOST = '127.0.0.1'  # localhost
PORT = 18500

def main():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        print(f"Sending UDP packets to {HOST}:{PORT}")
        print("Press Ctrl+C to stop\n")
        
        # Send packets
        counter = 1
        while True:
            message = f"Test packet #{counter}"
            sock.sendto(message.encode(), (HOST, PORT))
            print(f"Sent: {message}")
            counter += 1
            time.sleep(2)  # Wait 2 seconds between packets
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed")

if __name__ == "__main__":
    main()
