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

def connect():
    pass


if __name__ == '__main__':
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
    
    logging.basicConfig(filename=MSG_PATH)
    logging.warning("Server is starting.")
    
    listen_thread = threading.Thread(target=listen)
    listen_thread.daemon = True    
    listen_thread.start()
    
    
    # Keep the main thread running, waiting for 'q' to quit
    while True:
        op = input("Enter 'q' to quit: ")
        if op.lower() == 'q':
            soc.close()  # Closes the socket
            logging.basicConfig(filename=SERVER_PATH)
            logging.warning('Server is shutting down.')
            break