import socket
import struct
from typing import Callable

MULTICAST_IP = "239.255.255.249" # Must be in multicast range 224.0.0.0-239.255.255.255
PORT = 5005 # Pick a value above standard port # range

def _send_to_multicast(data: bytes):
    """Sends the given data to the multicast address

    Args:
        data (bytes): data to be sent
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 64)
        sock.sendto(data, (MULTICAST_IP, PORT))

def subscribe_to_multicast(callback_function: Callable[[int,float,bool],None]):
    """Subscribes to the multicast address and runs the callback function upon receiving a message from a vent

    Args:
        callback_function (Callable[[vent_uuid:int,temperature:float,motion:bool],None]): function to run after receiving a message from a vent
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_IP) + socket.inet_aton(socket.gethostbyname(socket.gethostname())))
        sock.bind(('', PORT))

        print(f'Subscribed to multicast: {MULTICAST_IP}, {PORT}')

        while True:
            data, address = sock.recvfrom(1024)
            # "<" is little-endian formatting, B is unsigned char (uint8), Q is unsigned long long (uint64), f is float (4 bytes), ? is bool (uint8)
            try:
                (header, vent_uuid, temperature, motion) = struct.unpack("<BQf?", data) 
            except struct.error as e:
                # print(e)
                header = -1
            if header == 0:
                callback_function(vent_uuid, temperature, motion)

def send_louver_position(vent_uuid: int, louver_position: float):
    """Send the new louver position to a vent

    Args:
        vent_uuid (int): vent uuid of the vent needing to update its louvers
        louver_position (float): new louver position for the vent where 0 < louver_position < 1
    """
    header = int(1) # header is always 1 for messages from the hub to the vents
    byte_message = struct.pack("<BQf", header, vent_uuid, louver_position)
    # print(f'Sending message: {str(byte_message)}')
    _send_to_multicast(byte_message)

# Functions below are for testing purposes
def _send_vent_data(vent_uuid: int, temperature: float, motion: bool):
    """Simulate a vent sending data to test 'subscribe_to_multicast' function

    Args:
        vent_uuid (int): vent uuid
        temperature (float): measured temperature
        motion (bool): whether or not motion was detected
    """
    byte_message = struct.pack("<BQf?", 0, vent_uuid, temperature, motion)
    # print(f'Sending message: {str(byte_message)}')
    _send_to_multicast(byte_message)

def _callback_function(vent_uuid: int, temperature: float, motion: bool):
    """Callback function to pass to 'subscribe_to_multicast' for testing
    """
    print(f'Received message: {vent_uuid=} | {temperature=:.2f} | {motion=}')

def _subscribe_to_multicast():
    """Simulate a vent listening to test 'send_louver_position' function
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MULTICAST_IP) + socket.inet_aton(socket.gethostbyname(socket.gethostname())))
        sock.bind(('', PORT))

        print(f'Subscribed to multicast: {MULTICAST_IP}, {PORT}')

        while True:
            data, address = sock.recvfrom(1024)
            # "!" is network formatting (big-endian), B is unsigned char (uint8), Q is unsigned long long (uint64), f is float (4 bytes)
            (header, vent_uuid, louver_position) = struct.unpack("!BQf", data) 
            print(f'From {address}: {header}|{vent_uuid}|{louver_position:.2f}')

# used in initial testing with mohammad
def _temp_send():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('',5005))
    mreq = struct.pack("4sl", socket.inet_aton("239.255.255.249"), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    message = ("192.168.0.10", "120")
    sock.sendto("|".join(message).encode(), ("239.255.255.249", 5005))

if __name__ == '__main__':
    # Test Script
    import time
    import threading

    TEST_INCOMING_MESSAGES = True

    # Start the TCP server in a thread
    # if TEST_INCOMING_MESSAGES:
    #     server_thread = threading.Thread(target=subscribe_to_multicast, args=((_callback_function,)))
    # else:
    #     server_thread = threading.Thread(target=_subscribe_to_multicast)
    # server_thread.start()

    # Send some data to the multicast address in another thread
    for i in range(50):
        time.sleep(0.5)
        if TEST_INCOMING_MESSAGES:
            sendThreads = []
            sendThreads.append(threading.Thread(target=_send_vent_data, args=(0,72+i/9,False)))
            sendThreads.append(threading.Thread(target=_send_vent_data, args=(1,70+i/5,False)))
            sendThreads.append(threading.Thread(target=_send_vent_data, args=(2,61+i/3,False)))
        else:
            send_thread = threading.Thread(target=send_louver_position, args=(129,0.66))
        for thread in sendThreads:
            thread.start()

# Notes
# some WAP allow certain multicast addressed messages to go through and not others; also depends on the device sending the messages
# changed from 224.1.1.1 because it is reserved for network administration functions
