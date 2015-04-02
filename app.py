from ws4py.client.threadedclient import WebSocketClient
from ast import literal_eval
import threading
from flask import Flask, render_template
import datetime
from json import loads, dumps
import redis
from time import sleep

try:
    with open("lowest.json", "r") as f:
        button_data = {"lowestTime": loads(f.read()), "clicks_second": {"1m": 0, "10m": 0, "60m": 0, "all": 0},
                       "clicks": 0}
except IOError:
        button_data = {"lowestTime": {"value": 60, "time": ""}, "clicks_second": {"1m": 0, "10m": 0, "60m": 0,
                                                                                  "all": 0}, "clicks": 0}

app = Flask(__name__)
red = redis.StrictRedis()


def socket_controller():
    global button_data

    class Socket(WebSocketClient):
        def received_message(self, message):
            message_dict = literal_eval(str(message))["payload"]  # Convert string to dictionary and strip unneeded data.
            if message_dict["seconds_left"] < button_data["lowestTime"]["value"]:
                button_data["lowestTime"]["value"] = int(message_dict["seconds_left"])
                button_data["lowestTime"]["time"] = message_dict["now_str"][-8:].replace("-", ":")
                with open("lowest.json", "w") as f:
                    f.write(dumps(button_data["lowestTime"]))
            button_data["clicks"] = int(message_dict["participants_text"].replace(",", ""))
            button_data["clicks_second"]["all"] = round((button_data["clicks"] / (datetime.datetime.today() -
                                                         datetime.datetime(2015, 4, 1, 17, 00, 00)).total_seconds()), 3)
        red.publish("main", dumps(button_data))
    socket = Socket("wss://wss.redditmedia.com/thebutton?h=18f357d4d3b377018523f3981d36f2c63f976873&e=1428054735")
    socket.connect()
    socket.run_forever()


def one_minute_average():
    global button_data
    while True:
        start = button_data["clicks"]
        sleep(60)
        end = button_data["clicks"]
        button_data["clicks_second"]["1m"] = round((end - start) / 60, 3)


def ten_minute_average():
    global button_data
    while True:
        start = button_data["clicks"]
        sleep(600)
        end = button_data["clicks"]
        button_data["clicks_second"]["10m"] = round((end - start) / 600, 3)


def sixty_minute_average():
    global button_data
    while True:
        start = button_data["clicks"]
        sleep(3600)
        end = button_data["clicks"]
        button_data["clicks_second"]["60m"] = round((end - start) / 3600, 3)


@app.route("/")
def home():
    return render_template("home.html", data=button_data, time=datetime.datetime.utcnow().strftime("%H:%M:%S"))

if __name__ == "__main__":
    threading.Thread(target=socket_controller).start()
    threading.Thread(target=one_minute_average).start()
    threading.Thread(target=ten_minute_average).start()
    threading.Thread(target=sixty_minute_average).start()
    app.run(debug=True, use_reloader=False, threaded=True)