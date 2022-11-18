from flask import (
    Flask,
    Response,
    request,
)

app = Flask(__name__)


class Utils:
    """
    This certainly not the optimal way to do this, but it works.
    """

    def get_lines(fp, line_number):
        return [x for i, x in enumerate(fp) if i == line_number]


# take a line number and return the line from the log file
@app.route("/get_data", methods=["GET"])
def gen_table() -> Response:

    values = request.args.to_dict()
    line_number = int(values["line_number"])
    file_name = values["file_name"]

    try:
        """
        since we dont wanna have a broken pipe or typeError
        we end up using generators to yeild the data as well as
        safely catch all exceptions
        """

        def generate() -> Exception:
            try:
                with open(file_name, "r") as f:
                    yield str(Utils.get_lines(f, line_number))[2:-4]
            except Exception as e:
                yield str(e)

    except Exception as e:
        return e
    return Response(generate())


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="localhost")
