import os, sys, datetime, logging, pathlib
import socket, threading


# Constants
#######################################################################
BASE_DIR = pathlib.Path(__name__).resolve().parent

IP = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (IP, PORT)

HEADER_LENGTH = 64
TIMEOUT = 5

FORMAT = 'UTF-8'
BROADCAST_MESSAGE = "!DISCOVER_SERVER"
RESPONSE_MESSAGE = "!SERVER_PRESENT"
#######################################################################

# LOGGING
#######################################################################
date = str(datetime.datetime.today().strftime('%d-%m-%Y'))
os.mkdir(os.path.join(BASE_DIR, 'Logs', 'Messages', date))
    
MSG_PATH = os.path.join(BASE_DIR, 'Logs', 'Messages', date, 'logs.log')
SERVER_PATH = os.path.join(BASE_DIR, 'Logs', 'Server', date, 'logs.log')
    
logging.basicConfig(
    filename=MSG_PATH,
    filemode='a',
    encoding='UTF-8',
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)
#######################################################################

class Network():
    def __init__(self):
        self.soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.soc.bind(ADDR)
        
        # Check if there is a server on the network
        is_server_present = self.send_broadcast()
        if is_server_present:
            # Start client
            logging.warning("Starting in client mode...")
            self.start
        else:
            # Start server
            logging.info("No server found, starting in server mode...")
            self.start_server_mode()

    def send_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(TIMEOUT)
        
        # Send broadcast message
        logging.info("Sending discovery message to network...")
        sock.sendto(BROADCAST_MESSAGE, ('<broadcast>', PORT))

        try:
            # Listen for responses
            response, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
            if response == RESPONSE_MESSAGE:
                (f"Server found at {addr}")
                return True  # Server is already running
        
        # No server found, proceed as server
        except socket.timeout:
            logging.info("No response from any server on the network.")
            return False

    def respond_to_discovery(self):
        pass