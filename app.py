import streamlit as st
import os
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image
import io
import time
import json

# Initialize the mixer
pygame.mixer.init()

# Global variables
current_track = None
music_dir = "music"  # Your folder where mp3 files are stored

# Function to load songs from directory
def load_songs():
    return [file for file in os.listdir(music_dir) if file.endswith(".mp3")]

# Extract album art from MP3 metadata
def extract_album_art(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return Image.open(io.BytesIO(tag.data))
    except Exception:
        return None

# Load song and play it
def play_song(song_file):
    global current_track
    pygame.mixer.music.load(song_file)
    pygame.mixer.music.play()
    current_track = song_file

# Save playlist to JSON
def save_playlist(playlist, name="playlist.json"):
    with open(name, "w") as f:
        json.dump(playlist, f)

# Load playlist from JSON
def load_playlist(name="playlist.json"):
    if os.path.exists(name):
        with open(name, "r") as f:
            return json.load(f)
    return []

# Real-time progress bar
def show_progress(duration):
    progress = st.progress(0)
    for i in range(duration):
        if not pygame.mixer.music.get_busy():
            break
        time.sleep(1)
        progress.progress(min((i + 1) / duration, 1.0))

# Streamlit UI starts here
st.set_page_config(layout="centered")
st.markdown("""
    <style>
        .block-container {
            background: linear-gradient(to right, #232526, #414345);
            color: white;
        }
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            font-weight: bold;
            padding: 10px;
        }
        .stTextInput>div>div>input {
            background-color: #1f1f1f;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 Vibes Music Player")

songs = load_songs()
playlist = load_playlist()

col1, col2 = st.columns(2)

with col1:
    selected_song = st.selectbox("Select a song to play", songs)
    if st.button("▶️ Play"):
        full_path = os.path.join(music_dir, selected_song)
        play_song(full_path)

        # Show album art
        art = extract_album_art(full_path)
        if art:
            st.image(art, width=250)
        else:
            st.warning("No album artwork found.")

        # Show progress
        song_info = MP3(full_path)
        duration = int(song_info.info.length)
        show_progress(duration)

with col2:
    st.subheader("📁 Playlist")
    playlist_name = st.text_input("Save as (filename):", value="playlist.json")

    if st.button("➕ Add to Playlist"):
        if selected_song not in playlist:
            playlist.append(selected_song)
            st.success(f"{selected_song} added to playlist")

    if st.button("💾 Save Playlist"):
        save_playlist(playlist, name=playlist_name)
        st.success("Playlist saved")

    if st.button("📂 Load Playlist"):
        playlist = load_playlist(name=playlist_name)
        st.success("Playlist loaded")

    if playlist:
        st.write("Your Playlist:")
        for song in playlist:
            st.markdown(f"- {song}")

# Footer
st.markdown("""
    <hr>
    <center>🎶 Made with ❤️ by Aman • Streamlit Music App</center>
""", unsafe_allow_html=True)
