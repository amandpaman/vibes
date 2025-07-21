import streamlit as st
import os
import base64
import time
import tempfile
import shutil
import eyed3
import json
import pandas as pd
import requests
from mutagen.mp3 import MP3
from pydub import AudioSegment
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.app_logo import add_logo
from yt_dlp import YoutubeDL

# Ensure ffmpeg is in the PATH
os.environ["PATH"] += os.pathsep + "/usr/bin"

st.set_page_config(page_title="Vibes Music Player", layout="wide")
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        .stTextInput, .stFileUploader, .stButton, .stSelectbox {
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 Vibes Music Player")

uploaded_files = st.file_uploader("Upload MP3 Files", accept_multiple_files=True, type=['mp3'])

playlist = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name
            audio = MP3(file_path)
            duration = audio.info.length
            playlist.append({
                'title': uploaded_file.name,
                'file_path': file_path,
                'duration': duration
            })

    current_track = st.selectbox("Select a track", options=[track['title'] for track in playlist])

    selected_track = next((track for track in playlist if track['title'] == current_track), None)
    if selected_track:
        audio_bytes = open(selected_track['file_path'], 'rb').read()
        st.audio(audio_bytes, format='audio/mp3')
        st.write(f"Duration: {int(selected_track['duration'] // 60)}:{int(selected_track['duration'] % 60):02d} minutes")

# YouTube Downloader
st.subheader("📥 Download from YouTube")
youtube_url = st.text_input("Enter YouTube URL")

if st.button("Download and Play") and youtube_url:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': '/usr/bin'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = f"downloads/{info['title']}.mp3"

            st.success(f"Downloaded: {info['title']}")
            audio_bytes = open(filename, 'rb').read()
            st.audio(audio_bytes, format='audio/mp3')

    except Exception as e:
        st.error(f"Error downloading from YouTube: {str(e)}")

# Save/Load Playlist
st.subheader("💾 Save / Load Playlist")
playlist_name = st.text_input("Playlist Name")

if st.button("Save Playlist") and playlist and playlist_name:
    with open(f"{playlist_name}.json", 'w') as f:
        json.dump(playlist, f)
    st.success("Playlist saved!")

if st.button("Load Playlist") and playlist_name:
    try:
        with open(f"{playlist_name}.json", 'r') as f:
            loaded = json.load(f)
            playlist = loaded
        st.success("Playlist loaded!")
    except FileNotFoundError:
        st.error("Playlist file not found.")

# Waveform simulation (basic progress bar)
if playlist:
    st.subheader("🔊 Real-Time Playback Progress")
    progress_placeholder = st.empty()
    play_button = st.button("Simulate Progress")
    if play_button:
        for i in range(100):
            time.sleep(0.1)
            progress_placeholder.progress(i + 1)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
