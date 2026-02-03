import streamlit as st
import yt_dlp
import tempfile
import os

# -------------------- Page config --------------------
st.set_page_config(page_title="YouTube Downloader", page_icon="📥", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            height: 3em;
            width: 100%;
            border-radius: 10px;
            border: none;
        }
        .stTextInput>div>div>input {
            height: 3em;
            border-radius: 10px;
            border: 1px solid #ccc;
            padding-left: 10px;
        }
        .stSelectbox>div>div>div>select {
            height: 3em;
            border-radius: 10px;
            padding-left: 10px;
        }
        .stProgress>div>div>div>div {
            background-color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- Header --------------------
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>YouTube Video Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>Download YouTube videos in your preferred quality (1080p+ supported)</p>", unsafe_allow_html=True)

# -------------------- URL input --------------------
with st.container():
    st.markdown("### Enter YouTube URL")
    url = st.text_input("", placeholder="https://www.youtube.com/watch?v=example")

formats = []
selected_quality = None

# -------------------- Fetch qualities --------------------
if url:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [f for f in info['formats'] if f.get('height')]
            qualities = []
            for f in formats:
                audio_flag = "with audio" if f.get('acodec') != "none" else "video-only"
                qualities.append(f"{f['height']}p ({audio_flag})")
            selected_quality = st.selectbox("Select Quality", qualities)
    except Exception as e:
        st.error(f"Failed to fetch qualities: {e}")

# -------------------- Download video --------------------
if st.button("Download Video") and url and selected_quality:
    height = int(selected_quality.split("p")[0])

    ydl_opts = {
        'format': f'bestvideo[height={height}]+bestaudio/best[height={height}]',
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': []
    }

    progress_bar = st.progress(0)
    status = st.empty()

    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percent = downloaded / total
            progress_bar.progress(min(percent, 1.0))
            status.text(f"Downloading... {percent*100:.2f}%")
        elif d['status'] == 'finished':
            status.text("Download finished!")

    ydl_opts['progress_hooks'] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url)
            filename = ydl.prepare_filename(info_dict)

        st.success("✅ Download completed!")
        st.download_button(
            label="📥 Click to Save Video",
            data=open(filename, 'rb'),
            file_name=os.path.basename(filename),
            mime="video/mp4"
        )
    except Exception as e:
        st.error(f"Download failed: {e}")

# -------------------- Footer --------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>Made with ❤️ using Streamlit and yt-dlp</p>", unsafe_allow_html=True)
