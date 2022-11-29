import requests
import json
import pandas as pd
import os
import time
import warnings
import mysql.connector as mysql
from mysql.connector import Error

SCHEMA = "http"

class Utils:

    try:
        connection = mysql.connect(
            host="localhost",
            user="abuyusif01",
            password="1111",
            database="dtss",
            autocommit=True, # this will force commit after each query, eg select and update
        )

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = str(cursor.fetchall())[3:-4]
            print("You're connected to database:", record)
    except Error as e:
        print("Error while connecting to MySQL", e)

    def db_exec(self, query) -> str:
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        return str(result)

    def get_logs(
        self,
        host,
        port,
        file_name,
        line_number,
    ) -> json:

        url = f"{SCHEMA}://{host}:{port}/get_data"

        return json.loads(
            requests.get(
                url,
                params={
                    "file_name": file_name,
                    "line_number": line_number,
                },
            ).text.replace("'", '"')
        )

    def get_status(
        self,
        host,
        port,
        **args,
    ) -> json:

        tank_liquidlevel = args["tank_liquidlevel"]
        flowlevel = args["flowlevel"]
        bottle_liquidlevel = args["bottle_liquidlevel"]
        motor_status = args["motor_status"]
        model_name = args["model_name"]

        url = f"{SCHEMA}://{host}:{port}/get_status"

        return json.loads(
            requests.get(
                url,
                params={
                    "tank_liquidlevel": tank_liquidlevel,
                    "flowlevel": flowlevel,
                    "bottle_liquidlevel": bottle_liquidlevel,
                    "motor_status": motor_status,
                    "model_name": model_name,
                },
            ).text.replace("'", '"')
        )

    warnings.filterwarnings("ignore")
    cols = ["Timestamp", "From", "To", "Label", "Port", "Value", "Status"]


if __name__ == "__main__":

    Utils = Utils()
    i = 0
    while True:
        df = pd.DataFrame()  # reset dataframe
        logs = Utils.get_logs("localhost", 8000, "api_log.csv", i)
        measurements = Utils.get_logs(
            "localhost", 8000, "measurements.csv", (int(i / 4) + 1)
        )
        status = Utils.get_status(
            "localhost",
            8001,
            flowlevel=measurements["flowlevel"],
            tank_liquidlevel=measurements["tank_liquidlevel"],
            bottle_liquidlevel=measurements["bottle_liquidlevel"],
            motor_status=measurements["motor_status"],
            model_name="rf",
        )

        df = df.append(
            {
                "Timestamp": logs["Timestamp"],
                "From": logs["From"],
                "To": logs["To"],
                "Label": logs["Label"],
                "Port": logs["Port"],
                "Value": logs["Value"],
                "Status": status["result"],
            },
            ignore_index=True,
        )

        i += 1

        time.sleep(1)
        if df["Status"].iloc[-1] != "Normal":

            if (
                df["Status"].iloc[-1] == "Command Injection TL"
                or df["Status"].iloc[-1] == "Command Injection TH"
            ):
                temp = int(
                    Utils.db_exec("select value from attacks where name='Injection';")[
                        1:-2
                    ]
                )
                temp += 1
                query = f"UPDATE attacks SET value = {temp} WHERE name = 'Injection';"
                Utils.db_exec(query)
                Utils.connection.commit()

                # add one to db count
                print("Command line injection detected and updated in the database")
                print("Attack count: ", temp)

            elif df["Status"].iloc[-1] == "DoS":

                temp = int(
                    Utils.db_exec("select value from attacks where name='Dos';")[1:-2]
                )
                temp += 1
                query = f"UPDATE attacks SET value = {temp} WHERE name = 'Dos';"
                Utils.db_exec(query)
                Utils.connection.commit()

                # add one to db count
                print("Dos attack detected and updated in the database")
                print("current dos count: ", temp)

        df.to_csv(
            "table.csv",
            index=False,
            mode="a",
            header=not os.path.exists("table.csv"),
        )
