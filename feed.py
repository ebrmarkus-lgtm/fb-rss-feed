from datetime import datetime
import feedgenerator

GROUP_URL = "https://www.facebook.com/groups/tasutaasjadharjumaaltallinnas"

def generate_rss():
    feed = feedgenerator.Rss201rev2Feed(
        title="Tasuta asjad Harjumaal / Tallinnas",
        link=GROUP_URL,
        description="Automaatselt uuenev voog Facebooki grupist",
        language="et",
    )

    # Lisame testpostituse, et näha, kas Streamlit ja XML-voog toimivad
    feed.add_item(
        title="Testpostitus: Süsteem töötab!",
        link=GROUP_URL,
        description="Kui näete seda teksti, siis Streamlit ja RSS-voog on omavahel õigesti ühendatud. Järgmisena lahendame Facebooki sisselogimise piirangu.",
        pubDate=datetime.now(),
    )

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed.writeString("utf-8"))

if __name__ == "__main__":
    generate_rss()
