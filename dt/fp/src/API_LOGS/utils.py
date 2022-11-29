import requests
import json
import pandas as pd
import os
import time
import warnings

SCHEMA = "http"


def get_logs(
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


i = 0
while True:
    df = pd.DataFrame()  # reset dataframe
    logs = get_logs("localhost", 8000, "api_log.csv", i)
    measurements = get_logs("localhost", 8000, "measurements.csv", (int(i / 4) + 1))
    status = get_status(
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
    df.to_csv(
        "output.csv", index=False, mode="a", header=not os.path.exists("output.csv")
    )
