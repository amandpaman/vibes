import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Vibes - Music Player", layout="centered")

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
    .uploadbox label {
        color: white;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">🎵 Vibes</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Play your favorite tracks from local files or online</div>', unsafe_allow_html=True)

# Tabs for Local or Online
tab1, tab2 = st.tabs(["📁 Local MP3", "🌐 YouTube Stream"])

with tab1:
    st.subheader("Upload and Play MP3 Files")
    uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])
    
    if uploaded_file:
        st.audio(uploaded_file, format="audio/mp3")
        st.success("Playing: " + uploaded_file.name)

with tab2:
    st.subheader("Stream from YouTube (Audio Only)")
    youtube_link = st.text_input("Paste YouTube audio stream URL (must be direct audio stream link)")

    if youtube_link:
        st.audio(youtube_link)
        st.success("Streaming from YouTube")

# Footer
st.markdown("---")
st.markdown('<p style="text-align:center; color: #ccc;">Created with ❤️ by Aman</p>', unsafe_allow_html=True)
