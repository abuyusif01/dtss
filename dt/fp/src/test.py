import requests
from plc1 import SENSOR3_3

# from utils import SERVER_ADDR

SERVER_ADDR, port = "localhost", 8080

liquidlevel_bottle = float(
    requests.get(f"http://{SERVER_ADDR}:{port}/get_value/{SENSOR3_3[0]}").text
)

print (liquidlevel_bottle)