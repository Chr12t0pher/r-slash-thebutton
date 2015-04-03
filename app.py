from ws4py.client.threadedclient import WebSocketClient
from ast import literal_eval
import threading
from flask import Flask, render_template
import datetime
from json import loads, dumps
from time import sleep

starttime = datetime.datetime.utcnow().strftime("%d %b %H:%M:%S")

try:
    with open("lowest.json", "r") as f:
        button_data = {"lowestTime": {"1m": 0, "10m": 0, "60m": 0, "all": loads(f.read())},
                       "clicks_second": {"1m": 0, "10m": 0, "60m": 0, "all": 0},
                       "clicks": {"1m": 0, "10m": 0, "60m": 0, "all": 0}}
        historic_data = {"click_count": []}
except IOError:
        button_data = {"lowestTime": {"1m": 0, "10m": 0, "60m": 0, "all": {"clicks": 60, "time": ""}},
                       "clicks_second": {"1m": 0, "10m": 0, "60m": 0, "all": 0},
                       "clicks": {"1m": 0, "10m": 0, "60m": 0, "all": 0}}
        historic_data = {"click_count": []}

app = Flask(__name__)


def socket_controller():
    global button_data

    class Socket(WebSocketClient):
        def received_message(self, message):
            message_dict = literal_eval(str(message))["payload"]
            if message_dict["seconds_left"] < button_data["lowestTime"]["all"]["clicks"]:
                button_data["lowestTime"]["all"]["clicks"] = int(message_dict["seconds_left"])
                button_data["lowestTime"]["all"]["time"] = message_dict["now_str"][-8:].replace("-", ":")
                with open("lowest.json", "w") as f:
                    f.write(dumps(button_data["lowestTime"]["all"]))
            button_data["clicks"]["all"] = int(message_dict["participants_text"].replace(",", ""))

    socket = Socket("wss://wss.redditmedia.com/thebutton?h=18f357d4d3b377018523f3981d36f2c63f976873&e=1428054735")
    socket.connect()
    socket.run_forever()


def calculate_averages():
    while True:
        button_data["clicks_second"]["all"] = round((button_data["clicks"]["all"] / (datetime.datetime.today() -
                                                     datetime.datetime(2015, 4, 1, 17, 00, 00)).total_seconds()), 3)
        if len(historic_data["click_count"]) >= 12:
            button_data["clicks_second"]["1m"] = round(((historic_data["click_count"][-1] - historic_data["click_count"][-12]) / 60), 3)
            button_data["clicks"]["1m"] = historic_data["click_count"][-1] - historic_data["click_count"][-12]
        if len(historic_data["click_count"]) >= 120:
            button_data["clicks_second"]["10m"] = round(((historic_data["click_count"][-1] - historic_data["click_count"][-120]) / 600), 3)
            button_data["clicks"]["10m"] = historic_data["click_count"][-1] - historic_data["click_count"][-120]
        if len(historic_data["click_count"]) == 720:
            button_data["clicks_second"]["60m"] = round(((historic_data["click_count"][-1] - historic_data["click_count"][-720]) / 3600), 3)
            button_data["clicks"]["60m"] = historic_data["click_count"][-1] - historic_data["click_count"][-720]
        sleep(5)


def historic_append():
    sleep(10)
    while True:
        historic_data["click_count"].append(button_data["clicks"]["all"])
        if len(historic_data["click_count"]) > 720:
            historic_data.pop(0)
        sleep(5)


@app.route("/")
def home():
    return render_template("home.html", data=button_data, time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])

if __name__ == "__main__":
    threading.Thread(target=socket_controller).start()
    threading.Thread(target=historic_append).start()
    threading.Thread(target=calculate_averages).start()
    app.run(debug=True, use_reloader=False, threaded=True)