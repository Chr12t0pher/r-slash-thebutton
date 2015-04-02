from websocket import WebSocketApp
from ast import literal_eval
from multiprocessing import Process, Manager
from flask import Flask, render_template

app = Flask(__name__)


def socket_controller(dictionary):
    print(dictionary)

    def received(socket, message):
        message_dict = literal_eval(message)["payload"]
        if message_dict["seconds_left"] <= dictionary["lowestTime"]["value"]:
            print(message_dict["seconds_left"])
            print("^^^^ LOWEST TIME!")
            dictionary["lowestTime"]["value"] = message_dict["seconds_left"]
            dictionary["lowestTime"]["time"] = message_dict["now_str"][-8:]

    socket = WebSocketApp("wss://wss.redditmedia.com/thebutton?h=18f357d4d3b377018523f3981d36f2c63f976873&e=1428054735",
                          on_message=received)
    socket.run_forever()


@app.route("/")
def home():
    print(d)
    return render_template("home.html", data=d)

if __name__ == "__main__":
    manager = Manager()
    d = manager.dict({"lowestTime": {"value": 60, "time": ""}})
    websocket = Process(target=socket_controller, args=(d,))
    websocket.start()
    app.run(debug=True, use_reloader=False)