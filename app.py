from websocket import WebSocketApp
from ast import literal_eval
import threading
from flask import Flask, render_template, Response
from datetime import datetime
from json import loads, dumps
import redis
from time import sleep

app = Flask(__name__)
red = redis.StrictRedis()


def socket_controller():
    global button_data
    try:
        with open("lowest.json", "r") as f:
            button_data = {"lowestTime": loads(f.read())}
    except FileNotFoundError:
        button_data = {"lowestTime": {"value": 60, "time": ""}}

    def received(socket, message):
        message_dict = literal_eval(message)["payload"]  # Convert string to dictionary and strip unneeded data.
        if message_dict["seconds_left"] < button_data["lowestTime"]["value"]:
            # Lowest Time
            button_data["lowestTime"]["value"] = int(message_dict["seconds_left"])
            button_data["lowestTime"]["time"] = message_dict["now_str"][-8:].replace("-", ":")
            with open("lowest.json", "w") as f:
                f.write(dumps(button_data["lowestTime"]))
        button_data["clicks"] = int(message_dict["participants_text"].replace(",", ""))
        button_data["clicks_second"] = round((button_data["clicks"] / (datetime.today() -
                                              datetime(2015, 4, 1, 17, 00, 00)).total_seconds()), 3)
        red.publish("main", dumps(button_data))
    socket = WebSocketApp("wss://wss.redditmedia.com/thebutton?h=18f357d4d3b377018523f3981d36f2c63f976873&e=1428054735",
                          on_message=received)
    socket.run_forever()


@app.route("/")
def home():
    return render_template("home.html", data=button_data)


@app.route("/stream")
def data_stream():
    def stream():
        pubsub = red.pubsub()
        pubsub.subscribe("main")
        for x in pubsub.listen():
            if x["data"] != 1:
                yield "data: " + x["data"].decode("utf-8") + "\n\n"
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    threading.Thread(target=socket_controller).start()
    app.run(debug=True, use_reloader=False, threaded=True)