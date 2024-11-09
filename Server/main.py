import os, sys, datetime, logging, pathlib
import socket, threading

# CONSTANTS
#######################################################################
BASE_DIR = pathlib.Path(__name__).resolve().parent
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)

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


connections: list[socket.socket] = list()
def handle_client(conn: socket.socket, addr):
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
            for connection in connections:
                if (conn == connection):
                    continue
                connection.send(len(NEW_MESSAGE_FROM_SERVER))
                connection.send(NEW_MESSAGE_FROM_SERVER)
                
                username_message = f'[{username}: {message}]'
                connection.send(len(username_message))
                connection.send(username_message)

        logging.basicConfig(filename=MSG_PATH)
        logging.info(message)

    conn.close()
    logging.basicConfig(filename=SERVER_PATH)
    logging.info(f'{addr} has disconnected!')
                
        
def listen():
    soc.listen()
    logging.warning(f'Listening on {ADDR}:{PORT}')

    while True:
        connection, addr = soc.accept()
        
        thread = threading.Thread(target=handle_client, args=(connection, addr))
        thread.daemon = True
        thread.start()
        
        logging.basicConfig(filename=MSG_PATH)
        logging.info(f'{addr} has connected.')
        logging.info(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
        print(f'[CONNECTED] {addr}')
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
        
    logging.basicConfig(filename=MSG_PATH)
    logging.info(f'Leaving {ADDR}:{PORT}')  


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