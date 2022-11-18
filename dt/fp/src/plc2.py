"""
FP plc2.py
"""

import re
from shutil import ExecError
from minicps.devices import PLC
from utils import PLC2_DATA, PORT, SERVER_ADDR, STATE
from utils import PLC2_PROTOCOL, PLC2_ADDR
from utils import PLC_PERIOD_SEC, PLC_SAMPLES

import time
import logging
import requests


SENSOR2 = ("SENSOR2-FL", 2)


class FPPLC2(PLC):

    # boot process
    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s " + PLC2_ADDR + " %(funcName)s %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    def pre_loop(self):
        print("DEBUG: FP PLC2 booting process (enter pre_loop)")
        print
        # wait for the other plcs
        time.sleep(PLC_PERIOD_SEC)

    # setup logger for plc2
    def setup_logger(self, name, log_file, level=logging.INFO):
        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def main_loop(self):
        """plc2 main loop.
        - read flow level (sensor2)
        - read sensor2 value from server
        - update internal enip server
        """

        # setting up first logger
        logger = self.setup_logger("local_logger", "logs/plc2.log")
        print("DEBUG: FP PLC2 enters main_loop.")

        count = 0
        # while count <= PLC_SAMPLES:
        while True:

            # physical process
            flowlevel = float(self.get(SENSOR2))
            print("PLC2 - get flowlevel (SENSOR 2): %f" % flowlevel)

            # network capabilities
            try:
                self.send(SENSOR2, flowlevel, PLC2_ADDR)

                # we try reading sensor2 from the main server
                # if this failed we gonna assume there's a Dos attack on the network
                try:
                    req = requests.get(
                        f"http://{SERVER_ADDR}:{PORT}/set_value/{SENSOR2[0]}/{flowlevel}",
                        timeout=0.1,
                    )

                    if req.text == "success":
                        pass
                    else:
                        print("PLC2 - failed to update server DDOS attacker detected")

                        logger.error(
                            "PLC2 - failed to update server DDOS attacker detected"
                        )

                except Exception as e:
                    print("PLC2 SERVER - Exception: %s" % e)
                    logger.debug("PLC2 SERVER - Exception: %s" % e)

                # logging the value of sensor2 from db, we gonna use this in the future to calcluate
                # possible measurement modification
                print("DEBUG PLC2 - receive flowlevel (SENSOR 2): ", flowlevel)
                logger.info("Internal ENIP tag (SENSOR 2) updated: %.2f" % (flowlevel))
            except:
                logger.error("Could not update internal ENIP tag (SENSOR 2)")

            time.sleep(PLC_PERIOD_SEC)
            count += 1

    def _stop(self):
        print("DEBUG FP PLC3 shutdown")

        return super()._stop()


if __name__ == "__main__":

    plc2 = FPPLC2(
        name="plc2",
        state=STATE,
        protocol=PLC2_PROTOCOL,
        memory=PLC2_DATA,
        disk=PLC2_DATA,
    )
