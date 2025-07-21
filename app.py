import streamlit as st
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image
import os

# Explicitly set ffmpeg location for yt_dlp
os.environ["PATH"] += os.pathsep + "/usr/bin"

import io
import base64
import tempfile
import json
import yt_dlp

st.set_page_config(page_title="Vibes Music Player", layout="wide")
st.markdown("""
    <style>
    .title {
        font-size: 3em;
        font-weight: bold;
        background: -webkit-linear-gradient(45deg, #ff6ec4, #7873f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .block {
        border-radius: 20px;
        padding: 2em;
        background-color: #f0f2f6;
        margin-bottom: 2em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Vibes - Music Player</div>', unsafe_allow_html=True)

# Global states
playlist = []
current_song = None

# Create folders
if not os.path.exists("downloads"):
    os.makedirs("downloads")
if not os.path.exists("playlists"):
    os.makedirs("playlists")

# --- Functions ---
def load_metadata(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
        tags = audio.tags
        if tags and 'APIC:' in tags:
            artwork = tags['APIC:'].data
            return Image.open(io.BytesIO(artwork))
    except:
        pass
    return None

def download_youtube_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"downloads/{info['title']}.mp3"
            return filename
    except Exception as e:
        st.error(f"Download failed: {e}")
        return None

def save_playlist(name, songs):
    with open(f"playlists/{name}.json", "w") as f:
        json.dump(songs, f)

def load_playlist(name):
    try:
        with open(f"playlists/{name}.json", "r") as f:
            return json.load(f)
    except:
        return []

def display_waveform(audio_file):
    st.audio(audio_file)

# --- UI ---
st.sidebar.header("🎵 Upload or Download")

uploaded_file = st.sidebar.file_uploader("Upload MP3", type=["mp3"])

yt_url = st.sidebar.text_input("YouTube URL")
if st.sidebar.button("Download from YouTube"):
    if yt_url:
        downloaded = download_youtube_audio(yt_url)
        if downloaded:
            st.sidebar.success("Downloaded and added to playlist")
            playlist.append(downloaded)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(uploaded_file.read())
        playlist.append(tmp.name)
        st.sidebar.success("Uploaded and added to playlist")

# Playlist Display
st.subheader("🎧 Playlist")
for idx, song in enumerate(playlist):
    col1, col2 = st.columns([1, 4])
    with col1:
        art = load_metadata(song)
        if art:
            st.image(art, width=60)
        else:
            st.image("https://via.placeholder.com/60x60.png?text=♪")
    with col2:
        st.write(os.path.basename(song))
        if st.button("Play", key=f"play_{idx}"):
            current_song = song

# Play selected song
if current_song:
    st.markdown("---")
    st.subheader(f"Now Playing: {os.path.basename(current_song)}")
    display_waveform(current_song)

# Playlist Save/Load
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    pl_name = st.text_input("Save Playlist As")
    if st.button("💾 Save Playlist"):
        if pl_name:
            save_playlist(pl_name, playlist)
            st.success("Playlist saved")
with col2:
    pl_files = [f.replace(".json", "") for f in os.listdir("playlists") if f.endswith(".json")]
    selected = st.selectbox("Load Playlist", pl_files)
    if st.button("📂 Load Playlist"):
        playlist = load_playlist(selected)
        st.success("Playlist loaded")
