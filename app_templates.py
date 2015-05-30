reddit_post = """
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


Want to get notified when new milestones are achieved? Click [here](http://button.cstevens.me/notify) for email alerts.


Data via [/r/thebutton stats](http://button.cstevens.me/).

^_I_ ^_am_ ^_a_ ^_bot._ ^_Contact_ ^_/u/Chr12t0pher_ ^_with_ ^_comments/complaints._
"""

reddit_post_end = """
#Button Statistics at {} UTC

Clicks Per Second | Time Frame | Number Of Clicks
-----------------|:----------:|------------:
{} | _Overall_ | {}

Flair Colour | Count no. | Count %
------------|---------|-------
Purple | {} | {}
Blue | {} | {}
Green | {} | {}
Yellow | {} | {}
Orange | {} | {}
Red | {} | {}

Flair Number | Count no.
------------ | ---------
60 | {}
59 | {}
58 | {}
57 | {}
56 | {}
55 | {}
54 | {}
53 | {}
52 | {}
51 | {}
50 | {}
49 | {}
48 | {}
47 | {}
46 | {}
45 | {}
44 | {}
43 | {}
42 | {}
41 | {}
40 | {}
39 | {}
38 | {}
37 | {}
36 | {}
35 | {}
34 | {}
33 | {}
32 | {}
31 | {}
30 | {}
29 | {}
28 | {}
27 | {}
26 | {}
25 | {}
24 | {}
23 | {}
22 | {}
21 | {}
20 | {}
19 | {}
18 | {}
17 | {}
16 | {}
15 | {}
14 | {}
13 | {}
12 | {}
11 | {}
10 | {}
9 | {}
8 | {}
7 | {}
6 | {}
5 | {}
4 | {}
3 | {}
2 | {}
1 | {}
0 | {}

### Raw Websocket Data

    {}

This is the raw data sent by reddit announcing the end of the button, there may be stuff here or there may be nothing,
I don't know because im writing this from the past, cool right? All I know is there is "type": "just_expired" in there
somewhere which triggered this post, hopefully there is "now_str" or similar which will give the exact time the button
ended, as the time shown at the top is likely to be a few seconds out.

---

Thanks to /u/emtes (inspiration), /u/mjgcfb (flair data), /u/lovethebacon (flair data), /u/OutOfBrain (flair data &
historical data), and anybody else who suggested features, donated, or offered feedback.

---

^_Data_ ^_via_ [^_/r/thebutton_ ^_stats_](http://button.cstevens.me/)^_._

^_Source_ ^_Code_ ^_available_ ^_on_ [^_Github_](https://github.com/Chr12t0pher/r-slash-thebutton)^_._

^_If_ ^_you_ ^_enjoyed_ ^_this_ ^_service_ ^_please_ ^_consider_ [^_donating_](http://button.cstevens.me/donate)^_._

^_I_ ^_am_ ^_a_ ^_bot._ ^_Contact_ ^_/u/Chr12t0pher_ ^_with_ ^_comments/complaints._
"""

reddit_low = """
The button has gone down to {} seconds! Click [here]({}) to view the stats.

To unsubscribe, click [here](http://www.reddit.com/message/compose?to=thebuttonstatsbot&subject=Unsubscribing&message=!unsubscribe).
"""

reddit_clicks = """
The button has passed {} clicks! Click [here]({}) to view the stats.

To unsubscribe, click [here](http://www.reddit.com/message/compose?to=thebuttonstatsbot&subject=Unsubscribing&message=!unsubscribe).
"""

reddit_end = """
The experiement is over! Click [here]({}) to view the stats.

Thank you for using [/r/thebutton stats](http://button.cstevens.me).

^_If_ ^_you_ ^_enjoyed_ ^_this_ ^_service_ ^_please_ ^_consider_ [^_donating_](http://button.cstevens.me/donate)^_._

"""

email_low = """
The button has gone down to {} seconds! See the stats at {}.

To unsubscribe, goto http://button.cstevens.me/notify and enter your email address.
"""

email_clicks = """
The button has passed {} clicks! See the stats at {}.

To unsubscribe, goto http://button.cstevens.me/notify and enter your email address.
"""

email_end = """
The experiement is over! Click [here]({}) to view the stats.

Thank you for using [/r/thebutton stats](http://button.cstevens.me).
Your email will now be removed from the database.

If you enjoyed this service please consider [donating](http://button.cstevens.me/donate).

"""