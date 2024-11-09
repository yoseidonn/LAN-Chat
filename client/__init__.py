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
#######################################################################

# SOCKET
#######################################################################
soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
soc.bind(ADDR)
#######################################################################

# LOGGER
#######################################################################
MESSAGE_LOGGER = pydotenv.Environment.get(key='MESSAGE-LOGGER')
CLIENT_LOGGER = pydotenv.Environment.get(key='CLIENT-LOGGER')
#######################################################################


class Client():
    def __init__(self):
        self.run = True
        
    def listen(self):
        soc.listen()
        CLIENT_LOGGER.warning(f'[CLIENT] Listening on {ADDR}:{PORT}')

        while self.run:
            connection, addr = soc.accept()
            
            thread = threading.Thread(target=self.handle_connection, args=(connection, addr))
            thread.daemon = True
            thread.start()
        
        soc.close()
        CLIENT_LOGGER.info(f'[CLIENT] Stopped listening on {ADDR}:{PORT}')

    def send(self, message: str):
        message_length = str(len(message)).encode(FORMAT)
        send_length = str(len(message_length)).encode(FORMAT)
        send_length += b' ' * (HEADER_LENGTH - send_length)

if __name__ == '__main__':
    pass