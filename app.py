import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Vibes - Music Player", layout="centered")

# ----------- UI Styling -----------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
    }
    .block-container {
        padding-top: 2rem;
    }
    .title {
        font-size: 3rem;
        font-weight: bold;
        color: #fddb3a;
        text-align: center;
    }
    .subtitle {
        font-size: 1.3rem;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------- Title Section -----------
st.markdown('<div class="title">🎵 Vibes</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Play your favorite tracks from local files or online</div>', unsafe_allow_html=True)

# ----------- Theme Switch -----------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

theme = st.radio("Select Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)
st.session_state.theme = theme

if theme == "Light":
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(to right, #ffffff, #d3d3d3);
            color: black;
        }
        .title { color: #1e3c72; }
        .subtitle { color: #000; }
        </style>
    """, unsafe_allow_html=True)

# ----------- Load Favorites -----------
fav_file = Path("favorites.json")
if fav_file.exists():
    favorites = json.loads(fav_file.read_text())
else:
    favorites = []

# ----------- Tabs -----------
tab1, tab2, tab3 = st.tabs(["📁 Local MP3", "🌐 YouTube Stream", "⭐ Favorites"])

# ----------- Local MP3 -----------
with tab1:
    st.subheader("Upload and Play MP3 Files")
    uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])
    if uploaded_file:
        st.audio(uploaded_file, format="audio/mp3")
        st.success("Playing: " + uploaded_file.name)
        if st.button("Add to Favorites"):
            favorites.append({"type": "local", "name": uploaded_file.name})
            fav_file.write_text(json.dumps(favorites))
            st.success("Added to favorites!")

# ----------- YouTube Stream -----------
with tab2:
    st.subheader("Stream from YouTube (Audio Only)")
    youtube_link = st.text_input("Paste direct YouTube audio stream URL")
    if youtube_link:
        st.audio(youtube_link)
        if st.button("Add YouTube Link to Favorites"):
            favorites.append({"type": "youtube", "url": youtube_link})
            fav_file.write_text(json.dumps(favorites))
            st.success("Added to favorites!")

# ----------- Favorites -----------
with tab3:
    st.subheader("Your Favorite Tracks")
    if favorites:
        for i, fav in enumerate(favorites):
            if fav["type"] == "local":
                st.markdown(f"**🎧 {fav['name']}** (local file - reupload needed)")
            elif fav["type"] == "youtube":
                st.markdown(f"**🔗 YouTube Stream:** {fav['url']}")
                st.audio(fav["url"])
            if st.button(f"❌ Remove Favorite {i+1}"):
                del favorites[i]
                fav_file.write_text(json.dumps(favorites))
                st.experimental_rerun()
    else:
        st.info("No favorites added yet.")

# ----------- Footer -----------
st.markdown("---")
st.markdown('<p style="text-align:center; color: #ccc;">Created with ❤️ by Aman</p>', unsafe_allow_html=True)
