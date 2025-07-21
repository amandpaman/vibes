import streamlit as st
from pytube import YouTube
import os
import uuid

# Page config and custom CSS for effective UI
st.set_page_config(page_title="🎵 Vibes Music Player", layout="wide")

st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #1CB5E0, #000851);
            color: white;
        }
        .stButton > button {
            background-color: #FF4B2B;
            color: white;
            border-radius: 10px;
            padding: 0.5rem 1rem;
        }
        .stTextInput > div > input {
            background-color: #f0f2f6;
            color: #111;
            border-radius: 10px;
            padding: 0.5rem;
        }
        .stFileUploader {
            background-color: #f0f2f6;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Title and header
st.title("🎵 Vibes Music Player")
st.markdown("#### Listen to local MP3s or stream audio from YouTube!")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Sidebar for navigation
st.sidebar.title("🔊 Select Source")
option = st.sidebar.radio("Choose an option", ["📁 Upload MP3", "▶️ YouTube Link"])

# Function to play audio from file
def play_audio(file_path, label="Audio Playback"):
    with open(file_path, 'rb') as f:
        audio_bytes = f.read()
        st.markdown(f"**{label}**")
        st.audio(audio_bytes, format="audio/mp3")

# Handle Uploads
if option == "📁 Upload MP3":
    uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])
    if uploaded_file is not None:
        file_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded: {uploaded_file.name}")
        play_audio(file_path, label=uploaded_file.name)

# Handle YouTube Download and Playback
elif option == "▶️ YouTube Link":
    yt_url = st.text_input("Enter YouTube URL:")
    if yt_url:
        try:
            yt = YouTube(yt_url)
            stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
            if stream:
                filename = f"{uuid.uuid4()}.mp4"
                download_path = os.path.join(DOWNLOAD_DIR, filename)

                with st.spinner("Downloading audio..."):
                    stream.download(output_path=DOWNLOAD_DIR, filename=filename)

                st.success(f"Audio downloaded: {yt.title}")
                play_audio(download_path, label=yt.title)

            else:
                st.warning("No suitable audio stream found.")
        except Exception as e:
            st.error(f"Error: {e}")
