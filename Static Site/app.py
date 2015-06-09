from flask import Flask, render_template
import datetime
import json

app = Flask(__name__)

with open("data.json", "r") as f:
    data = json.loads(f.read())


@app.route("/")
def home():
    return render_template("home.html", data=data, time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/times")
def times():
    return render_template("times.html", data=data, time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/flairs")
def flairs():
    return render_template("flairs.html", data=data, time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/graphs")
def graphs():
    return render_template("graphs.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/about")
def about():
    return render_template("about.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


@app.route("/donate")
def donate():
    return render_template("donate.html", time=datetime.datetime.utcnow().strftime("%H:%M:%S"))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, threaded=True)
