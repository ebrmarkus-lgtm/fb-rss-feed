from datetime import datetime
import feedgenerator

GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

def generate_rss():
    feed = feedgenerator.Rss201rev2Feed(
        title="Tasuta Asjad Facebooki Grupp",
        link=GROUP_URL,
        description="Automaatselt uuenev voog Facebooki grupist (viimased 48h)",
        language="et",
    )

    # Lisame näidistena toimivad kirjed, et näeksite kohe mitme postituse kuvamist
    for i in range(1, 6):
        feed.add_item(
            title=f"Tasuta asi nr {i} - Vaata pakkumist",
            link=f"{GROUP_URL}/permalink/100000{i}/",
            description=f"See on automaatselt genereeritud kirjeldus ja info toote nr {i} kohta grupis TasutaAsjad.",
            pubDate=datetime.now(),
        )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
