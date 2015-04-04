from bs4 import BeautifulSoup
import requests
from time import sleep
from app import flairfile
from json import dumps

while True:
    flairs = {"grey": 0, "purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0}
    data = requests.get("http://www.streamingflair.com/thebutton/rawthebutton/").text
    soup = BeautifulSoup(data).find(id="table1").find_all("tr")
    soup.pop(0)

    counts = {}
    for i in range(1, 61):
        counts[i] = 0

    for entry in soup:
        if entry.find_all("td")[1].text == "non presser":
            flairs["grey"] += 1
        elif entry.find_all("td")[1].text == "NoFlair":
            pass  # Ignore users without flair.
        else:
            time = int(entry.find_all("td")[1].text[:-1])
            counts[time] += 1

    for time in counts:
        if 60 >= time > 50:
            flairs["purple"] += counts[time]
        elif 50 >= time > 40:
            flairs["blue"] += counts[time]
        elif 40 >= time > 30:
            flairs["green"] += counts[time]
        elif 30 >= time > 20:
            flairs["yellow"] += counts[time]
        elif 20 >= time > 10:
            flairs["orange"] += counts[time]
        elif 10 >= time > 0:
            flairs["red"] += counts[time]

    with open(flairfile, "w") as f:
        f.write(dumps(flairs))
    sleep(300)