import streamlit as st
import feedparser

st.set_page_config(page_title="Tasuta Asjad Feed", page_icon="📦", layout="centered")

st.title("📦 Tasuta Asjad Harjumaal & Tallinnas")
st.write("Automaatne Facebooki grupi postituste voog.")

RSS_URL = "https://raw.githubusercontent.com/ebrmarkus-lgtm/fb-rss-feed/main/feed.xml"

try:
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        st.success(f"Leiti {len(feed.entries)} postitust.")
        for entry in feed.entries:
            st.subheader(entry.get("title", "Pealkirjata"))
            st.write(entry.get("description", "Sisu puudub"))
            link = entry.get("link")
            if link:
                st.markdown(f"[🔗 Ava Facebookis]({link})")
            st.markdown("---")
    else:
        st.info("Voog on hetkel tühi.")
except Exception as e:
    st.error(f"Viga: {e}")
