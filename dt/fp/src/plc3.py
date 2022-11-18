"""
FP plc3.py
"""

from queue import LifoQueue
from minicps.devices import PLC
from utils import PLC3_DATA, PORT, SERVER_ADDR, STATE
from utils import PLC3_PROTOCOL, PLC3_ADDR
from utils import PLC_PERIOD_SEC, PLC_SAMPLES

import time
import logging
import requests


SENSOR3 = ("SENSOR3-LL-bottle", 3)


class FPPLC3(PLC):

    # boot process
    def pre_loop(self):
        print("DEBUG: FP PLC3 booting process (enter pre_loop)")
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
        """plc3 main loop.
        - read liquid level of bottle (sensor3)
        - update internal enip server
        """

        print("DEBUG: FP PLC3 enters main_loop.")
        print
        # FYI: BSD-syslog format (RFC 3164), e.g. <133>Feb 25 14:09:07 webserver syslogd: restart   PRI <Facility*8+Severity>, HEADER (timestamp host), MSG (program/process message)
        logger = self.setup_logger("local_logger", "logs/plc3.log")
        count = 0
        # while count <= PLC_SAMPLES:
        while True:
            # physical process
            liquidlevel_bottle = float(self.get(SENSOR3))
            print("PLC3 - get liquidlevel_bottle (SENSOR 3): %i" % liquidlevel_bottle)

            try:
                # network capabilities
                self.send(SENSOR3, liquidlevel_bottle, PLC3_ADDR)
                try:
                    req = requests.get(
                        f"http://{SERVER_ADDR}:{PORT}/set_value/{SENSOR3[0]}/{liquidlevel_bottle}",
                        timeout=0.1,
                    )

                    if req.text == "success":
                        pass
                    else:
                        print("PLC2 - failed to update server DDOS attacker detected")
                        logger.error(
                            "PLC3 - failed to update server DDOS attacker detected"
                        )
                        exit(1)

                except Exception as e:
                    print("PLC2 - Exception: %s" % e)
                    logger.debug("PLC2 - Exception: %s" % e)
                    exit(1)
                print(
                    "DEBUG PLC3 - receive liquidlevel_bottle (SENSOR 3): ",
                    liquidlevel_bottle,
                )
                logger.info(
                    "Internal ENIP tag (SENSOR 3) updated: %.2f" % (liquidlevel_bottle)
                )
            except:
                logging.error("Could not update internal ENIP tag (SENSOR 3)")

            time.sleep(PLC_PERIOD_SEC)  # sleep for .5 seconds
            count += 1

    def _stop(self):
        print("DEBUG FP PLC3 shutdown")
        return super()._stop()


if __name__ == "__main__":

    plc3 = FPPLC3(
        name="plc3",
        state=STATE,
        protocol=PLC3_PROTOCOL,
        memory=PLC3_DATA,
        disk=PLC3_DATA,
    )
