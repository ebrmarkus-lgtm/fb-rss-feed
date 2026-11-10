import streamlit as st
import feedparser

st.set_page_config(page_title="Tasuta Asjad Feed", page_icon="📦", layout="centered")

st.title("📦 Tasuta Asjad Facebooki Grupp")
st.write("Reaalajas uuenev voog (kuni 50 viimast postitust, uueneb iga 6h tagant).")

RSS_URL = "https://raw.githubusercontent.com/ebrmarkus-lgtm/fb-rss-feed/main/feed.xml"

try:
    feed = feedparser.parse(RSS_URL)
    
    if feed.entries:
        st.success(f"Leiti {len(feed.entries)} aktiivset postitust.")
        st.markdown("---")
        
        for entry in feed.entries:
            st.subheader(entry.get("title", "Pealkirjata"))
            
            # Pildi kuvamine (kontrollib enclosure või kirjelduses olevaid pilte)
            image_url = None
            if hasattr(entry, "enclosures") and entry.enclosures:
                image_url = entry.enclosures[0].get("href")
            
            if image_url:
                st.image(image_url, width=500)
                
            st.write(entry.get("description", "Sisu puudub"))
            
            link = entry.get("link")
            if link:
                st.markdown(f"[🔗 Ava originaalpostitus Facebookis]({link})")
            st.markdown("---")
    else:
        st.info("Voog on hetkel tühi.")
        
except Exception as e:
    st.error(f"Tekkis viga voo laadimisel: {e}")
