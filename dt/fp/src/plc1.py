"""
FP plc1.py
"""

from minicps.devices import PLC
from utils import (
    CPPPO_PORT,
    PLC1_DATA,
    PLC1_PROTOCOL,
    PLC1_ADDR,
    PLC2_ADDR,
    PLC3_ADDR,
    PORT,
    SERVER_ADDR,
    STATE,
    PLC_PERIOD_SEC,
    TANK_M,
    BOTTLE_M,
    SENSOR2_THRESH,
)

import time
import logging
import csv
import datetime
import requests
import os

# tag addresses
SENSOR1 = ("SENSOR1-LL-TANK", 1)
ACTUATOR1 = ("ACTUATOR1-MV", 1)

# interlocks to plc2 and plc3
SENSOR2_1 = ("SENSOR2-FL", 1)  # to be sent to PLC2
SENSOR2_2 = ("SENSOR2-FL", 2)  # to be received from PLC2
SENSOR3_1 = ("SENSOR3-LL-BOTTLE", 1)  # to be sent to PLC3
SENSOR3_3 = ("SENSOR3-LL-BOTTLE", 3)  # to be received from PLC3


class FPPLC1(PLC):

    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s " + PLC1_ADDR + " %(funcName)s %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    # boot process
    def pre_loop(self, sleep=0.5):
        print("DEBUG: FP PLC1 enters pre_loop")
        print()

        time.sleep(sleep)

    # setup logger for plc1
    def setup_logger(self, name, log_file, level=logging.INFO):
        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def api_log(self, _timestamp, _from, _to, _label, _port, _value):
        """The api_log is what we gonna be reading from the server to generate the dashboard logs table"""
        with open("API_LOGS/api_log.csv", "w") as writeobj:
            fieldnames = [
                "timestamp",
                "from",
                "to",
                "label",
                "port",
                "value",
            ]
            csv_writer = csv.DictWriter(writeobj, fieldnames=fieldnames)

            csv_writer.writerow(
                {
                    "timestamp": _timestamp,
                    "from": _from,
                    "to": _to,
                    "label": _label,
                    "port": _port,
                    "value": _value,
                }
            )

    def store_values(
        self,
        liquidlevel_tank,
        flowlevel,
        liquidlevel_bottle,
        motor_status,
        count,
    ):
        with open("API_LOGS/measurements.csv", "w") as writeobj:
            fieldnames = [
                "timestamp",
                "tank_liquidlevel",
                "flowlevel",
                "bottle_liquidlevel",
                "motor_status",
            ]
            csv_writer = csv.DictWriter(writeobj, fieldnames=fieldnames)

            if count == 0:  # we basically write the header only once
                csv_writer.writeheader()

            csv_writer.writerow(
                {
                    "timestamp": str(datetime.datetime.now()),
                    "tank_liquidlevel": liquidlevel_tank,
                    "flowlevel": flowlevel,
                    "bottle_liquidlevel": liquidlevel_bottle,
                    "motor_status": motor_status,
                }
            )

    def main_loop(self):
        """plc1 main loop.
        - reads values from sensors
        - drives actuator according to the control strategy
        - updates its enip server
        - logs the control strategy events (info, exceptions)
        """

        print("DEBUG: FP PLC1 enters main_loop.")
        print()
        logger = self.setup_logger("local_logger", "logs/plc1.log")

        count = 0
        while True:
            # get sensor1 value (tank liquid level) from self
            liquidlevel_tank = float(
                self.get(SENSOR1)
            )  # physical process simulation (sensor 1 reads value)
            print(
                "DEBUG PLC1 - liquid level of tank (SENSOR 1): %.5f" % liquidlevel_tank
            )
            self.send(
                SENSOR1, liquidlevel_tank, PLC1_ADDR
            )  # network process simulation (value of sensor 1 is stored as enip tag)
            self.set(
                SENSOR1, liquidlevel_tank
            )  # logical process simulation (value of sensor 1 is stored in the plc1 memory)

            if liquidlevel_tank <= TANK_M["LowerBound"]:
                """The only way we can reach this point is if we command line inject the value of the sensor to be lower than the lower bound of the tank"""

                print(
                    "INFO PLC1 - liquid level of tank (SENSOR 1) under LowerBound: %.2f <= %.2f -> close mv (ACTUATOR 1)."
                    % (liquidlevel_tank, TANK_M["LowerBound"])
                )
                logger.info(
                    "Liquid level of tank (SENSOR 1) under LowerBound: %.2f <= %.2f -> close mv (ACTUATOR 1)."
                    % (liquidlevel_tank, TANK_M["LowerBound"])
                )

                self.set(ACTUATOR1, 0)  # 0 (CLOSE) actuator mv
                try:

                    self.send(ACTUATOR1, 0, PLC1_ADDR)  # send the value to plc1
                    self.api_log(
                        str(datetime.datetime.now()),
                        PLC1_ADDR,
                        "SELF",
                        "ACTUATOR1-MV",
                        CPPPO_PORT,
                        "0 (CLOSE)",
                    )
                except:
                    pass

            # read from PLC2
            try:
                flowlevel = float(
                    requests.get(
                        f"http://{SERVER_ADDR}:{PORT}/get_value/{SENSOR2_2[0]}",
                        timeout=0.1,
                    ).text
                )

                print(
                    "DEBUG PLC2 - receive liquid level of flow (SENSOR 2): %f"
                    % flowlevel
                )

                self.api_log(
                    str(datetime.datetime.now()),
                    PLC2_ADDR,
                    PLC1_ADDR,
                    "SENSOR2-FL",
                    PORT,
                    flowlevel,
                )

                print("DEBUG PLC1 - receive flowlevel (SENSOR 2): %f" % flowlevel)

                try:
                    self.send(SENSOR2_1, flowlevel, PLC1_ADDR)
                    self.api_log(
                        str(datetime.datetime.now()),
                        PLC1_ADDR,
                        PLC2_ADDR,
                        "SENSOR2-FL",
                        CPPPO_PORT,
                        flowlevel,
                    )
                except:
                    self.api_log(
                        str(datetime.datetime.now()),
                        PLC1_ADDR,
                        PLC2_ADDR,
                        "SENSOR2-FL",
                        CPPPO_PORT,
                        "None",
                    )

                if flowlevel >= SENSOR2_THRESH:
                    print(
                        "INFO PLC1 - Flow level (SENSOR 2) over SENSOR2_THRESH:  %.2f >= %.2f -> close mv (ACTUATOR 1)."
                        % (flowlevel, SENSOR2_THRESH)
                    )
                    logger.info(
                        "Flow level (SENSOR 2) over SENSOR2_THRESH:  %.2f >= %.2f -> close mv (ACTUATOR 1)."
                        % (flowlevel, SENSOR2_THRESH)
                    )
                    self.set(ACTUATOR1, 0)  # 0 (CLOSE) actuator mv

                    try:
                        self.send(ACTUATOR1, 0, PLC1_ADDR)  # send the value to plc1
                        self.api_log(
                            str(datetime.datetime.now()),
                            PLC1_ADDR,
                            "SELF",
                            "ACTUATOR1-MV",
                            CPPPO_PORT,
                            "0 (CLOSE)",
                        )
                    except:
                        pass

                else:
                    logger.info(
                        "Flow level (SENSOR 2) under SENSOR2_THRESH:  %.2f < %.2f -> leave mv status (ACTUATOR 1)."
                        % (flowlevel, SENSOR2_THRESH)
                    )
            except Exception as e:
                logger.warning(
                    "Flow level (SENSOR 2) is not received. Program is unable to proceed properly"
                )
                self.api_log(
                    str(datetime.datetime.now()),
                    PLC2_ADDR,
                    PLC1_ADDR,
                    "SENSOR2-FL",
                    PORT,
                    "None",
                )

                flowlevel = 999

            # read from PLC3 then update
            try:
                liquidlevel_bottle = float(
                    requests.get(
                        f"http://{SERVER_ADDR}:{PORT}/get_value/{SENSOR3_3[0]}",
                        timeout=0.1,
                    ).text
                )

                print(
                    "DEBUG PLC1 - receive liquid level of bottle (SENSOR 3): %f"
                    % liquidlevel_bottle
                )
                self.api_log(
                    str(datetime.datetime.now()),
                    PLC3_ADDR,
                    PLC1_ADDR,
                    "SENSOR3-BL",
                    PORT,
                    liquidlevel_bottle,
                )

                # simulating sending to PLC3 (updating the value in the db)
                try:
                    self.send(SENSOR3_1, liquidlevel_bottle, PLC1_ADDR)
                    self.api_log(
                        str(datetime.datetime.now()),
                        PLC1_ADDR,
                        PLC3_ADDR,
                        "SENSOR3-BL",
                        CPPPO_PORT,
                        liquidlevel_bottle,
                    )

                except:
                    self.api_log(
                        str(datetime.datetime.now()),
                        PLC1_ADDR,
                        PLC3_ADDR,
                        "SENSOR3-BL",
                        CPPPO_PORT,
                        "None",
                    )

                if liquidlevel_bottle >= BOTTLE_M["UpperBound"]:
                    print(
                        "INFO PLC1 - Liquid level (SENSOR 3) over BOTTLE_M['UpperBound']:  %.2f >= %.2f -> close mv (ACTUATOR 1)."
                        % (liquidlevel_bottle, BOTTLE_M["UpperBound"])
                    )
                    logger.info(
                        "Liquid level (SENSOR 3) over BOTTLE_M['UpperBound']:  %.2f >= %.2f -> close mv (ACTUATOR 1)."
                        % (liquidlevel_bottle, BOTTLE_M["UpperBound"])
                    )
                    self.set(ACTUATOR1, 0)  # 0 (CLOSE) actuator mv
                    try:

                        self.send(ACTUATOR1, 0, PLC1_ADDR)  # send the value to plc1

                        self.api_log(
                            str(datetime.datetime.now()),
                            PLC1_ADDR,
                            "SELF",
                            "ACTUATOR1-MV",
                            CPPPO_PORT,
                            "0 (CLOSE)",
                        )
                    except:
                        pass

                elif (
                    liquidlevel_bottle < BOTTLE_M["UpperBound"]
                    and liquidlevel_tank > TANK_M["LowerBound"]
                ):
                    print(
                        "INFO PLC1 - Liquid level (SENSOR 3) under BOTTLE_M['UpperBound']: %.2f < %.2f ->  open mv (ACTUATOR 1)."
                        % (liquidlevel_bottle, BOTTLE_M["UpperBound"])
                    )
                    logger.info(
                        "Liquid level (SENSOR 3) under BOTTLE_M['UpperBound']: %.2f < %.2f -> open mv (ACTUATOR 1)."
                        % (liquidlevel_bottle, BOTTLE_M["UpperBound"])
                    )
                    self.set(ACTUATOR1, 1)  # OPEN actuator mv

                    self.api_log(
                        str(datetime.datetime.now()),
                        PLC3_ADDR,
                        PLC1_ADDR,
                        "ACTUATOR1-MV",
                        CPPPO_PORT,
                        "1 (OPEN)",
                    )
                    self.send(ACTUATOR1, 1, PLC1_ADDR)
            except Exception as e:
                logger.warning(
                    "Liquid level (SENSOR 3) is not received. Program is unable to proceed properly", e
                )
                liquidlevel_bottle = 999
            motor_status = int(self.get(ACTUATOR1))

            if os.path.isfile("trigger.txt"):
                # Collect relevant process measurements
                print("INFO PLC1 - Trigger file found. Collecting measurements")
                self.store_values(
                    liquidlevel_tank, flowlevel, liquidlevel_bottle, motor_status, count
                )
                count = 1
                time.sleep(PLC_PERIOD_SEC)

    def _stop(self):
        print("DEBUG FP PLC3 shutdown")
        return super()._stop()


if __name__ == "__main__":
    plc1 = FPPLC1(
        name="plc1",
        state=STATE,
        protocol=PLC1_PROTOCOL,
        memory=PLC1_DATA,
        disk=PLC1_DATA,
    )