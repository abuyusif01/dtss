from flask import (
    Flask,
    Response,
    request,
)

app = Flask(__name__)


class Utils:
    # read file by line numbers
    """
    This certainly not the optimal way to do this, but it works.
    """

    def get_lines(fp, line_number):
        return [x for i, x in enumerate(fp) if i == line_number ]


# take a line number and return the line from the log file
@app.route("/gen_table", methods=["GET"])
def gen_table():
    line_number = int(request.args.get("line_number"))
    try:
        def generate():
            try:
                with open("api_log.csv", "r") as f:
                    yield str(Utils.get_lines(f, line_number)).replace("\\n", "")
            except Exception as e:
                yield str(e)

    except:
        return "generate failed"
    return Response(generate())


if __name__ == "__main__":
    app.run(debug=True)
