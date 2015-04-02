from websocket import WebSocketApp
from ast import literal_eval


def received(socket, message):
    print("RECEIVED", end="\r")
    message_dict = literal_eval(message)["payload"]
    if message_dict["seconds_left"] <= 57:
        print(message_dict["seconds_left"])
        print("^^^^  LOW TIME!")

socket = WebSocketApp("wss://wss.redditmedia.com/thebutton?h=5276b3bdcd25e805f3f8bae4ba146bdcda662129&e=1428047451",
                      on_message=received)

socket.run_forever()