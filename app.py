from ws4py.client.threadedclient import WebSocketClient
from ws4py.exc import HandshakeError
from ast import literal_eval
import threading
from flask import Flask, render_template
import datetime
from json import loads, dumps
from time import sleep
from sys import platform
import requests
import praw
from secret import secret

bot = praw.Reddit(user_agent="/r/thebutton Stats Poster (contact /u/Chr12t0pher)")
bot.login("TheButtonStatsBot", secret)


if platform == "win32":  # If running locally.
    lowestfile = "lowest.json"; flairfile = "flair.json"; currentflairfile = "currentflair.json";
    historicfile = "historic.json"; milestonefile = "milestones.json"
else:  # If running in production.
    lowestfile = "/var/www/FlaskApp/lowest.json"; flairfile = "/var/www/FlaskApp/flair.json";
    currentflairfile = "/var/www/FlaskApp/currentflair.json"; historicfile = "/var/www/FlaskApp/historic.json";
    milestonefile = "/var/www/FlaskApp/milestones.json"

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
                threading.Thread(target=reddit_low, args=(button_data["lowestTime"]["all"]["clicks"],)).start()
            button_data["clicks"]["all"] = int(message_dict["participants_text"].replace(",", ""))

    while True:
        def new_socket_url():
            return requests.get("http://reddit.com/r/thebutton",
                                headers={"User-Agent": "/r/thebutton websocket url scraper (/u/Chr12t0pher)"}
                                ).text.split('_websocket": "')[1].split('", ')[0]
        try:
            socket = Socket(new_socket_url())
            socket.connect()
            socket.run_forever()
        except HandshakeError:
            continue


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
            data = loads(f.read())
            button_data["flairs"] = data["colours"]
            button_data["flairs_number"] = data["counts"]
        with open(currentflairfile, "r") as f:
            button_data["current_flair"] = loads(f.read())
        sleep(150)


def reddit_low(start_time):
    sleep(10)
    if start_time == button_data["lowestTime"]["all"]["clicks"]:
        bot.submit("thebutton",
                   "Just now, at {} UTC, the button went down to {} seconds.".format(
                       button_data["lowestTime"]["all"]["time"], button_data["lowestTime"]["all"]["clicks"]),
                   text=""")
#Button Statistics at {} UTC

Clicks Per Second | Time Frame | Number Of Clicks
-----------------|:----------:|------------:
{} | _Overall_ | {}
{} | _Past 01m_ | {}
{} | _Past 10m_ | {}
{} | _Past 60m_ | {}

Flair Colour | Count no. | Count %
------------|---------|-------
Purple | {} | {}
Blue | {} | {}
Green | {} | {}
Yellow | {} | {}
Orange | {} | {}
Red | {} | {}

>### Lowest time reached at the time of posting
>__{}__ at {} UTC

^_I_ ^_am_ ^_a_ ^_bot._ ^_Contact_ ^_/u/Chr12t0pher_ ^_with_ ^_comments/complaints._

^_Uses_ ^_data_ ^_from_ [^_/r/thebutton_ ^_stats_](http://46.101.29.145/) ^_&_
[^_streamingflair_](http://www.streamingflair.com/thebutton/rawthebutton/)
""".format(datetime.datetime.utcnow().strftime("%d %b %H:%M:%S"),
                    button_data["clicks_second"]["all"], button_data["clicks"]["all"],
                    button_data["clicks_second"]["1m"], button_data["clicks"]["1m"],
                    button_data["clicks_second"]["10m"], button_data["clicks"]["10m"],
                    button_data["clicks_second"]["60m"], button_data["clicks"]["60m"],

                    button_data["flairs"]["purple"], button_data["current_flair"]["purple"],
                    button_data["flairs"]["blue"], button_data["current_flair"]["blue"],
                    button_data["flairs"]["green"], button_data["current_flair"]["green"],
                    button_data["flairs"]["yellow"], button_data["current_flair"]["yellow"],
                    button_data["flairs"]["orange"], button_data["current_flair"]["orange"],
                    button_data["flairs"]["red"], button_data["current_flair"]["red"],

                    button_data["lowestTime"]["all"]["clicks"], button_data["lowestTime"]["all"]["time"]))


def reddit_milestone():
    with open(milestonefile, "r") as f:
        milestones = loads(f.read())
    sleep(30)
    while True:
        if int(button_data["clicks"]["all"]) >= milestones[0]:
            bot.submit("wpctesting",
                       "Just now, at {} UTC, the button surpassed {} clicks.".format(
                            datetime.datetime.utcnow().strftime("%d %b %H:%M:%S"), milestones[0]),
                       text="""
#Button Statistics at {} UTC

Clicks Per Second | Time Frame | Number Of Clicks
-----------------|:----------:|------------:
{} | _Overall_ | {}
{} | _Past 01m_ | {}
{} | _Past 10m_ | {}
{} | _Past 60m_ | {}

Flair Colour | Count no. | Count %
------------|---------|-------
Purple | {} | {}
Blue | {} | {}
Green | {} | {}
Yellow | {} | {}
Orange | {} | {}
Red | {} | {}

>### Lowest time reached at the time of posting
>__{}__ at {} UTC

^_I_ ^_am_ ^_a_ ^_bot._ ^_Contact_ ^_/u/Chr12t0pher_ ^_with_ ^_comments/complaints._

^_Uses_ ^_data_ ^_from_ [^_/r/thebutton_ ^_stats_](http://46.101.29.145/) ^_&_
[^_streamingflair_](http://www.streamingflair.com/thebutton/rawthebutton/)
""".format(datetime.datetime.utcnow().strftime("%d %b %H:%M:%S"),
                    button_data["clicks_second"]["all"], button_data["clicks"]["all"],
                    button_data["clicks_second"]["1m"], button_data["clicks"]["1m"],
                    button_data["clicks_second"]["10m"], button_data["clicks"]["10m"],
                    button_data["clicks_second"]["60m"], button_data["clicks"]["60m"],

                    button_data["flairs"]["purple"], button_data["current_flair"]["purple"],
                    button_data["flairs"]["blue"], button_data["current_flair"]["blue"],
                    button_data["flairs"]["green"], button_data["current_flair"]["green"],
                    button_data["flairs"]["yellow"], button_data["current_flair"]["yellow"],
                    button_data["flairs"]["orange"], button_data["current_flair"]["orange"],
                    button_data["flairs"]["red"], button_data["current_flair"]["red"],

                    button_data["lowestTime"]["all"]["clicks"], button_data["lowestTime"]["all"]["time"]))
            milestones.pop(0)
            with open(milestonefile, "w") as f:
                f.write(dumps(milestones))
            sleep(5)
        sleep(5)


@app.route("/")
def home():
    return render_template("home.html", data=button_data, time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])


@app.route("/times")
def times():
    return render_template("times.html", data=historic_data, time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])


@app.route("/flairs")
def flairs():
    return render_template("flairs.html", data=button_data, time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])


@app.route("/donate")
def donate():
    return render_template("donate.html", time=[datetime.datetime.utcnow().strftime("%H:%M:%S"), starttime])


@app.route("/json")
def json():
    json_data = button_data
    json_data["generated_at"] = datetime.datetime.utcnow().strftime("%H:%M:%S")
    return dumps(json_data)

if __name__ == "__main__":
    threading.Thread(target=socket_controller).start()
    threading.Thread(target=historic_append).start()
    threading.Thread(target=calculate_averages).start()
    threading.Thread(target=flair_data).start()
    threading.Thread(target=reddit_milestone).start()
    app.run(debug=True, use_reloader=False, threaded=True)