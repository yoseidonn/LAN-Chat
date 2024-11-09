import os, sys
import datetime, logging, pathlib, pydotenv
import socket, threading

# CONSTANTS
#######################################################################
if __name__ == '__main__':
    BASE_DIR = pathlib.Path(__name__).parent.parent
    SERVER = socket.gethostbyname(socket.gethostname())
    PORT = pydotenv.Environment.get(key="PORT")
else:
    BASE_DIR = pydotenv.Environment.get(key="BASE-DIR")
    SERVER = pydotenv.Environment.get(key="SERVER")
    PORT = pydotenv.Environment.get(key="PORT")

ADDR = (SERVER, PORT)
TIMEOUT = pydotenv.Environment.get(key="TIMEOUT")

HEADER_LENGTH = 64
FORMAT = 'UTF-8'
DISCONNECT = '!DISCONNECT'
USERNAME = '!USERNAME'
NEW_MESSAGE_FROM_CLIENT = '!NEW_MESSAGE_FROM_CLIENT'
NEW_MESSAGE_FROM_SERVER = '!NEW_MESSAGE_FROM_SERVER'
BROADCAST_MESSAGE = "!IS_THERE_ANY_SERVER"
SERVER_PRESENTING = "!HERE_I_AM_SERVING"
#######################################################################

# SOCKET
#######################################################################
soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
soc.bind(ADDR)
#######################################################################

# LOGGER
#######################################################################
date = str(datetime.datetime.today().strftime('%d-%m-%Y'))
log_path = os.path.join(BASE_DIR, 'server', 'logs')
msg_log_path = os.path.join(log_path, date+'.msg.log')
srv_log_path = os.path.join(log_path, date+'.srv.log')

try:
    os.mkdir(log_path)
except Exception as e:
    pass

MESSAGE_LOGGER = logging.getLogger("MessageLogger")
SERVER_LOGGER = logging.getLogger('ServerLogger')
message_handler = logging.FileHandler(
    filename=msg_log_path,
    mode='a',
    encoding=FORMAT,
    style='{',
    datefmt='%d-%m-%Y %H:%M'
)
server_handler = logging.FileHandler(
    filename=srv_log_path,
    mode='a',
    encoding=FORMAT,
    style='{',
    datefmt='%d-%m-%Y %H:%M'
)    
MESSAGE_LOGGER.addHandler(message_handler)
SERVER_LOGGER.addHandler(server_handler)
#######################################################################



class Server():
    def __init__(self):
        self.run = True
        self.connections: list[socket.socket] = list()
        self.any_server_presenting = self.broadcast()
        
    def start(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.daemon = True    
        listen_thread.start()
        
    def handle_client(self, conn: socket.socket, addr):
        connected = True
        last_message = ''
        username = ''
        
        while connected:    
            message_len = conn.recv(HEADER_LENGTH).decode(format=FORMAT)
            message = conn.recv(message_len)
            
            # Check if user has copied the header command
            if (message == last_message):
                continue
            else:
                last_message = message
                
            # TODO - Create some other checks in need.
            if (last_message == DISCONNECT):
                connected = False
            elif (last_message == USERNAME):
                username = message
            elif (last_message == NEW_MESSAGE_FROM_CLIENT):
                # If the msg is a chat message, send the msg to other connections
                for connection in self.connections:
                    if (conn == connection):
                        continue
                    connection.send(len(NEW_MESSAGE_FROM_SERVER))
                    connection.send(NEW_MESSAGE_FROM_SERVER)
                    
                    username_message = f'[{username}: {message}]'
                    connection.send(len(username_message))
                    connection.send(username_message)

            MESSAGE_LOGGER.info(username_message)

        conn.close()
        SERVER_LOGGER.info(f'{addr} has disconnected!')
                    
            
    def listen(self):
        soc.listen()
        SERVER_LOGGER.warning(f'Listening on {ADDR}:{PORT}')

        while self.run:
            connection, addr = soc.accept()
            
            thread = threading.Thread(target=self.handle_client, args=(connection, addr))
            thread.daemon = True
            thread.start()
            
            SERVER_LOGGER.info(f'[CONNECTED] {addr[0]}:{addr[1]}, active connections {threading.active_count() - 1}')
        SERVER_LOGGER.info(f'Leaving {ADDR}:{PORT}')  

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
            if response == SERVER_PRESENTING:
                (f"Server found at {addr}")
                return True  # Server is already running
        
        # No server found, proceed as server
        except socket.timeout:
            logging.info("No response from any server on the network.")
            return False


if __name__ == '__main__':
    server = Server()
    server.start()
    SERVER_LOGGER.warning("Server is starting.")
    
    # Keep the main thread running, waiting for 'q' to quit
    while True:
        op = input("Enter 'q' to quit: ")
        if op.lower() == 'q':
            soc.close()  # Closes the socket
            SERVER_LOGGER.warning('Server is shutting down.')
            break