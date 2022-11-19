from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import warnings


app = Flask(__name__)

CORS(app)
warnings.filterwarnings("ignore")  # To ignore any warnings

cols = ["tank_liquidlevel", "flowlevel", "bottle_liquidlevel", "motor_status"]
# get condition


# display plc log from file
@app.route("/plc_log", methods=["GET"])
def plc_log():
    """this display any file by given its location"""
    name = request.args.get("name")

    with open(name, "r") as f:
        plc_log = f.read()
    return str(plc_log)


# get status of plc from the train data
@app.route("/get_status", methods=["GET"])
def get_status():

    # if request.get_json():
    #     try:
    #         model_name = request.get_json()["model_name"]
    #         tank_liquidlevel = request.get_json()["tank_liquidlevel"]
    #         flowlevel = request.get_json()["flowlevel"]
    #         bottle_liquidlevel = request.get_json()["bottle_liquidlevel"]
    #         motor_status = request.get_json()["motor_status"]

    #         model = pickle.load(open("models/" + model_name + ".pkl", "rb"))

    #         return jsonify(
    #             {
    #                 "result": str(
    #                     model.predict(
    #                         [
    #                             [
    #                                 tank_liquidlevel,
    #                                 flowlevel,
    #                                 bottle_liquidlevel,
    #                                 motor_status,
    #                             ]
    #                         ]
    #                     )
    #                 )[
    #                     2:-2
    #                 ]  # remove some characters [] and ''
    #             }
    #         )
    #     except Exception as e:
    #         return jsonify({"error": str(e)[1:-1] + " not given"})
    # else:
    values = request.args.to_dict()
    print(values)
    try:
        model = pickle.load(open("models/" + values["model_name"] + ".pkl", "rb"))
        return jsonify(
            {
                "result": str(
                    model.predict(
                        [
                            [
                                float(values["tank_liquidlevel"]),
                                float(values["flowlevel"]),
                                float(values["bottle_liquidlevel"]),
                                float(values["motor_status"]),
                            ]
                        ]
                    )
                )[
                    2:-2
                ]  # remove some characters [] and ''
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)[1:-1] + " not given"})


port = 8001
app.run(debug=True, port=port)
