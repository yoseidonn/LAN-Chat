import os, sys, socket
import pathlib, pydotenv
import server

HELP_MSG = """
Invalid usage. Correct usage is:
python3 main.py <PORT> <TIMEOUT>
main.py <PORT>
main.py
"""

BASE_DIR = pathlib.Path(__name__).parent
argv = sys.argv
if len(argv) == 1:
    PORT = 5050
    TIMEOUT = 5
elif len(argv) == 2:
    PORT = argv[1]
elif len(argv) == 3:
    SERVER = socket.gethostbyname(socket.gethostname())
    TIMEOUT = argv[2]
else:
    print(HELP_MSG)
    sys.exit()

pydotenv.Environment.save_environment(key="BASE-DIR", key=BASE_DIR)
pydotenv.Environment.save_environment(key="SERVER", key=SERVER)
pydotenv.Environment.save_environment(key="PORT", key=PORT)

server = server.Server()