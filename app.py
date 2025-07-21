
import streamlit as st
import os
from io import BytesIO
from pydub import AudioSegment
from mutagen.mp3 import MP3
import base64
from yt_dlp import YoutubeDL
import tempfile

st.set_page_config(page_title="🎵 Vibes Music Player", layout="wide")

st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎶 Vibes Music Player")

option = st.radio("Select Mode", ["Upload Local MP3", "Download from YouTube"])

# Download directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': tmpfile.name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return tmpfile.name

def show_metadata(file):
    try:
        audio = MP3(file)
        duration = audio.info.length
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        st.markdown(f"**Duration:** {minutes}:{seconds:02d}")
        try:
            title = audio.get('TIT2', 'Unknown Title')
            st.markdown(f"**Title:** {title}")
        except:
            pass
    except Exception as e:
        st.error("Metadata not found")

def play_audio(file_path):
    audio = AudioSegment.from_file(file_path, format="mp3")
    buffer = BytesIO()
    audio.export(buffer, format="mp3")
    audio_bytes = buffer.getvalue()
    st.audio(audio_bytes, format="audio/mp3")

    st.progress(0)
    duration = MP3(file_path).info.length
    with st.empty():
        for i in range(1, 101):
            st.progress(i)
            st.sleep(duration / 100)

def save_playlist(playlist):
    with open("playlist.txt", "w") as f:
        for item in playlist:
            f.write(item + "\n")

def load_playlist():
    if os.path.exists("playlist.txt"):
        with open("playlist.txt", "r") as f:
            return [line.strip() for line in f]
    return []

playlist = load_playlist()

if option == "Upload Local MP3":
    file = st.file_uploader("Upload an MP3 file", type="mp3")
    if file is not None:
        temp_file_path = os.path.join(DOWNLOAD_DIR, file.name)
        with open(temp_file_path, "wb") as f:
            f.write(file.read())
        show_metadata(temp_file_path)
        play_audio(temp_file_path)
        if st.button("Add to Playlist"):
            playlist.append(temp_file_path)
            save_playlist(playlist)
            st.success("Added to playlist ✅")

elif option == "Download from YouTube":
    url = st.text_input("Enter YouTube URL")
    if st.button("Download & Play") and url:
        with st.spinner("Downloading..."):
            path = download_youtube_audio(url)
        if path:
            show_metadata(path)
            play_audio(path)
            if st.button("Add to Playlist"):
                playlist.append(path)
                save_playlist(playlist)
                st.success("Added to playlist ✅")

st.markdown("## 🎧 Your Playlist")
for i, item in enumerate(playlist):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{os.path.basename(item)}**")
    with col2:
        if st.button("▶️ Play", key=f"play_{i}"):
            show_metadata(item)
            play_audio(item)
