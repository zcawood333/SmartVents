import socket

MULTICAST_IP = "224.1.1.1" # Must be in multicast range 224.0.0.0-239.255.255.255
PORT = 12345 # Pick a value above standard port # range

def subscribe_to_multicast():
    """Subscribes to the multicast address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_IP) + socket.inet_aton('0.0.0.0'))
        sock.bind(('', PORT))

        while True:
            data, address = sock.recvfrom(1024)
            print(f"Received data from {address}: {data}") # Can be changed later in here or function can be passed a callback to run

def send_to_multicast(data: bytes):
    """Sends the given data to the multicast address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(data, (MULTICAST_IP, PORT))

if __name__ == '__main__':
    # Test Script
    import time
    import threading

    # Start the TCP server in a thread
    server_thread = threading.Thread(target=subscribe_to_multicast)
    server_thread.start()

    # Send some data to the multicast address in another thread
    data = b"Hello, world!"
    for _ in range(10):
        time.sleep(0.5)
        send_thread = threading.Thread(target=send_to_multicast, args=(data,))
        send_thread.start()