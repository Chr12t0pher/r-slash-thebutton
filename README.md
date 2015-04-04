# r/thebutton
Generating statistics based off of /r/thebutton using Python.
![Image of the site in action](http://i.imgur.com/frO07b6.png)
---
## Installation/Usage:
1) `pip install ws4py` & `pip install flask`

2) Navigate to [/r/thebutton](http://reddit.com/r/thebutton), and using your dev tools,
find the url with the domain wss.redditmedia.com and change line 40 with your unique url,
with the format: `"wss://wss.redditmedia.com/thebutton?h=...&e=...`

3) Remove the `.copy` extension for the two `.json` files.


4) And you're done! Run `app.py` and visit [127.0.0.1:5000](http://127.0.0.1:5000) to see it in action.
