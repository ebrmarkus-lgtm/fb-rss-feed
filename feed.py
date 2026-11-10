from datetime import datetime
import os
from bs4 import BeautifulSoup
import feedgenerator
import requests

# Asendage see oma Facebooki grupi õige aadressiga
GROUP_URL = (
    "https://www.facebook.com/groups/tasutaasjadharjumaaltallinnas"
)  # või teie grupi täpne link


def generate_rss():
  # Loome RSS-voo objekti
  feed = feedgenerator.Rss201rev2Feed(
      title="Tasuta asjad Harjumaal / Tallinnas",
      link=GROUP_URL,
      description="Automaatselt uuenev voog Facebooki grupist",
      language="et",
  )

  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(GROUP_URL, headers=headers)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      for post in soup.find_all("p")[:10]:
        text = post.get_text().strip()
        if len(text) > 10:
          feed.add_item(
              title=text[:50] + "...",
              link=GROUP_URL,
              description=text,
              pubDate=datetime.now(),
          )
  except Exception as e:
    print(f"Viga andmete lugemisel: {e}")

  # Kirjutame tulemuse XML faili
  with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(feed.writeString("utf-8"))


if __name__ == "__main__":
  generate_rss()
