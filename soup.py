from bs4 import BeautifulSoup
import requests
from time import sleep
from app import flairfile, currentflairfile
from json import dumps
import threading
import praw
from secret import secret


def five_minute():
    while True:
        # Get flair data.
        flairs = {"colours": {"grey": 0, "purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0},
                  "counts": {}}

        flair_data = requests.get("http://www.streamingflair.com/thebutton/rawthebutton2/").text
        flair_soup = BeautifulSoup(flair_data).find(id="table1").find_all("tr")
        flair_soup.pop(0)

        for i in range(1, 61):
            flairs["counts"][i] = 0

        for entry in flair_soup:
            if entry.find_all("td")[1].text == "non presser":
                pass  # Implementing this soon
            elif entry.find_all("td")[1].text == "NoFlair":
                pass  # Ignore users without flair.
            elif entry.find_all("td")[1].text == "admin":
                pass
            elif entry.find_all("td")[1].text == "can't press":
                pass  # Implementing this soon
            else:
                time = int(entry.find_all("td")[1].text[:-1])
                flairs["counts"][time] += 1

        for time in flairs["counts"]:
            if 60 >= time > 50:
                flairs["colours"]["purple"] += flairs["counts"][time]
            elif 50 >= time > 41:
                flairs["colours"]["blue"] += flairs["counts"][time]
            elif 41 >= time > 31:
                flairs["colours"]["green"] += flairs["counts"][time]
            elif 31 >= time > 21:
                flairs["colours"]["yellow"] += flairs["counts"][time]
            elif 21 >= time > 11:
                flairs["colours"]["orange"] += flairs["counts"][time]
            elif 11 >= time > 0:
                flairs["colours"]["red"] += flairs["counts"][time]

        with open(flairfile, "w") as f:
            f.write(dumps(flairs))

        current_flair = {"purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0}

        for flair in flairs["colours"]:
            current_flair[flair] = round(float((flairs["colours"][flair] / sum(flairs["colours"].values())) * 100), 2)

        with open(currentflairfile, "w") as f:
            f.write(dumps(current_flair))

        sleep(300)


def fiveteen_seconds():
    bot = praw.Reddit(user_agent="/r/thebutton Stats Poster (contact /u/Chr12t0pher)")
    bot.login("TheButtonStatsBot", secret)
    while True:
        user = bot.get_redditor("TheButtonStatsBot")
        posts = user.get_submitted(sort="new")
        title_list = []
        for post in posts:
            if post.title in title_list:
                post.delete()
            title_list.append(post.title)
        sleep(15)


if __name__ == "__main__":
    threading.Thread(target=five_minute).start()
    threading.Thread(target=fiveteen_seconds).start()