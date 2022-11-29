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

  


# take a line number and return the line from the log file

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="localhost")
