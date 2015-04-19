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
        flairs = {"colours": {"grey": 0, "purple": 0, "blue": 0, "green": 0,
                              "yellow": 0, "orange": 0, "red": 0, "cant": 0},
                  "counts": {}}

        flair_data = requests.get("http://www.reddit.com/r/thebutton/comments/31zag0/the_top_100/",
                                  headers={"User-Agent": "/r/thebutton stats scraper (contact /u/Chr12t0pher)"}).text
        flair_soup = BeautifulSoup(flair_data).find("div", {"class": "entry"}).find("div", {"class": "usertext-body"})

        soup_table = flair_soup.find("table").find_all("tr")
        soup_table.pop(0)

        for entry in soup_table:
            entry = entry.text.splitlines()
            entry.pop(0)

            if entry[0] == "non presser":
                flairs["counts"]["non_presser"] = int(entry[1])
                flairs["colours"]["grey"] = int(entry[1])
            elif entry[0] == "Cowardly flair hiders":
                flairs["counts"]["no_flair"] = int(entry[1])
            elif entry[0] == "admin":
                pass
            elif entry[0] == "Noobs":
                flairs["counts"]["cant_press"] = int(entry[1])
                flairs["colours"]["cant"] = int(entry[1])
            else:
                flairs["counts"][entry[0][:-1]] = int(entry[1])

        for time in flairs["counts"]:
            if time in ["non_presser", "cant_press", "no_flair"]:
                pass
            elif 60 >= int(time) > 50:
                flairs["colours"]["purple"] += flairs["counts"][time]
            elif 50 >= int(time) > 41:
                flairs["colours"]["blue"] += flairs["counts"][time]
            elif 41 >= int(time) > 31:
                flairs["colours"]["green"] += flairs["counts"][time]
            elif 31 >= int(time) > 21:
                flairs["colours"]["yellow"] += flairs["counts"][time]
            elif 21 >= int(time) > 11:
                flairs["colours"]["orange"] += flairs["counts"][time]
            elif 11 >= int(time) > 0:
                flairs["colours"]["red"] += flairs["counts"][time]

        with open(flairfile, "w") as f:
            f.write(dumps(flairs))

        current_flair = {"purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0, "grey": 0, "cant": 0}

        for flair in flairs["colours"]:
            current_flair[flair] = round(float((flairs["colours"][flair] / sum(flairs["colours"].values())) * 100), 2)

        with open(currentflairfile, "w") as f:
            f.write(dumps(current_flair))

        sleep(300)


if __name__ == "__main__":
    threading.Thread(target=five_minute).start()