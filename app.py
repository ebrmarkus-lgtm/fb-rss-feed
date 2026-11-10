import streamlit as st
import feedparser

st.set_page_config(page_title="Tasuta Asjad Feed", page_icon="📦", layout="centered")

st.title("📦 Tasuta Asjad Harjumaal & Tallinnas")
st.write("Automaatne Facebooki grupi postituste voog.")

# Siia kleepige oma feed.xml täpne Raw link
RSS_URL = "https://raw.githubusercontent.com/ebrmarkus-lgtm/fb-rss-feed/main/feed.xml"

try:
    feed = feedparser.parse(RSS_URL)
    
    # Kuvame silumiseks info otse lehel
    st.write(f"Loetud URL: `{RSS_URL}`")
    st.write(f"Leitud postituste arv: {len(feed.entries)}")
    
    if feed.entries:
        st.success("Voog on edukalt laetud!")
        for entry in feed.entries:
            st.subheader(entry.get("title", "Pealkirjata"))
            st.write(entry.get("description", "Sisu puudub"))
            link = entry.get("link")
            if link:
                st.markdown(f"[🔗 Ava link]({link})")
            st.markdown("---")
    else:
        st.warning("Feed on tühi või seda ei õnnestunud lugeda.")
        
except Exception as e:
    st.error(f"Tekkis viga: {e}")
