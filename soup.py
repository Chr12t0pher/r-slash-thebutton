from bs4 import BeautifulSoup
import requests
from time import sleep
from app import flairfile, currentflairfile
from json import dumps

while True:
    # Get flair data.
    flairs = {"colours": {"grey": 0, "purple": 0, "blue": 0, "green": 0, "yellow": 0, "orange": 0, "red": 0},
              "counts": {}}

    flair_data = requests.get("http://www.streamingflair.com/thebutton/rawthebutton/").text
    flair_soup = BeautifulSoup(flair_data).find(id="table1").find_all("tr")
    flair_soup.pop(0)

    for i in range(1, 61):
        flairs["counts"][i] = 0

    for entry in flair_soup:
        if entry.find_all("td")[1].text == "non presser":
            pass  # Ignore dirty greys ;)
        elif entry.find_all("td")[1].text == "NoFlair":
            pass  # Ignore users without flair.
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