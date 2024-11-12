import os, sys, socket, logging
import pathlib, pydotenv, datetime
import server


#######################################################################
# Set constants
#######################################################################
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'UTF-8'
BASE_DIR = pathlib.Path(__name__).parent
PORT = 5050
TIMEOUT = 5
HELP_MSG = """
Invalid usage. Correct usage is:
python3 main.py <PORT> <TIMEOUT>
main.py <PORT>
main.py
"""

#######################################################################
# Process the parameters passed into the program
#######################################################################
try:
    if len(sys.argv) == 2:
        PORT = sys.argv[1]
    elif len(sys.argv) == 3:
        PORT = sys.argv[1]
        TIMEOUT = sys.argv[2]
    else:
        print(HELP_MSG)
        sys.exit()
except Exception as e:
    print(e)
    exit()
    
#######################################################################
# Create loggers
#######################################################################
date = str(datetime.datetime.today().strftime('%d-%m-%Y'))
log_path = os.path.join(BASE_DIR, 'server', 'logs')

msg_log_path = os.path.join(log_path, date+'.msg.log')
srv_log_path = os.path.join(log_path, date+'.srv.log')
clt_log_path = os.path.join(log_path, date+'.clt.log')

try:
    os.mkdir(log_path)
except Exception as e:
    pass

MESSAGE_LOGGER = logging.getLogger("MessageLogger")
SERVER_LOGGER = logging.getLogger('ServerLogger')
CLIENT_LOGGER = logging.getLogger('ClientLogger')
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
client_handler = logging.FileHandler(
    filename=clt_log_path,
    mode='a',
    encoding=FORMAT,
    style='{',
    datefmt='%d-%m-%Y %H:%M'
)    
MESSAGE_LOGGER.addHandler(message_handler)
SERVER_LOGGER.addHandler(server_handler)
CLIENT_LOGGER.addHandler(client_handler)

#######################################################################
# Set environment variables
#######################################################################
pydotenv.Environment().save_environment(key="MESSAGE-LOGGER", value=MESSAGE_LOGGER)
pydotenv.Environment().save_environment(key="SERVER-LOGGER", value=SERVER_LOGGER)
pydotenv.Environment().save_environment(key="CLIENT-LOGGER", value=CLIENT_LOGGER)
pydotenv.Environment().save_environment(key="BASE-DIR", value=BASE_DIR)
pydotenv.Environment().save_environment(key="SERVER", value=SERVER)
pydotenv.Environment().save_environment(key="PORT", value=PORT)

#######################################################################
# Start server
#######################################################################
server = server.Server()