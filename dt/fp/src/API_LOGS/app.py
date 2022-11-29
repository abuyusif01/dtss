from flask import Flask, Response, request
from flask_cors import CORS
from itertools import takewhile, repeat
from utils import Utils as _utils


app = Flask(__name__)

CORS(app)


class Utils:
    """
    This certainly not the optimal way to do this, but it works.
    """

    def read_last_line(file_name) -> str:
        with open(file_name, "r") as f:
            return f.readlines()[-1]

    def get_lines(fp, line_number):
        return [x for i, x in enumerate(fp) if i == line_number]

    def get_total_lines(filename):
        f = open(filename, "rb")
        bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
        return sum(buf.count(b"\n") for buf in bufgen)


@app.route("/gen_table", methods=["GET"])
def gen_table() -> Response:
    try:
        """
        since we dont wanna have a broken pipe or typeError
        we end up using generators to yeild the data as well as
        safely catch all exceptions
        """
        file_name = request.args.get("file_name")

        def generate() -> Exception:

            temp = str(Utils.read_last_line(file_name))[2:-1].split(",")
            print(temp)

            yield str(
                {
                    "Timestamp": temp[0],
                    "From": temp[1],
                    "To": temp[2],
                    "Label": temp[3],
                    "Port": temp[4],
                    "Value": temp[5],
                    "Status": temp[6],
                }
            )

    except Exception as e:
        return e
    return Response(generate())


# take a line number and return the line from the log file
@app.route("/get_data", methods=["GET"])
def get_data() -> Response:

    values = request.args.to_dict()

    if len(values) < 2:
        file_name = "api_log.csv"
        line_number = 0
    else:
        file_name = values["file_name"]
        line_number = int(values["line_number"])

    try:
        """
        since we dont wanna have a broken pipe or typeError
        we end up using generators to yeild the data as well as
        safely catch all exceptions
        """

        def generate() -> Exception:
            try:
                with open(file_name, "r") as f:

                    temp = str(Utils.get_lines(f, line_number))[2:-4].split(",")
                    if file_name == "api_log.csv":
                        yield str(
                            {
                                "Timestamp": temp[0],
                                "From": temp[1],
                                "To": temp[2],
                                "Label": temp[3],
                                "Port": temp[4],
                                "Value": temp[5],
                            }
                        )
                    else:
                        yield str(
                            {
                                "Timestamp": temp[0],
                                "tank_liquidlevel": temp[1],
                                "flowlevel": temp[2],
                                "bottle_liquidlevel": temp[3],
                                "motor_status": temp[4],
                            }
                        )

            except Exception as e:
                yield str(e)

    except Exception as e:
        return e
    return Response(generate())


@app.route("/card_info", methods=["GET"])
def card_info() -> Response:
    utils = _utils()

    """
    get total lines, then calculate how many attacks are there and get percentage
    number of attacks from db
    """
    network_count = int(
        utils.db_exec("select value from attacks where name='Dos';")[1:-2]
    )
    injection_cont = int(
        utils.db_exec("select value from attacks where name='Injection';")[1:-2]
    )
    total_lines = Utils.get_total_lines("table.csv")
    network_percent = (network_count / total_lines) * 100
    injection_percent = (injection_cont / total_lines) * 100

    return str(
        {
            "network_count": network_count,
            "network_percent": network_percent,
            "injection_count": injection_cont,
            "injection_percent": injection_percent,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="localhost")
