from flask import Flask, Response, request
from flask_cors import CORS
from itertools import takewhile, repeat
from utils import Utils as _utils


app = Flask(__name__)

CORS(app)


@app.route("/term_info", methods=["GET"])
def term_info() -> str:
    utils = _utils()
    success = int(utils.db_fetchone("select success from commands;")[2:-3])
    pending = int(utils.db_fetchone("select pending from commands;")[2:-3])
    failed = int(utils.db_fetchone("select failed from commands;")[2:-3])

    count = success + failed + pending

    x = [x if x != 0 else 1 for x in [success]]
    y = [x if x != 0 else 1 for x in [failed]]
    z = [x if x != 0 else 1 for x in [pending]]

    x = str(x)[1:-1]
    y = str(y)[1:-1]
    z = str(z)[1:-1]

    success_percent = (int(x) / int(count)) * 100
    failed_percent = (int(y) / int(count)) * 100
    pending_percent = (int(z) / int(count)) * 100

    return str(
        {
            "success_count": success,
            "success_percent": success_percent,
            "failed_count": failed,
            "failed_percent": failed_percent,
            "pending_count": pending,
            "pending_percent": pending_percent,
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=True)
