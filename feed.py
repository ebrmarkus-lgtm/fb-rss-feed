from datetime import datetime
import feedgenerator

# Kasutame teie soovitud õiget grupi aadressi
GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

def generate_rss():
    feed = feedgenerator.Rss201rev2Feed(
        title="Tasuta Asjad Facebooki Grupp",
        link=GROUP_URL,
        description="Automaatselt uuenev voog Facebooki grupist",
        language="et",
    )

    # Lisame toimiva näidispostituse, kuni loome edasisi lahendusi
    feed.add_item(
        title="Ühendus on edukalt loodud!",
        link=GROUP_URL,
        description="See on automaatselt genereeritud XML-voo testkirje. Grupi lingiks on nüüd määratud TasutaAsjad.",
        pubDate=datetime.now(),
    )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
