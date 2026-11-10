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

    # Siia lisatakse automaatselt hangitud kirjed (kuni 50 postitust)
    feed.add_item(
        title="Tasuta Asjad Grupi automaatne voog",
        link=GROUP_URL,
        description="Reaalajas uuenevad postitused ja pakkumised grupist TasutaAsjad.",
        pubDate=datetime.now(),
    )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
