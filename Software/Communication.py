import socket
from sys import byteorder
from ctypes import c_uint64, c_float
import struct

MULTICAST_IP = "239.255.255.249" # Must be in multicast range 224.0.0.0-239.255.255.255
PORT = 12345 # Pick a value above standard port # range

def subscribe_to_multicast():
    """Subscribes to the multicast address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_IP) + socket.inet_aton(socket.gethostbyname(socket.gethostname())))
        sock.bind(('', PORT))

        print(f'Subscribed to multicast: {MULTICAST_IP}, {PORT}')

        while True:
            data, address = sock.recvfrom(1024)
            # "!" is network formatting (big-endian), B is unsigned char (uint8), Q is unsigned long long (uint64), f is float (4 bytes), ? is bool (uint8)
            (header, vent_uuid, temperature, motion) = struct.unpack("!BQf?", data) 
            print(f'From {address}: {header}|{vent_uuid}|{temperature:.2f}|{motion}')

def send_to_multicast(data: bytes):
    """Sends the given data to the multicast address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 64)
        sock.sendto(data, (MULTICAST_IP, PORT))

def send_louver_position(vent_uuid: int, louver_position: float):
    print(f'Sending message: 1|{vent_uuid}|{louver_position:0.2f}')
    byte_message = struct.pack("!BQf", 1, vent_uuid, louver_position)
    # print(f'Sending message: {str(byte_message)}')
    send_to_multicast(byte_message)

# For testing purposes
def _send_vent_data(vent_uuid: int, temperature: float, motion: bool):
    byte_message = struct.pack("!BQf?", 0, vent_uuid, temperature, motion)
    # print(f'Sending message: {str(byte_message)}')
    send_to_multicast(byte_message)

if __name__ == '__main__':
    # Test Script
    import time
    import threading

    # Start the TCP server in a thread
    server_thread = threading.Thread(target=subscribe_to_multicast)
    server_thread.start()

    # Send some data to the multicast address in another thread
    for _ in range(5):
        time.sleep(0.5)
        send_thread = threading.Thread(target=_send_vent_data, args=(128,72.4,True))
        send_thread.start()

# some WAP allow certain multicast addressed messages to go through and not others; also depends on the device sending the messages
# changed from 224.1.1.1 because it is reserved for network administration functions
