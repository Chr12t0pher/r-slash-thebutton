#!/home/www/venv/bin/python
import threading
import sys

sys.path.insert(0, '/home/www/venv/lib/python3.4/site-packages/')
sys.path.insert(0, '/home/www/')

from app import app as application
from app import Data

threading.Thread(target=Data.socket_controller).start()
threading.Thread(target=Data.scheduler).start()
