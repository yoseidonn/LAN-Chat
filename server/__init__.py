import os, sys
import datetime, logging, pathlib, pydotenv
import socket, threading

# CONSTANTS
#######################################################################
if __name__ == '__main__':
    BASE_DIR = pathlib.Path(__name__).parent.parent
    SERVER = socket.gethostbyname(socket.gethostname())
    PORT = pydotenv.Environment().get(key="PORT")
else:
    BASE_DIR = pydotenv.Environment().get(key="BASE-DIR")
    SERVER = pydotenv.Environment().get(key="SERVER")
    PORT = pydotenv.Environment().get(key="PORT")

ADDR = (SERVER, PORT)
TIMEOUT = pydotenv.Environment().get(key="TIMEOUT")
FORMAT = pydotenv.Environment().get(key="FORMAT")
HEADER_LENGTH = 64
DISCONNECT_MESSAGE = '!DISCONNECT'
USERNAME_MESSAGE = '!USERNAME'
NEW_MESSAGE_FROM_CLIENT = '!NEW_MESSAGE_FROM_CLIENT'
NEW_MESSAGE_FROM_SERVER = '!NEW_MESSAGE_FROM_SERVER'
BROADCAST_MESSAGE = "!IS_THERE_ANY_SERVER"
BROADCAST_REPLY = "!HERE_I_AM_HOSTING"
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

        self.start()
        
    def start(self):
        self.any_server_presenting = self.send_broadcast()
        if self.any_server_presenting:
            self.go_client_mode()
            
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
        
        # TODO - Implement client side!!!
        # Now it just gets them notified that server is being closed.
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
        last_request = str()
        user_name = f"{addr[0]}:{addr[1]}"
        while connected:    
            request_len = conn.recv(HEADER_LENGTH).decode(format=FORMAT)
            request = conn.recv(request_len)
            
            # Check if user has copied the header command
            if (request == last_request):
                continue
                
            ###################################################    
            # Decide if this is a special request
            ###################################################    
			
            if request == DISCONNECT_MESSAGE:
                self.update_everyone(mod=DISCONNECT_MESSAGE, user_name=user_name)
                MESSAGE_LOGGER.info(f"{user_name} -> {request}")
                connected = False
                
            elif request == NEW_MESSAGE_FROM_CLIENT:
                self.last_request = NEW_MESSAGE_FROM_CLIENT

            elif request == USERNAME_MESSAGE:
                self.last_request = USERNAME_MESSAGE
			
            ###################################################    
			# Process the request as what last_request is		
            ###################################################    
            if last_request == NEW_MESSAGE_FROM_CLIENT:
                MESSAGE_LOGGER.info(f"{user_name} -> {request}")
                self.update_everyone(mod=NEW_MESSAGE_FROM_CLIENT, message=request, user_name=user_name, connection=conn)
                self.last_request = ""

            elif last_request == USERNAME_MESSAGE:
                user_name = request

        ###################################################    
        # Close the connection, user has disconnected    
        ###################################################    
        conn.close()
        self.connections.remove(conn)
        SERVER_LOGGER.info(f'[DISCONNECT] {addr} has disconnected! Active connections {len(self.connections)}')                

    def send(self, connection: socket.socket, message: str):
        ###################################################    
        # Send the message
        ###################################################   
        message = message.encode(FORMAT)
        message_length = str(len(message)).encode(FORMAT)
        send_length = str(len(message_length)).encode(FORMAT)
        
        connection.send(send_length)
        connection.send(message_length)
        connection.send(message)

    def update_everyone(self, mod: str = None, user_name: str = str(), message: str = str(), connection: socket.socket = None):
        ###################################################    
        # Say everyone what is about to get sent
        ###################################################    
        message = message.encode(FORMAT)
        message_length = str(len(mod)).encode(FORMAT)
        send_length = str(len(message_length)).encode(FORMAT)        
        for conn in self.connections:
            if conn == connection:
                continue
            conn.send(send_length)
            conn.send(message_length)
            conn.send(message)
        
        ###################################################    
        # Edit the message
        ###################################################    
        if mod == NEW_MESSAGE_FROM_CLIENT:
            message = f"{user_name} -> {message}".encode(FORMAT)
        
        elif mod == DISCONNECT_MESSAGE:
            message = f"[SERVER] {user_name} has disconnected!"
            
        message_length = str(len(message)).encode(FORMAT)
        send_length = str(len(message_length)).encode(FORMAT)        
    
        ###################################################    
        # Send message to everyone
        ###################################################    
        for conn in self.connections:
            if conn == connection:
                continue
            conn.send(send_length)
            conn.send(message_length)
            conn.send(message)
            
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
        ###################################################
        # Set a socket to send the broadcast
        ###################################################
        broadcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broadcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_soc.settimeout(TIMEOUT)
        
        # Send broadcast message
        logging.info("[BROADCAST] Sending discovery message to network...")
        broadcast_soc.sendto(BROADCAST_MESSAGE, ('<broadcast>', PORT))

        ###################################################
        # Wait for any reponse
        ###################################################
        try:
            response, addr = broadcast_soc.recvfrom(HEADER_LENGTH)  # Buffer size of 1024 bytes
            if response == BROADCAST_REPLY:
                SERVER_LOGGER.warning(f"[SERVER] Presenting server found at {addr[0]}:{addr[1]}")
                return True  # Server is already running
        
        # No server found, proceed as server
        except socket.timeout:
            logging.info("[BROADCAST] No response from any server on the network.")
            return False
if __name__ == '__main__':
    server = Server()
    server.start()
    
    # Keep the main thread running, waiting for 'q' to quit
    while True:
        op = input("Enter 'q' to quit: ")
        if op.lower() == 'q':
            soc.close()  # Closes the socket
            break