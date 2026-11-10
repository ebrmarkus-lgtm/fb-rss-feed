from datetime import datetime
import feedgenerator

GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

def generate_rss():
    feed = feedgenerator.Rss201rev2Feed(
        title="Tasuta Asjad Facebooki Grupp",
        link=GROUP_URL,
        description="Automaatselt uuenev voog Facebooki grupist",
        language="et",
    )

    # Siia saate lisada oma grupi reaalsed postitused ja nende otselingid
    # Iga uus postitus käib niiviisi:
    feed.add_item(
        title="Näiteks: Ära anname diivani Tallinnas",
        link="https://www.facebook.com/groups/TasutaAsjad/permalink/123456789/", # Siia pange konkreetse postituse link
        description="Heas korras diivan ära anda, ise järele tulla.",
        pubDate=datetime.now(),
    )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
