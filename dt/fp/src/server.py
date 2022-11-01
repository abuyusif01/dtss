from flask import Flask
import sqlite3

from utils import PORT, SERVER_ADDR


SCHEMA = "fp_db.sqlite"
TABLE = "fp_table"


class FlaskAppWrapper(object):
    def __init__(self, app, con, **configs):
        self.app = app
        self.configs(**configs)
        self.con = sqlite3.connect(SCHEMA, check_same_thread=False)

    def configs(self, **configs):
        for config, value in configs:
            self.app.config[config.upper()] = value

    def add_endpoint(
        self,
        endpoint=None,
        endpoint_name=None,
        handler=None,
        methods=["GET"],
        *args,
        **kwargs
    ):
        self.app.add_url_rule(
            endpoint,
            endpoint_name,
            handler,
            methods=methods,
            *args,
            **kwargs,
        )

    def run(self, **kwargs):
        self.app.run(**kwargs)


flask_app = Flask(__name__)

con = None
app = FlaskAppWrapper(flask_app, con)


def get_value(tag_name):
    try:
        return str(
            app.con.execute(
                "SELECT value FROM {} WHERE name = '{}'".format(TABLE, tag_name)
            ).fetchone()[0]
        )
    except Exception as e:
        return str(e)


def set_value(tag_name, tag_value):
    try:
        cur = app.con.cursor()
        cur.execute(
            "UPDATE {} SET value = {} WHERE name = '{}'".format(
                TABLE,
                tag_value,
                tag_name,
            )
        )
        app.con.commit()
        return "success"
    except Exception as e:
        return str(e)


def test():
    return "test"


# Add endpoint for the action function
app.add_endpoint(
    "/get_value/<string:tag_name>",  # route
    "get_value",  # route name
    get_value,  # handler
    methods=["GET"],
)

app.add_endpoint(
    "/set_value/<string:tag_name>/<string:tag_value>",  # route
    "set_value",  # route name
    set_value,  # handler
    methods=["GET"],
)

app.add_endpoint(
    "/test",  # route
    "test",  # route name
    test,  # handler
    methods=["GET"],
)

# try:
app.run(host=SERVER_ADDR, port=PORT, debug=True)
# except Exception as e:
# app.run(host="localhost", port=8080, debug=True)

