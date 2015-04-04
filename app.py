from ws4py.client.threadedclient import WebSocketClient
from ast import literal_eval
import threading
from flask import Flask, render_template
import datetime
from json import loads, dumps
from time import sleep
from sys import platform

if platform == "win32":  # If running locally.
    lowestfile = "lowest.json"; flairfile = "flair.json"; currentflairfile = "currentflair.json"; historicfile = "historic.json"
else:  # If running in production.
    lowestfile = "/var/www/FlaskApp/lowest.json"; flairfile = "/var/www/FlaskApp/flair.json"; currentflairfile = "/var/www/FlaskApp/currentflair.json"; historicfile = "/var/www/FlaskApp/historic.json"

starttime = datetime.datetime.utcnow().strftime("%d %b %H:%M:%S")

with open(lowestfile, "r") as f:
    button_data = {"lowestTime": {"1m": 0, "10m": 0, "60m": 0, "all": loads(f.read())},
                   "clicks_second": {"1m": 0, "10m": 0, "60m": 0, "all": 0},
                   "clicks": {"1m": 0, "10m": 0, "60m": 0, "all": 0}}

with open(flairfile, "r") as f:
    button_data["flairs"] = loads(f.read())

with open(currentflairfile, "r") as f:
    button_data["current_flair"] = loads(f.read())

with open(historicfile, "r") as f:
    historic_data = loads(f.read())

app = Flask(__name__)


def socket_controller():
    global button_data

    class Socket(WebSocketClient):
        def received_message(self, message):
            message_dict = literal_eval(str(message))["payload"]
            if message_dict["seconds_left"] < button_data["lowestTime"]["all"]["clicks"]:
                historic_data["lowestTime"][str(int(message_dict["seconds_left"]))] =  \
                    datetime.datetime.utcnow().strftime("%d %b ") + message_dict["now_str"][-8:].replace("-", ":")
                button_data["lowestTime"]["all"]["clicks"] = int(message_dict["seconds_left"])
                button_data["lowestTime"]["all"]["time"] = datetime.datetime.utcnow().strftime("%d %b ") + \
                                                           message_dict["now_str"][-8:].replace("-", ":")
                with open(lowestfile, "w") as f:
                    f.write(dumps(button_data["lowestTime"]["all"]))
            button_data["clicks"]["all"] = int(message_dict["participants_text"].replace(",", ""))

    socket = Socket("wss://wss.redditmedia.com/thebutton?h=78a51e27e104970daca337e21ca88869b5de0f7a&e=1428166663")
    socket.connect()
    socket.run_forever()


def calculate_averages():
    while True:
        button_data["clicks_second"]["all"] = round((button_data["clicks"]["all"] / (datetime.datetime.today() -
                                                     datetime.datetime(2015, 4, 1, 17, 00, 00)).total_seconds()), 3)
        if len(historic_data["click_count"]) >= 12:
            button_data["clicks_second"]["1m"] = round((historic_data["click_count"][-1] - historic_data["click_count"][-12]) / float(60), 3)
            button_data["clicks"]["1m"] = historic_data["click_count"][-1] - historic_data["click_count"][-12]
        if len(historic_data["click_count"]) >= 120:
            button_data["clicks_second"]["10m"] = round((historic_data["click_count"][-1] - historic_data["click_count"][-120]) / float(600), 3)
            button_data["clicks"]["10m"] = historic_data["click_count"][-1] - historic_data["click_count"][-120]
        if len(historic_data["click_count"]) == 720:
            button_data["clicks_second"]["60m"] = round((historic_data["click_count"][-1] - historic_data["click_count"][-720]) / float(3600), 3)
            button_data["clicks"]["60m"] = historic_data["click_count"][-1] - historic_data["click_count"][-720]
        sleep(5)


def historic_append():
    sleep(10)
    while True:
        historic_data["click_count"].append(button_data["clicks"]["all"])
        if len(historic_data["click_count"]) > 720:
            historic_data["click_count"].pop(0)
        with open(historicfile, "w") as f:
            f.write(dumps(historic_data))
        sleep(5)


def flair_data():
    sleep(10)
    while True:
        with open(flairfile, "r") as f:
            button_data["flairs"] = loads(f.read())
        with open(currentflairfile, "r") as f:
            button_data["current_flair"] = loads(f.read())
        sleep(150)


@app.route("/")
def home():
    return render_template("home.html", data=button_data, time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])


@app.route("/times")
def times():
    return render_template("times.html", data=historic_data, time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])


@app.route("/donate")
def donate():
    return render_template("donate.html", time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])

if __name__ == "__main__":
    threading.Thread(target=socket_controller).start()
    threading.Thread(target=historic_append).start()
    threading.Thread(target=calculate_averages).start()
    threading.Thread(target=flair_data).start()
    app.run(debug=True, use_reloader=False, threaded=True)