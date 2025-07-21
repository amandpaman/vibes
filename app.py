import streamlit as st
import base64
from tinytag import TinyTag
import time
from io import BytesIO

# --- Custom CSS for UI Styling ---
def load_css():
    st.markdown("""
    <style>
        /* Main Container */
        .stApp {
            background-color: #1E1E1E;
            color: white;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #4ECDC4;
            color: white;
            border-radius: 10px;
            padding: 8px 16px;
            transition: all 0.3s;
            margin: 2px;
        }
        .stButton>button:hover {
            background-color: #FF6B6B !important;
            transform: scale(1.05);
        }
        
        /* Player Controls Container */
        .player-controls {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 15px 0;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize Session State ---
if 'current_song' not in st.session_state:
    st.session_state.current_song = None
if 'volume' not in st.session_state:
    st.session_state.volume = 70
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'audio_id' not in st.session_state:
    st.session_state.audio_id = 0  # Used to force audio reload

# --- Metadata Extraction ---
def get_metadata(file):
    try:
        if isinstance(file, BytesIO):
            file.seek(0)
            tag = TinyTag.get(file)
        else:
            tag = TinyTag.get(file.name)
        return {
            'title': tag.title or os.path.basename(file.name if hasattr(file, 'name') else "Unknown"),
            'artist': tag.artist or "Unknown Artist",
            'album': tag.album or "Unknown Album",
            'duration': tag.duration
        }
    except:
        return {
            'title': os.path.basename(file.name) if hasattr(file, 'name') else "Unknown",
            'artist': "Unknown Artist",
            'album': "Unknown Album",
            'duration': 0
        }

# --- Audio Player Component ---
def audio_player():
    if st.session_state.current_song:
        audio_bytes = st.session_state.current_song.read()
        audio_str = f"data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}"
        
        # Unique ID to force reload when changing tracks
        audio_id = st.session_state.audio_id
        
        st.markdown(f"""
        <audio id="audio_{audio_id}" {'autoplay' if st.session_state.is_playing else ''}>
            <source src="{audio_str}" type="audio/mp3">
        </audio>
        <script>
            const audio = document.getElementById("audio_{audio_id}");
            audio.volume = {st.session_state.volume/100};
            
            function togglePlay() {{
                if (audio.paused) {{
                    audio.play();
                    parent.window.postMessage({{type: 'playStatus', isPlaying: true}}, '*');
                }} else {{
                    audio.pause();
                    parent.window.postMessage({{type: 'playStatus', isPlaying: false}}, '*');
                }}
            }}
            
            // Update Streamlit when audio ends
            audio.addEventListener('ended', function() {{
                parent.window.postMessage({{type: 'songEnded'}}, '*');
            }});
        </script>
        """, unsafe_allow_html=True)

# --- Main App ---
def main():
    load_css()
    st.title("🎧 Advanced Music Player")
    
    # JavaScript communication
    st.components.v1.html("""
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'playStatus') {
                Streamlit.setComponentValue({
                    isPlaying: event.data.isPlaying,
                    action: "updatePlayStatus"
                });
            }
            if (event.data.type === 'songEnded') {
                Streamlit.setComponentValue({
                    action: "nextSong"
                });
            }
        });
    </script>
    """, height=0)
    
    # Handle JS events
    if 'action' in st.session_state:
        if st.session_state.action == "updatePlayStatus":
            st.session_state.is_playing = st.session_state.isPlaying
        elif st.session_state.action == "nextSong" and st.session_state.playlist:
            st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.playlist)
            st.session_state.current_song = st.session_state.playlist[st.session_state.current_index]
            st.session_state.audio_id += 1
            st.session_state.is_playing = True
            st.experimental_rerun()

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("🔊 Volume Control")
        st.session_state.volume = st.slider(
            "Volume", 0, 100, st.session_state.volume, key="volume_slider"
        )

        st.subheader("🎶 Playlist Management")
        uploaded_files = st.file_uploader(
            "Add songs to playlist", type=["mp3", "wav", "ogg"], accept_multiple_files=True
        )
        if uploaded_files:
            st.session_state.playlist.extend(uploaded_files)
            st.success(f"Added {len(uploaded_files)} songs!")

        if st.button("Clear Playlist"):
            st.session_state.playlist = []
            st.session_state.current_song = None
            st.session_state.is_playing = False
            st.experimental_rerun()

        if st.session_state.playlist:
            st.write("**Playlist:**")
            for i, song in enumerate(st.session_state.playlist):
                cols = st.columns([1, 4])
                with cols[0]:
                    if st.button("▶", key=f"play_{i}"):
                        st.session_state.current_index = i
                        st.session_state.current_song = song
                        st.session_state.audio_id += 1
                        st.session_state.is_playing = True
                        st.experimental_rerun()
                with cols[1]:
                    metadata = get_metadata(song)
                    st.write(f"{i+1}. {metadata['title']}")

    # --- Main Player Area ---
    if st.session_state.current_song:
        metadata = get_metadata(st.session_state.current_song)
        
        # Metadata Display
        with st.container():
            st.markdown(f"""
            <div style="background-color: #2E2E2E; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <h3>{metadata['title']}</h3>
                <p>👨‍🎤 Artist: {metadata['artist']}</p>
                <p>💿 Album: {metadata['album']}</p>
                <p>⏱ Duration: {int(metadata['duration']//60)}:{int(metadata['duration']%60):02d}</p>
            </div>
            """, unsafe_allow_html=True)

        # Audio Player (hidden)
        audio_player()

        # Player Controls
        st.markdown("<div class='player-controls'>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⏮ Previous") and st.session_state.playlist:
                st.session_state.current_index = (st.session_state.current_index - 1) % len(st.session_state.playlist)
                st.session_state.current_song = st.session_state.playlist[st.session_state.current_index]
                st.session_state.audio_id += 1
                st.session_state.is_playing = True
                st.experimental_rerun()
        with col2:
            play_pause_text = "⏸ Pause" if st.session_state.is_playing else "▶ Play"
            if st.button(play_pause_text):
                st.session_state.is_playing = not st.session_state.is_playing
                st.session_state.audio_id += 1  # Force reload to trigger JS
                st.experimental_rerun()
        with col3:
            if st.button("⏭ Next") and st.session_state.playlist:
                st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.playlist)
                st.session_state.current_song = st.session_state.playlist[st.session_state.current_index]
                st.session_state.audio_id += 1
                st.session_state.is_playing = True
                st.experimental_rerun()
        with col4:
            if st.button("🗑 Remove"):
                st.session_state.playlist.pop(st.session_state.current_index)
                if st.session_state.playlist:
                    st.session_state.current_index = min(st.session_state.current_index, len(st.session_state.playlist)-1)
                    st.session_state.current_song = st.session_state.playlist[st.session_state.current_index]
                else:
                    st.session_state.current_song = None
                    st.session_state.is_playing = False
                st.experimental_rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("👆 Add songs to your playlist using the sidebar")

if __name__ == "__main__":
    main()
