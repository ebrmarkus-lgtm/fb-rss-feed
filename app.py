import streamlit as st
import feedparser

st.set_page_config(page_title="Tasuta Asjad Feed", page_icon="📦", layout="centered")

st.title("📦 Tasuta Asjad Facebooki Grupp")
st.write("Reaalajas uuenev voog otse RSS-failist (uueneb automaatselt).")

RSS_URL = "https://raw.githubusercontent.com/ebrmarkus-lgtm/fb-rss-feed/main/feed.xml"

try:
    feed = feedparser.parse(RSS_URL)
    
    if feed.entries:
        st.success(f"Leiti {len(feed.entries)} aktiivset postitust.")
        st.markdown("---")
        
        for entry in feed.entries:
            st.subheader(entry.get("title", "Pealkirjata"))
            st.write(entry.get("description", "Sisu puudub"))
            
            # Piltide ja linkide kuvamine
            link = entry.get("link")
            if link:
                st.markdown(f"[🔗 Ava Facebookis]({link})")
            st.markdown("---")
    else:
        st.info("Voog on hetkel tühi.")
        
except Exception as e:
    st.error(f"Tekkis viga voo laadimisel: {e}")
