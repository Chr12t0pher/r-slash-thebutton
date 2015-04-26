from ws4py.client.threadedclient import WebSocketClient
from ws4py.exc import HandshakeError
import csv
from ast import literal_eval
import threading
from flask import Flask, render_template, flash
import datetime
from json import loads, dumps
from time import sleep
import requests
import praw
from secret import secret
from os import urandom
import sendgrid
import app_templates

app = Flask(__name__)
app.secret_key = urandom(24)
bot = praw.Reddit(user_agent="[V2.0.0] button.cstevens.me (via /u/Chr12t0pher)")
bot.login("TheButtonStatsBot", secret["reddit"])
grid = sendgrid.SendGridClient("Chr12t0pher", secret["sendgrid"])


class Socket(WebSocketClient):
    def received_message(self, message):
        message = literal_eval(str(message))["payload"]
        if message["seconds_left"] < Data.lowest_click["click"]:  # Check for new low.
            Data.lowest_click_times[str(int(message["seconds_left"]))] = \
                datetime.datetime.utcnow().strftime("%d %b ") + message["now_str"][-8:].replace("-", ":")
            Data.lowest_click["click"] = int(message["seconds_left"])
            Data.lowest_click["time"] = \
                datetime.datetime.utcnow().strftime("%d %b ") + message["now_str"][-8:].replace("-", ":")
            #  Start milestone click watcher.
            threading.Thread(target=Data.milestone_low_watcher, args=(int(message["seconds_left"]), )).start()
        Data.total_clicks["all"] = int(message["participants_text"].replace(",", ""))


