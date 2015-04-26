from bs4 import BeautifulSoup
import requests
from time import sleep
from app import flairfile, currentflairfile
from json import dumps
import threading
import csv


def two_minute():
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
            elif 60 >= int(time) > 51:
                flairs["colours"]["purple"] += flairs["counts"][time]
            elif 51 >= int(time) > 41:
                flairs["colours"]["blue"] += flairs["counts"][time]
            elif 41 >= int(time) > 31:
                flairs["colours"]["green"] += flairs["counts"][time]
            elif 31 >= int(time) > 21:
                flairs["colours"]["yellow"] += flairs["counts"][time]
            elif 21 >= int(time) > 11:
                flairs["colours"]["orange"] += flairs["counts"][time]
            elif 11 >= int(time) > 0:
                flairs["colours"]["red"] += flairs["counts"][time]

        # Get 'actual' flair data.
        actual_flair_data_csv = requests.get("http://tcial.org/the-button/button_clicks.csv").content.decode().split("\n")
        actual_flair_data = {}
        actual_flair_data_csv.pop(0)
        actual_flair_data_csv.pop(-1)
        for i in range(0, 61):
            actual_flair_data[str(i)] = 0
        for row in csv.reader(actual_flair_data_csv):
            if row[0] != "1429984547":  # Ignore dodgy row in data with -824253 0 second clicks :3
                actual_flair_data[row[2]] += int(row[1])

        flairs["calc_flairs"] = {"red": 0, "orange": 0, "yellow": 0, "green": 0, "blue": 0, "purple": 0}

        for time in actual_flair_data:
            if 60 >= int(time) > 50:
                flairs["calc_flairs"]["purple"] += actual_flair_data[time]
            elif 51 >= int(time) > 41:
                flairs["calc_flairs"]["blue"] += actual_flair_data[time]
            elif 41 >= int(time) > 31:
                flairs["calc_flairs"]["green"] += actual_flair_data[time]
            elif 31 >= int(time) > 21:
                flairs["calc_flairs"]["yellow"] += actual_flair_data[time]
            elif 21 >= int(time) > 11:
                flairs["calc_flairs"]["orange"] += actual_flair_data[time]
            elif 11 >= int(time) >= 0:
                flairs["calc_flairs"]["red"] += actual_flair_data[time]

        flairs["current_calc_flairs"] = {"purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0}
        for flair in flairs["calc_flairs"]:
            flairs["current_calc_flairs"][flair] = round(float((flairs["calc_flairs"][flair] / sum(actual_flair_data.values())) * 100), 2)
        
        with open(flairfile, "w") as f:
            f.write(dumps(flairs))

        current_flair = {"purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0, "grey": 0, "cant": 0}

        for flair in flairs["colours"]:
            current_flair[flair] = round(float((flairs["colours"][flair] / sum(flairs["colours"].values())) * 100), 2)

        with open(currentflairfile, "w") as f:
            f.write(dumps(current_flair))


        sleep(120)


if __name__ == "__main__":
    threading.Thread(target=two_minute).start()