import os
import re
import hashlib
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

import requests
import feedparser
import streamlit as st
from bs4 import BeautifulSoup

# =============================================================================
# TASUTA ASJAD PRO — GITHUB / STREAMLIT CLOUD
# Version 2.0 | Real RSS/Atom data | No fabricated listings
# =============================================================================

APP_TITLE = "Tasuta Asjad Harjumaal & Tallinnas"
APP_ICON = "📦"
GROUP_URL = "https://www.facebook.com/groups/TasutaAsjad"

CACHE_TTL = 300
REQUEST_TIMEOUT = 20
MAX_POSTS = 500
LOCAL_TZ = ZoneInfo("Europe/Tallinn")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tasuta_asjad")


# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #ffffff;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5eaf1;
    padding: 15px;
    border-radius: 12px;
}

.listing-title {
    font-size: 19px;
    font-weight: 700;
    color: #172033;
    margin-bottom: 8px;
}

.listing-meta {
    color: #64748b;
    font-size: 12px;
    margin-bottom: 12px;
}

.status-footer {
    color: #64748b;
    font-size: 12px;
    text-align: center;
    padding: 24px 0;
    border-top: 1px solid #e5eaf1;
    margin-top: 40px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 14px;
}

a {
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

def get_secret(name, default=""):
    """Read Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value).strip()
    except Exception:
        pass

    return os.getenv(name, default).strip()


DEFAULT_FEED_URL = get_secret("RSS_FEED_URL")


def valid_http_url(url):
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


# -----------------------------------------------------------------------------
# DATA EXTRACTION
# -----------------------------------------------------------------------------

def clean_html(value):
    if not value:
        return ""

    soup = BeautifulSoup(str(value), "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def extract_image(entry):
    """Extract an image belonging to the actual RSS item."""

    candidates = []

    # RSS media extensions
    for field in ("media_content", "media_thumbnail"):
        values = entry.get(field, [])
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    candidates.append(item.get("url"))

    # Enclosures
    for item in entry.get("enclosures", []):
        if isinstance(item, dict):
            mime = item.get("type", "")
            href = item.get("href") or item.get("url")

            if mime.startswith("image/") or (
                href and re.search(r"\.(jpg|jpeg|png|webp)(\?|$)", href, re.I)
            ):
                candidates.append(href)

    # HTML inside description / summary / content
    html_fields = [
        entry.get("summary", ""),
        entry.get("description", "")
    ]

    for content in entry.get("content", []):
        if isinstance(content, dict):
            html_fields.append(content.get("value", ""))

    for html in html_fields:
        if html:
            soup = BeautifulSoup(str(html), "html.parser")
            img = soup.find("img")

            if img:
                candidates.append(
                    img.get("src") or img.get("data-src")
                )

    # Only accept valid HTTP(S) images
    for candidate in candidates:
        if candidate and valid_http_url(candidate):
            return candidate

    return None


# -----------------------------------------------------------------------------
# AUTOMATIC CATEGORY DETECTION
# -----------------------------------------------------------------------------

CATEGORY_RULES = {
    "Mööbel": [
        "diivan", "laud", "tool", "riiul", "kapp",
        "voodi", "madrats", "mööbel", "tugitool"
    ],
    "Sporditarbed": [
        "jalgratas", "ratas", "suusad", "rulluisud",
        "sporditarbed", "treening", "pall"
    ],
    "Kodutehnika": [
        "televiisor", "teler", "külmkapp", "pesumasin",
        "mikrolaineahi", "tolmuimeja", "tehnika"
    ],
    "Kontor ja kool": [
        "arvuti", "monitor", "printer", "kirjutuslaud",
        "koolikott", "õpik", "kontoritool"
    ],
    "Riided ja jalatsid": [
        "riided", "jope", "mantel", "jalanõud",
        "jalatsid", "kingad", "püksid"
    ],
    "Ehitusmaterjalid": [
        "ehitusmaterjal", "lauad", "puit", "värv",
        "plaat", "tsement", "tööriist"
    ],
    "Lastekaubad": [
        "lapsevanker", "beebivoodi", "lastekaup",
        "mänguasi", "lasteriided", "turvatool"
    ],
    "Aed ja taimed": [
        "taim", "lill", "muld", "muru",
        "aiatöö", "istik", "potid"
    ]
}

LOCATION_RULES = {
    "Tallinn, Kesklinn": ["kesklinn"],
    "Tallinn, Mustamäe": ["mustamäe", "mustamäel"],
    "Tallinn, Õismäe": ["õismäe", "haabersti"],
    "Tallinn, Lasnamäe": ["lasnamäe"],
    "Tallinn, Nõmme": ["nõmme", "nõmmel"],
    "Tallinn, Kristiine": ["kristiine"],
    "Tallinn, Pirita": ["pirita"],
    "Harjumaa, Viimsi": ["viimsi"],
    "Harjumaa, Maardu": ["maardu"],
    "Harjumaa, Keila": ["keila"],
    "Harjumaa, Saue": ["saue"],
    "Harjumaa, Rae": ["rae", "jüri"],
    "Harjumaa, Saku": ["saku"],
    "Harjumaa, Harku": ["harku", "tabasalu"]
}


def detect_category(text):
    text = text.lower()

    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "Muu / määramata"


def detect_location(text):
    text = text.lower()

    for location, keywords in LOCATION_RULES.items():
        if any(keyword in text for keyword in keywords):
            return location

    if "tallinn" in text:
        return "Tallinn, määramata piirkond"

    if "harjumaa" in text:
        return "Harjumaa, määramata piirkond"

    return "Asukoht määramata"


# -----------------------------------------------------------------------------
# DATE PARSING
# -----------------------------------------------------------------------------

def parse_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")

    if parsed:
        try:
            dt = datetime(
                *parsed[:6],
                tzinfo=timezone.utc
            )
            return dt.astimezone(LOCAL_TZ)
        except (TypeError, ValueError, OverflowError):
            pass

    return None


# -----------------------------------------------------------------------------
# RSS / ATOM FETCH ENGINE
# -----------------------------------------------------------------------------

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_feed(feed_url):
    if not valid_http_url(feed_url):
        return [], "RSS-aadress puudub või ei ole korrektne.", ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; TasutaAsjadPro/2.0; "
            "+https://streamlit.io)"
        ),
        "Accept": (
            "application/rss+xml, application/atom+xml, "
            "application/xml, text/xml, */*"
        )
    }

    try:
        response = requests.get(
            feed_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        parsed_feed = feedparser.parse(response.content)

        entries = parsed_feed.entries[:MAX_POSTS]

        if not entries:
            return [], (
                "Andmevoog ei tagastanud ühtegi kuulutust. "
                "Kontrolli RSS-aadressi ja selle ligipääsu."
            ), parsed_feed.feed.get("title", "")

        posts = []
        seen = set()

        for entry in entries:
            title = clean_html(entry.get("title", ""))

            description_html = (
                entry.get("summary")
                or entry.get("description")
                or ""
            )

            if not description_html and entry.get("content"):
                description_html = entry["content"][0].get("value", "")

            description = clean_html(description_html)

            if not title:
                continue

            original_link = entry.get("link", "").strip()
            entry_id = entry.get("id", "").strip()

            # Prefer the actual post URL or feed ID
            identity = (
                original_link
                or entry_id
                or f"{title}|{entry.get('published', '')}"
            )

            fingerprint = hashlib.sha256(
                identity.encode("utf-8")
            ).hexdigest()

            if fingerprint in seen:
                continue

            seen.add(fingerprint)

            combined_text = f"{title} {description}"

            post_date = parse_date(entry)

            image_url = extract_image(entry)

            posts.append({
                "id": fingerprint,
                "title": title,
                "description": description,
                "image": image_url,
                "category": detect_category(combined_text),
                "location": detect_location(combined_text),
                "date": post_date,
                "link": original_link if valid_http_url(original_link) else "",
                "source": parsed_feed.feed.get("title", "RSS"),
            })

        posts.sort(
            key=lambda p: p["date"] or datetime.min.replace(
                tzinfo=LOCAL_TZ
            ),
            reverse=True
        )

        return posts, "", parsed_feed.feed.get("title", "RSS")

    except requests.exceptions.Timeout:
        return [], "Andmevoo päring aegus. Proovi uuesti.", ""

    except requests.exceptions.HTTPError as exc:
        return [], f"Andmeallika HTTP viga: {exc}", ""

    except requests.exceptions.RequestException as exc:
        logger.exception("RSS connection error")
        return [], f"Ühenduse viga: {exc}", ""

    except Exception:
        logger.exception("Unexpected feed parsing error")
        return [], "Andmevoo töötlemisel tekkis ootamatu viga.", ""


# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------

if "visible_count" not in st.session_state:
    st.session_state.visible_count = 25


# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Juhtpaneel")

    st.markdown("### 📡 Andmeallikas")

    feed_url = st.text_input(
        "RSS / Atom URL",
        value=DEFAULT_FEED_URL,
        placeholder="https://example.com/feed.xml",
        help="Sisesta Facebooki grupi postitusi vahendava teenuse RSS-aadress."
    ).strip()

    st.markdown(
        f"[Ava Facebooki grupp ↗]({GROUP_URL})"
    )

    st.divider()

    if st.button("🔄 Värskenda andmeid", use_container_width=True):
        st.cache_data.clear()
        st.session_state.visible_count = 25
        st.rerun()

    st.markdown("### 🔎 Otsing")

    search_query = st.text_input(
        "Märksõna",
        placeholder="Näiteks diivan, jalgratas..."
    ).strip().lower()

    st.markdown("### 📂 Kategooria")

    categories = ["Kõik kategooriad"] + list(CATEGORY_RULES.keys()) + [
        "Muu / määramata"
    ]

    category_filter = st.selectbox(
        "Vali kategooria",
        categories
    )

    st.markdown("### 📍 Piirkond")

    location_filter = st.selectbox(
        "Vali piirkond",
        ["Kõik piirkonnad"] + list(LOCATION_RULES.keys()) + [
            "Tallinn, määramata piirkond",
            "Harjumaa, määramata piirkond",
            "Asukoht määramata"
        ]
    )

    st.divider()

    st.caption(
        "Andmeid uuendatakse automaatselt iga 5 minuti järel "
        "uue päringu korral."
    )


# -----------------------------------------------------------------------------
# MAIN HEADER
# -----------------------------------------------------------------------------

st.title(f"{APP_ICON} {APP_TITLE}")

st.markdown(
    f"""
    Päris kuulutused Facebooki grupist
    **[TasutaAsjad ↗]({GROUP_URL})**.
    
    Otsi tasuta mööblit, tehnikat, riideid, lasteasju ja palju muud.
    """
)

st.divider()


# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------

if not feed_url:
    st.warning(
        "📡 Andmeallikas on seadistamata. Lisa vasakule "
        "külgpaneelile toimiv RSS/Atom-aadress."
    )

    st.info(
        "Facebooki grupi URL ei ole RSS-voog. Vajad eraldi "
        "andmevoogu, mis vahendab grupi päris avalikke postitusi."
    )

    st.link_button(
        "Ava Facebooki grupp",
        GROUP_URL
    )

    st.stop()


with st.spinner("Laen tegelikke kuulutusi..."):
    master_posts, feed_error, feed_title = load_feed(feed_url)


# -----------------------------------------------------------------------------
# SOURCE STATUS
# -----------------------------------------------------------------------------

if feed_error:
    st.error(f"⚠️ {feed_error}")

    st.link_button(
        "Ava Facebooki grupp",
        GROUP_URL
    )

    st.stop()


# -----------------------------------------------------------------------------
# FILTERING
# -----------------------------------------------------------------------------

filtered_posts = []

for post in master_posts:

    if (
        category_filter != "Kõik kategooriad"
        and post["category"] != category_filter
    ):
        continue

    if (
        location_filter != "Kõik piirkonnad"
        and post["location"] != location_filter
    ):
        continue

    if search_query:
        searchable = (
            post["title"] + " " + post["description"]
        ).lower()

        if search_query not in searchable:
            continue

    filtered_posts.append(post)


# -----------------------------------------------------------------------------
# STATISTICS
# -----------------------------------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "📦 Päris kuulutusi",
    len(master_posts)
)

col2.metric(
    "🔎 Otsingu tulemused",
    len(filtered_posts)
)

col3.metric(
    "📡 Andmeallikas",
    "Ühendatud"
)

st.caption(
    f"Allikas: {feed_title or 'RSS / Atom'} · "
    f"Viimane päring: {datetime.now(LOCAL_TZ).strftime('%d.%m.%Y %H:%M')}"
)

st.divider()


# -----------------------------------------------------------------------------
# RESULTS
# -----------------------------------------------------------------------------

if not filtered_posts:

    st.info(
        "Sellele otsingule vastavaid päris kuulutusi ei leitud."
    )

else:

    display_count = min(
        st.session_state.visible_count,
        len(filtered_posts)
    )

    visible_posts = filtered_posts[:display_count]

    st.markdown(
        f"### Leitud kuulutused ({len(filtered_posts)})"
    )

    columns = st.columns(2)

    for index, post in enumerate(visible_posts):

        with columns[index % 2]:

            with st.container(border=True):

                st.markdown(
                    f"<div class='listing-title'>{post['title']}</div>",
                    unsafe_allow_html=True
                )

                date_text = (
                    post["date"].strftime("%d.%m.%Y %H:%M")
                    if post["date"]
                    else "Kuupäev teadmata"
                )

                st.caption(
                    f"📂 {post['category']}  ·  "
                    f"📍 {post['location']}  ·  "
                    f"🕒 {date_text}"
                )

                if post["image"]:
                    try:
                        st.image(
                            post["image"],
                            use_container_width=True
                        )
                    except Exception:
                        st.caption("Pilt ei ole hetkel kättesaadav.")

                if post["description"]:
                    st.write(post["description"])

                if post["link"]:
                    st.markdown(
                        f"[🔗 Ava konkreetne kuulutus ↗]({post['link']})"
                    )
                else:
                    st.caption(
                        "Konkreetse postituse link puudub andmevoos."
                    )


    # -------------------------------------------------------------------------
    # PAGINATION
    # -------------------------------------------------------------------------

    if display_count < len(filtered_posts):

        st.divider()

        if st.button(
            "⬇️ Näita veel 25 kuulutust",
            use_container_width=True
        ):
            st.session_state.visible_count += 25
            st.rerun()

    elif len(filtered_posts) > 25:

        st.caption("Kõik leitud kuulutused on kuvatud.")


# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="status-footer">
        <b>📦 Tasuta Asjad Pro</b><br>
        Päris andmed · Duplikaatide eemaldamine ·
        Automaatne värskendamine<br>
        Andmed pärinevad ühendatud RSS / Atom andmeallikast.
    </div>
    """,
    unsafe_allow_html=True
)
