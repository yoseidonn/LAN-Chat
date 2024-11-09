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
FORMAT = pydotenv.Environment.get(key="FORMAT")
HEADER_LENGTH = 64
DISCONNECT = '!DISCONNECT'
USERNAME = '!USERNAME'
NEW_MESSAGE_FROM_CLIENT = '!NEW_MESSAGE_FROM_CLIENT'
NEW_MESSAGE_FROM_SERVER = '!NEW_MESSAGE_FROM_SERVER'
BROADCAST_MESSAGE = "!IS_THERE_ANY_SERVER"
SERVER_PRESENTING = "!HERE_I_AM_SERVING"
SERVER_IS_CLOSING = "!SERVER_IS_CLOSING"
#######################################################################

# SOCKET
#######################################################################
soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
soc.bind(ADDR)
#######################################################################

# LOGGER
#######################################################################
MESSAGE_LOGGER = pydotenv.Environment.get(key='MESSAGE-LOGGER')
SERVER_LOGGER = pydotenv.Environment.get(key='SERVER-LOGGER')
#######################################################################


class Server():
    def __init__(self):
        self.run = True
        self.connections: list[socket.socket] = list()
        self.any_server_presenting = self.broadcast()
        
    def start(self):
        SERVER_LOGGER.warning("[SERVER] Starting...")
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.daemon = True    
        listen_thread.start()
    
    def close(self):  
        SERVER_LOGGER.warning('[SERVER] Shutting down...')

        # TODO - Implement a logic that that keeps the chat going even if the current server is down.
        # Send all servers and ask someone to be the host.
        # Meanwhile, other connection informations would be sent already,
        # Thus, first one that accepts to be host will claim the throne.
        
        # TODO - Now it just gets them notified that server is being closed.
        for conn in self.connections:
            message = SERVER_IS_CLOSING.encode(FORMAT)
            message_length = len(message)
            send_length = str(message_length).encode(FORMAT)
            send_length += b' ' * (HEADER_LENGTH - len(send_length)) # This creates a constant length for header request as defined
            
            message_length = str(message_length).encode(FORMAT)
            conn.send(send_length)
            conn.send(message_length)
            conn.send(message)

        self.run = False
        
    def handle_client(self, conn: socket.socket, addr):
        SERVER_LOGGER.info(f'[NEW CONNECTION] {addr[0]}:{addr[1]} connected. Active connections {len(self.connections)}')
        self.connections.append(conn)
        
        connected = True
        # TODO - Check this last message protocol
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
                    
                    # TODO - Implement this send method
                    #self.send(connection, NEW_MESSAGE_FROM_SERVER)
                    connection.send(len(NEW_MESSAGE_FROM_SERVER))
                    connection.send(NEW_MESSAGE_FROM_SERVER)
                    
                    username_message = f'[{username}: {message}]'
                    connection.send(len(username_message))
                    connection.send(username_message)

            MESSAGE_LOGGER.info(username_message)

        conn.close()
        self.connections.remove(conn)
        SERVER_LOGGER.info(f'[DISCONNECT] {addr} has disconnected! Active connections {len(self.connections)}')
                    
    def listen(self):
        soc.listen()
        SERVER_LOGGER.warning(f'[SERVER] Listening on {ADDR}:{PORT}')

        while self.run:
            connection, addr = soc.accept()
            
            thread = threading.Thread(target=self.handle_client, args=(connection, addr))
            thread.daemon = True
            thread.start()
            
            SERVER_LOGGER.info(f'[CONNECTED] {addr[0]}:{addr[1]}, active connections {threading.active_count() - 1}')
        
        soc.close()
        SERVER_LOGGER.info(f'[SERVER] Stopped listening on {ADDR}:{PORT}')

    def send_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(TIMEOUT)
        
        # Send broadcast message
        logging.info("[BROADCAST] Sending discovery message to network...")
        sock.sendto(BROADCAST_MESSAGE, ('<broadcast>', PORT))

        try:
            # Listen for responses
            response, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
            if response == SERVER_PRESENTING:
                SERVER_LOGGER.warning(f"[SERVER] Presenting server found at {addr[0]}:{addr[1]}")
                return True  # Server is already running
        
        # No server found, proceed as server
        except socket.timeout:
            logging.info("[BROADCAST] No response from any server on the network.")
            return False

    def send(self, message):
        # TODO - Implement for sending messages to clients.
        pass

if __name__ == '__main__':
    server = Server()
    server.start()
    
    # Keep the main thread running, waiting for 'q' to quit
    while True:
        op = input("Enter 'q' to quit: ")
        if op.lower() == 'q':
            soc.close()  # Closes the socket
            break