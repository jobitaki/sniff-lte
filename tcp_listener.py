import socket
import sys

# TCP configuration
HOST = '127.0.0.1'  # Listen on all interfaces (accessible from internet)
PORT = 18500

def main():
    # Create TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind and listen
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"TCP listener started on {HOST}:{PORT}")
        print("Waiting for connections... (Press Ctrl+C to stop)\n")
        
        # Accept connections
        while True:
            conn, addr = sock.accept()
            print(f"Connected by {addr}")
            
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"Received: {data.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"Connection error: {e}")
            finally:
                conn.close()
                print(f"Connection from {addr} closed\n")
            
    except KeyboardInterrupt:
        print("\n\nListener stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Socket closed")

if __name__ == "__main__":
    main()