class ButtonStats:
    with open("data.json", "r") as f:
        data = loads(f.read())
        lowest_click = data["lowest_click"]
        lowest_click_times = data["lowest_click_times"]
        clicks_per_second = data["clicks_per_second"]
        total_clicks = data["total_clicks"]
        subreddit_flair = data["subreddit_flair"]
        max_date = data["max_date"]
        historic = data["historic"]
        milestones = data["milestones"]
        subscriptions_email = data["subscriptions"]["email"]
        subscriptions_reddit = data["subscriptions"]["reddit"]
        subscriptions_reddit_last_msg = data["subscriptions"]["reddit_last_msg"]

    def save_json(self):
        print("SAVING")
        data = {"lowest_click": self.lowest_click,
                "lowest_click_times": self.lowest_click_times,
                "clicks_per_second": self.clicks_per_second,
                "total_clicks": self.total_clicks,
                "subreddit_flair": self.subreddit_flair,
                "max_date": self.max_date,
                "historic": self.historic,
                "milestones": self.milestones,
                "subscriptions": {"email": self.subscriptions_email,
                                  "reddit": self.subscriptions_reddit,
                                  "reddit_last_msg": self.subscriptions_reddit_last_msg}
                }
        with open("data.json", "w") as f:
            f.write(dumps(data))

    def generate_json(self):
        data = {"lowest_click": self.lowest_click,
                "lowest_click_times": self.lowest_click_times,
                "clicks_per_second": self.clicks_per_second,
                "total_clicks": self.total_clicks,
                "subreddit_flair": self.subreddit_flair,
                "max_date": self.max_date}
        return data

    def scheduler(self):
        seconds = 0
        self._update_counts()
        self._update_flair()
        self._reddit_subscriptions()
        while True:
            self._update_counts()
            if seconds == 60 or seconds == 120:
                self._update_flair()
                self.save_json()
            elif seconds == 120:
                self._reddit_subscriptions()
                seconds = 0
            seconds += 1
            sleep(1)

    def milestone_low_watcher(self, second):
        sleep(10)
        if second == self.lowest_click["click"]:
            self._milestone_low()

    def milestone_clicks_watcher(self):
        if self.total_clicks["all"] >= self.milestones[0]:
            threading.Thread(target=self._milestone_clicks()).start()

    def socket_controller(self):
        while True:
            def socket_url():
                return requests.get("http://reddit.com/r/thebutton",
                                    headers={"User-Agent": "I'm grabbing the websocket URL for /u/Chr12t0pher"}
                                    ).text.split('_websocket": "')[1].split('", ')[0]
            try:
                socket = Socket(socket_url())
                socket.connect()
                socket.run_forever()
            except HandshakeError:
                continue

    def _update_counts(self):
        """Run every 5 seconds."""

        """Append click count to historic data, and remove unneeded data. Run every 5 seconds."""
        self.historic.append(self.total_clicks["all"])
        if len(self.historic) > 720:
            self.historic.pop(0)

        """Updates clicks_per_second & total_clicks."""
        self.clicks_per_second["all"] = round((
            self.total_clicks["all"] / (datetime.datetime.today() -
                                        datetime.datetime(2015, 4, 1, 17, 0, 0)).total_seconds()), 3)
        if len(self.historic) >= 12:  # 1 Minute Averages
            self.clicks_per_second["1m"] = round((self.historic[-1] - self.historic[-12]) / float(60), 3)
            self.total_clicks["1m"] = self.historic[-1] - self.historic[-12]
        if len(self.historic) >= 120:  # 10 Minute Averages
            self.clicks_per_second["10m"] = round((self.historic[-1] - self.historic[-120]) / float(600), 3)
            self.total_clicks["10m"] = self.historic[-1] - self.historic[-120]
        if len(self.historic) >= 720:  # 60 Minute Averages
            self.clicks_per_second["60m"] = round((self.historic[-1] - self.historic[-720]) / float(3600), 3)
            self.total_clicks["60m"] = self.historic[-1] - self.historic[-720]

        """Calculate max duration of timer."""
        calc_max_date = datetime.date(2015, 4, 1) + datetime.timedelta(int((self.total_clicks["all"] * 59) / 86400))
        self.max_date = datetime.datetime.strftime(calc_max_date, "%d %b %Y")

    def _update_flair(self):
        """Gets latest flair data and runs calculations. Run every 1 minute."""
        request_data = requests.get("http://tcial.org/the-button/button_clicks.csv").content.decode().split("\n")
        request_data.pop(0)  # First row is the headings.
        request_data.pop(-1)  # Last row is empty.

        flair_data = {"time": {}, "colour": {"red": 0, "orange": 0, "yellow": 0, "green": 0, "blue": 0, "purple": 0},
                      "colour_percentage": {"red": 0, "orange": 0, "yellow": 0, "green": 0, "blue": 0, "purple": 0}}
        for i in range(0, 61):  # Generate colours dictionary.
            flair_data["time"][str(i)] = 0
        for row in csv.reader(request_data):  # Read CSV file into each timer number.
            if row[0] != "1429984547":  # Ignore dodgy row in data with -824253 0 second clicks :3
                flair_data["time"][row[2]] += int(row[1])

        for time in flair_data["time"]:  # Add each times count to it's flair colour.
            if 60 >= int(time) > 51:
                flair_data["colour"]["purple"] += flair_data["time"][time]
            elif 51 >= int(time) > 41:
                flair_data["colour"]["blue"] += flair_data["time"][time]
            elif 41 >= int(time) > 31:
                flair_data["colour"]["green"] += flair_data["time"][time]
            elif 31 >= int(time) > 21:
                flair_data["colour"]["yellow"] += flair_data["time"][time]
            elif 21 >= int(time) > 11:
                flair_data["colour"]["orange"] += flair_data["time"][time]
            elif 11 >= int(time) > 0:
                flair_data["colour"]["red"] += flair_data["time"][time]

        for flair in flair_data["colour"]:
            flair_data["colour_percentage"][flair] = round(
                float((flair_data["colour"][flair] / sum(flair_data["time"].values())) * 100), 2)

        self.subreddit_flair = flair_data

    def _reddit_subscriptions(self):
        """Checks for users subscribing or unsubscribing to reddit pm notifications. Run every 2 minutes."""
        messages = bot.get_messages(limit=None, place_holder=self.subscriptions_reddit_last_msg)
        first = True
        for message in messages:
            # if message.body == "!subscribe" and message.author.name not in self.subscriptions_reddit:
                # self.subscriptions_reddit.append(message.author.name)
            if message.body == "!unsubscribe" and message.author.name in self.subscriptions_reddit:
                self.subscriptions_reddit.pop(self.subscriptions_reddit.index(message.author.name))
            if first is True:
                self.subscriptions_reddit_last_msg = message.id
                first = False

    def _milestone_low(self):
        """Post reddit thread and update users via email/reddit pm of a new low time."""
        post = bot.submit("thebutton",
                          "Just now, at {} UTC, the button went down to {} seconds.".format(
                              self.lowest_click["time"], self.lowest_click["click"]),
                          text=app_templates.reddit_post.format(
                              self.clicks_per_second["all"], self.total_clicks["all"],
                              self.clicks_per_second["1m"], self.total_clicks["1m"],
                              self.clicks_per_second["10m"], self.total_clicks["10m"],
                              self.clicks_per_second["60m"], self.total_clicks["60m"],

                              self.subreddit_flair["colour"]["purple"], self.subreddit_flair["colour_percentage"]["purple"],
                              self.subreddit_flair["colour"]["blue"], self.subreddit_flair["colour_percentage"]["blue"],
                              self.subreddit_flair["colour"]["green"], self.subreddit_flair["colour_percentage"]["green"],
                              self.subreddit_flair["colour"]["yellow"], self.subreddit_flair["colour_percentage"]["yellow"],
                              self.subreddit_flair["colour"]["orange"], self.subreddit_flair["colour_percentage"]["orange"],
                              self.subreddit_flair["colour"]["red"], self.subreddit_flair["colour_percentage"]["red"],

                              self.lowest_click["click"], self.lowest_click["time"]))

        grid.send(sendgrid.Mail(bcc=self.subscriptions_email, subject="[/r/thebutton stats] New low time!",
                                from_email="button@cstevens.me",
                                text=app_templates.email_low.format(self.lowest_click["click"],
                                                                       post.url.replace("www", "np"))))
        for user in self.subscriptions_reddit:
            bot.send_message(user, "[/r/thebutton stats] New low time!", app_templates.reddit_low.format(
                self.lowest_click["click"], post.url.replace("www", "np")))
            sleep(2)

    def _milestone_clicks(self):
        """Post reddit thread and update users via email/reddit pm of a particpant milestone."""
        milestone = self.milestones[0]
        self.milestones.pop(0)
        post = bot.submit("thebutton",
                          "Just now, at {} UTC, the button surpassed {} clicks.".format(
                              datetime.datetime.utcnow().strftime("%d %b %H:%M:%S"), milestone),
                          text=app_templates.reddit_post.format(
                              self.clicks_per_second["all"], self.total_clicks["all"],
                              self.clicks_per_second["1m"], self.total_clicks["1m"],
                              self.clicks_per_second["10m"], self.total_clicks["10m"],
                              self.clicks_per_second["60m"], self.total_clicks["60m"],

                              self.subreddit_flair["colour"]["purple"], self.subreddit_flair["colour_percentage"]["purple"],
                              self.subreddit_flair["colour"]["blue"], self.subreddit_flair["colour_percentage"]["blue"],
                              self.subreddit_flair["colour"]["green"], self.subreddit_flair["colour_percentage"]["green"],
                              self.subreddit_flair["colour"]["yellow"], self.subreddit_flair["colour_percentage"]["yellow"],
                              self.subreddit_flair["colour"]["orange"], self.subreddit_flair["colour_percentage"]["orange"],
                              self.subreddit_flair["colour"]["red"], self.subreddit_flair["colour_percentage"]["red"],

                              self.lowest_click["click"], self.lowest_click["time"]))
        grid.send(sendgrid.Mail(bcc=self.subscriptions_email, subject="[/r/thebutton stats] New participant milestone!",
                                from_email="button@cstevens.me",
                                text=app_templates.email_clicks.format(milestone,
                                                                       post.url.replace("www", "np"))))
        for user in self.subscriptions_reddit:
            bot.send_message(user, "[/r/thebutton stats] New participant milestone!", app_templates.reddit_clicks.format(
                self.milestone, post.url.replace("www", "np")))
            sleep(2)


Data = ButtonStats()


@app.route("/")
def home():
    return render_template("home.html", data=Data.generate_json(), time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/times")
def times():
    return render_template("times.html", data=Data.generate_json(), time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/flairs")
def flairs():
    return render_template("flairs.html", data=Data.generate_json(), time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/graphs")
def graphs():
    return render_template("graphs.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/about")
def about():
    return render_template("about.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/notify")
def notify():
    return render_template("notify.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/notify/<email>")
def notify_sub_unsub(email):
    if email in Data.subscriptions_email:
        Data.subscriptions_email.pop(Data.subscriptions_email.index(email))
        flash("You have successfully unsubscribed!", "success")
    else:
        Data.subscriptions_email.append(email)
        flash("You have successfully subscribed!", "success")
    return render_template("notify.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/donate")
def donate():
    return render_template("donate.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


if __name__ == '__main__':
    threading.Thread(target=Data.socket_controller).start()
    threading.Thread(target=Data.scheduler).start()
    app.run(debug=True, use_reloader=False, threaded=True)