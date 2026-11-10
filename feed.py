from datetime import datetime
import xml.etree.ElementTree as ET

GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

def generate_rss():
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Tasuta Asjad Facebooki Grupp"
    ET.SubElement(channel, "link").text = GROUP_URL
    ET.SubElement(channel, "description").text = "Automaatselt uuenev voog Facebooki grupist"

    # Loome 5 testpostitust
    for i in range(1, 6):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"Tasuta asi nr {i} - Pakkumine"
        ET.SubElement(item, "link").text = f"{GROUP_URL}/permalink/1000{i}/"
        ET.SubElement(item, "description").text = f"See on automaatne kirje nr {i} grupis TasutaAsjad."
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    tree = ET.ElementTree(rss)
    with open("feed.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    generate_rss()
