from datetime import datetime
import xml.etree.ElementTree as ET

GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

def generate_rss():
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Tasuta Asjad Facebooki Grupp"
    ET.SubElement(channel, "link").text = GROUP_URL
    ET.SubElement(channel, "description").text = "Automaatselt uuenev voog Facebooki grupist koos piltidega"

    # Näidisandmed reaalsete piltide ja toimivate linkidega
    items_data = [
        {
            "title": "Diivan ära anda Tallinnas",
            "link": "https://www.facebook.com/groups/TasutaAsjad/",
            "description": "Heas korras lahtikäiv diivan. Ise järele tulla Mustamäele.",
            "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600"
        },
        {
            "title": "Laste jalgratas (20 tolli)",
            "link": "https://www.facebook.com/groups/TasutaAsjad/",
            "description": "Vähekasutatud ratas, pidurid korras. Asub Nõmmel.",
            "image": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600"
        },
        {
            "title": "Raamaturiiul (valge)",
            "link": "https://www.facebook.com/groups/TasutaAsjad/",
            "description": "Kasutatud aga korralik raamaturiiul, kõrgus 180cm.",
            "image": "https://images.unsplash.com/photo-1594626513470-49666f54c30a?w=600"
        }
    ]

    for item_info in items_data:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = item_info["title"]
        ET.SubElement(item, "link").text = item_info["link"]
        ET.SubElement(item, "description").text = item_info["description"]
        # Lisame pildi toe RSS elemendina
        ET.SubElement(item, "enclosure", url=item_info["image"], type="image/jpeg")
        ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    tree = ET.ElementTree(rss)
    with open("feed.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    generate_rss()
