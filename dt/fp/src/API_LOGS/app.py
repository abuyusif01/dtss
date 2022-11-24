from flask import Flask, Response, request
from flask_cors import CORS
from itertools import takewhile, repeat
import os


app = Flask(__name__)

CORS(app)


class Utils:
    """
    This certainly not the optimal way to do this, but it works.
    """

    def get_lines(fp, line_number):
        return [x for i, x in enumerate(fp) if i == line_number]

    def get_total_lines(filename):
        f = open(filename, "rb")
        bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
        return sum(buf.count(b"\n") for buf in bufgen)

    def exec(command):
        return os.popen(command).read()


# take a line number and return the line from the log file
@app.route("/get_data", methods=["GET"])
def gen_table() -> Response:

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


# route to execute system commands
@app.route("/exec", methods=["GET"])
def exec() -> Response:
    values = request.args.to_dict()
    if len(values) < 1:
        return "No command provided"
    else:
        command = values["command"]
        return Utils.exec(command)


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="localhost")
