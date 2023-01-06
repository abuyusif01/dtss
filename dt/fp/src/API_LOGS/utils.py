import requests
import json
import pandas as pd
import os
import time
import warnings
import mysql.connector as mysql
from mysql.connector import Error
from datetime import datetime
import hashlib
from dotenv import load_dotenv

_env = load_dotenv()
SCHEMA = os.getenv("SCHEMA")
EMAIL_URL = os.getenv("EMAIL_URL")
EMAIL_PORT = os.getenv("EMAIL_PORT")
ML_URL = os.getenv("ML_URL")
ML_PORT = os.getenv("ML_PORT")
LOG_URL = os.getenv("LOG_URL")
LOG_PORT = os.getenv("LOG_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB = os.getenv("DB")


class Utils:

    try:
        connection = mysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB,
            autocommit=True,  # this will force commit after each query, eg select and update
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

    def db_fetchone(self, query) -> str:
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        return str(result)

    def db_fetchall(self, query) -> list:
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        return result

    def get_logs(
        self,
        host,
        port,
        file_name,
        line_number,
    ) -> json:

        url = f"{SCHEMA}://{host}:{port}/get_data"

        try:
            return json.loads(
                requests.get(
                    url,
                    params={
                        "file_name": file_name,
                        "line_number": line_number,
                    },
                ).text.replace("'", '"')
            )
        except Exception as e:
            return e  # update this as server failure

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

        try:
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
        except Exception as e:
            return e

    warnings.filterwarnings("ignore")
    cols = ["Timestamp", "From", "To", "Label", "Port", "Value", "Status"]


if __name__ == "__main__":

    Utils = Utils()
    total_count = 0
    injection_count = 0
    network_count = 0

    while True:
        df = pd.DataFrame()  # reset dataframe
        logs = Utils.get_logs(
            LOG_URL,
            LOG_PORT,
            "api_log.csv",
            0,
        )
        measurements = Utils.get_logs(
            LOG_URL,
            LOG_PORT,
            "measurements.csv",
            0,
        )

        status = Utils.get_status(
            ML_URL,
            ML_PORT,
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

        total_count = int(
            Utils.db_fetchone("select value from attacks where name = 'Count';")[1:-2]
        )

        total_count += 1
        query = f"UPDATE attacks SET value = {total_count} WHERE name = 'Count';"
        Utils.db_fetchone(query)
        Utils.connection.commit()

        time.sleep(0.5)
        if df["Status"].iloc[-1] != "Normal":

            if (
                df["Status"].iloc[-1] == "Command Injection TL"
                or df["Status"].iloc[-1] == "Command Injection TH"
            ):
                temp = int(
                    Utils.db_fetchone(
                        "select value from attacks where name='Injection';"
                    )[1:-2]
                )
                temp += 1
                injection_count += 1
                query = f"UPDATE attacks SET value = {temp} WHERE name = 'Injection';"
                Utils.db_fetchone(query)
                Utils.connection.commit()

                """we are trying the best we can to avoid a false positive """
                if injection_count == 15:
                    now = str(datetime.now()).split(".")[0]
                    id_hash = hashlib.sha256(str(now).encode("utf-8")).hexdigest()
                    description = "Command injection attack detected"
                    trigger = "Internal"
                    priority = "High"
                    query = f"INSERT INTO events values ('{now}', '{id_hash}', '{description}', '{trigger}', '{priority}');"

                    Utils.db_fetchone(query)
                    Utils.connection.commit()
                    network_count = 0

                    try:
                        # get all emails from db
                        emails = Utils.db_fetchall("select email from users;")
                        emails = [str(x)[2:-3] for x in emails]

                        for email in emails:
                            _hash = id_hash[:8]  # take first 8 characters of hash
                            _subject = description
                            _username = email.split("@")[0]
                            _time = now
                            _category_title = "Commandline Injection"
                            _severity_color = "red"
                            _severity = "High"

                            data = {
                                "recv_email": email,
                                "subject": _subject,
                                "hash": _hash,
                                "username": _username,
                                "time": _time,
                                "category_title": _category_title,
                                "severity_color": _severity_color,
                                "severity": _severity,
                                "site_url": "abuyusif01.github.io",
                            }

                            url = f"{SCHEMA}://{EMAIL_URL}:{EMAIL_PORT}/send_mail"
                            headers = {
                                "Content-type": "application/json",
                                "Accept": "text/plain",
                            }
                            role = Utils.db_fetchone(
                                "select role from users where email = '{}';".format(
                                    email
                                )
                            )
                            print("role: ", role)
                            if role == "admin" or role == "Admin":
                                try:
                                    req = requests.post(
                                        url=url,
                                        json=data,
                                        headers=headers,
                                    )
                                except Exception as e:
                                    print("Error sending email: ", e)

                    except Exception as e:
                        print("Error sending email final: ", e)

                # add one to db count
                print("Command line injection detected and updated in the database")
                print("Attack count: ", temp)
                print("count injection: ", injection_count)

            elif df["Status"].iloc[-1] == "DoS":

                temp = int(
                    Utils.db_fetchone("select value from attacks where name='Dos';")[
                        1:-2
                    ]
                )
                temp += 1
                network_count += 1
                query = f"UPDATE attacks SET value = {temp} WHERE name = 'Dos';"
                Utils.db_fetchone(query)
                Utils.connection.commit()

                """we are trying the best we can to avoid a false positive """
                if network_count == 15:
                    now = str(datetime.now()).split(".")[0]
                    id_hash = hashlib.sha256(str(now).encode("utf-8")).hexdigest()
                    description = "Dos attack detected"
                    trigger = "Internal"
                    priority = "High"
                    network_count = 0

                    try:
                        # get all emails from db
                        emails = Utils.db_fetchall("select email from users;")
                        emails = [str(x)[2:-3] for x in emails]

                        for email in emails:
                            _hash = id_hash[:8]  # take first 8 characters of hash
                            _subject = description
                            _username = email.split("@")[0]
                            _time = now
                            _category_title = "DDOSs Attack"
                            _severity_color = "red"
                            _severity = "High"

                            data = {
                                "recv_email": email,
                                "subject": _subject,
                                "hash": _hash,
                                "username": _username,
                                "time": _time,
                                "category_title": _category_title,
                                "severity_color": _severity_color,
                                "severity": _severity,
                                "site_url": "abuyusif01.github.io",
                            }

                            url = f"{SCHEMA}://{EMAIL_URL}:{EMAIL_PORT}/send_mail"
                            headers = {
                                "Content-type": "application/json",
                                "Accept": "text/plain",
                            }
                            # email only admin

                            role = str(
                                Utils.db_fetchone(
                                    "select role from users where email = '{}';".format(
                                        email
                                    )
                                )
                            )

                            if "admin" in role or "Admin" in role:
                                try:
                                    req = requests.post(
                                        url=url,
                                        json=data,
                                        headers=headers,
                                    )
                                except Exception as e:
                                    print("Error sending email:", e)
                    except Exception as e:
                        print(e)
                    query = f"INSERT INTO events values ('{now}', '{id_hash}', '{description}', '{trigger}', '{priority}');"
                    Utils.db_fetchone(query)
                    Utils.connection.commit()

                # add one to db count
                print("Dos attack detected and updated in the database")
                print("current dos count: ", temp)
                print("count dos: ", network_count)

        df.to_csv(
            "table.csv",
            index=False,
            mode="w",
            header=not os.path.exists("table.csv"),
        )
