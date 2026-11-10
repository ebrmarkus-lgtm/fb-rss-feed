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

    # Loome 5 testpostitust, et näeksite mitut erinevat elementi lehel
    for i in range(1, 6):
        feed.add_item(
            title=f"Tasuta asi nr {i} - Pakkumine",
            link=f"{GROUP_URL}/permalink/1000{i}/",
            description=f"See on automaatne kirje nr {i} grupis TasutaAsjad. Ese on heas korras.",
            pubDate=datetime.now(),
        )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
