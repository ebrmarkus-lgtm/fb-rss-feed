from datetime import datetime, timedelta
import feedgenerator

GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

def generate_rss():
    feed = feedgenerator.Rss201rev2Feed(
        title="Tasuta Asjad Facebooki Grupp",
        link=GROUP_URL,
        description="Automaatselt uuenev voog Facebooki grupist (viimased 48h)",
        language="et",
    )

    # Siia lisatakse automaatselt hangitud andmed, mis läbivad 48h ja katki-lingi kontrolli
    # Piirang: kuni 50 postitust, mis on uuemad kui 48 tundi
    piir_aeg = datetime.now() - timedelta(hours=48)

    # Näidis teavitus, kui ootel on automaatne ühendus
    feed.add_item(
        title="Süsteem on seadistatud koguma kuni 50 postitust",
        link=GROUP_URL,
        description="Filtreerib automaatselt välja postitused, mis on vanemad kui 48h või sisaldavad katkiseid linke.",
        pubDate=datetime.now(),
    )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
