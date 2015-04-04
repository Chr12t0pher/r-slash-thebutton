from bs4 import BeautifulSoup
import requests
from time import sleep
from app import flairfile, currentflairfile
from json import dumps

while True:
    # Get flair data.
    flairs = {"grey": 0, "purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0}
    flair_data = requests.get("http://www.streamingflair.com/thebutton/rawthebutton/").text
    flair_soup = BeautifulSoup(flair_data).find(id="table1").find_all("tr")
    flair_soup.pop(0)

    counts = {}
    for i in range(1, 61):
        counts[i] = 0

    for entry in flair_soup:
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
        elif 50 >= time > 41:
            flairs["blue"] += counts[time]
        elif 41 >= time > 31:
            flairs["green"] += counts[time]
        elif 31 >= time > 21:
            flairs["yellow"] += counts[time]
        elif 21 >= time > 11:
            flairs["orange"] += counts[time]
        elif 11 >= time > 0:
            flairs["red"] += counts[time]

    with open(flairfile, "w") as f:
        f.write(dumps(flairs))

    #
    # Get subreddit data.
    current_flair = {"grey": 0, "purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0}
    subreddit_data = requests.get("http://www.reddit.com/r/thebutton",
                                  headers={"user-agent": "python:theButtonStats:1 (by /u/Chr12t0pher)"}).text
    subreddit_soup = BeautifulSoup(subreddit_data)
    subreddit_users = int(subreddit_soup.find("p", {"class": "users-online"}).find("span", {"class": "number"}).text.replace(",", ""))
    total_flair = sum(flairs.values())

    for flair in flairs:
        current_flair[flair] = round(float((flairs[flair] / total_flair) * 100), 2)

    with open(currentflairfile, "w") as f:
        f.write(dumps(current_flair))

    sleep(300)