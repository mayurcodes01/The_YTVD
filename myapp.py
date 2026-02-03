import streamlit as st
import yt_dlp
import tempfile
import os

# -------------------- Page Config --------------------
st.set_page_config(page_title="YouTube Downloader", page_icon="📥", layout="centered")
st.title("YouTube Downloader (Highest Quality)")

# -------------------- URL Input --------------------
url = st.text_input("Enter YouTube URL:")

# -------------------- Download Button --------------------
if st.button("Download Highest Quality Video") and url:
    temp_path = tempfile.gettempdir()  # Temporary download location
    status = st.empty()
    progress_bar = st.progress(0)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Best video + best audio automatically merged
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(temp_path, '%(title)s.%(ext)s'),
        'progress_hooks': []
    }

    # Progress hook for Streamlit
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
            info_dict = ydl.extract_info(url, download=True)
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
