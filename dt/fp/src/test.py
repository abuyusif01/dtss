from shutil import ExecError
import time
import requests
from plc1 import SENSOR3_3

# from utils import SERVER_ADDR

SERVER_ADDR, port = "10.0.0.6", 8080

while True:
    try:
        liquidlevel_bottle = float(
            requests.get(
                f"http://{SERVER_ADDR}:{port}/get_value/ACTUATOR1-MV",
                timeout=0.1,  # starting from .1 it doesnt matters
            ).text,
        )
        print("linquid_bottle: ", liquidlevel_bottle)
        time.sleep(0.3)
    except Exception as e:
        print(e)
        time.sleep(0.1)
    # print("PLC1 - failed to get liquid level of bottle (SENSOR 3)")
