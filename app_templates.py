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

reddit_low = """
The button has gone down to {} seconds! Click [here]({}) to view the stats.

To unsubscribe, click [here](http://www.reddit.com/message/compose?to=thebuttonstatsbot&subject=Unsubscribing&message=!unsubscribe).
"""

reddit_clicks = """
The button has passed {} clicks! Click [here]({}) to view the stats.

To unsubscribe, click [here](http://www.reddit.com/message/compose?to=thebuttonstatsbot&subject=Unsubscribing&message=!unsubscribe).
"""

email_low = """
The button has gone down to {} seconds! See the stats at {}.

To unsubscribe, goto http://button.cstevens.me/notify and enter your email address.
"""

email_clicks = """
The button has passed {} clicks! See the stats at {}.

To unsubscribe, goto http://button.cstevens.me/notify and enter your email address.
"""