import streamlit as st
import yt_dlp
import tempfile
import os

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("YouTube Video Downloader")

# Input YouTube URL
url = st.text_input("Enter YouTube URL:")

# Container for status messages
status_text = st.empty()

formats = []

if url:
    try:
        # Fetch available formats
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [f for f in info['formats'] if f.get('height')]
            qualities = [f"{f['height']}p" for f in formats]
        
        if qualities:
            selected_quality = st.selectbox("Select Quality", qualities)
        else:
            st.warning("No video formats with resolution available.")
            selected_quality = None
    except Exception as e:
        st.error(f"Failed to fetch qualities: {e}")
        selected_quality = None
else:
    selected_quality = None

# Download button
if st.button("Download Video") and url and selected_quality:
    # Find the format id
    format_id = None
    for f in formats:
        if f.get('height') and f['height'] == int(selected_quality.replace("p", "")):
            format_id = f['format_id']
            break

    if format_id:
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
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

            st.success("Download completed!")
            st.download_button(
                label="Click to Save Video",
                data=open(filename, 'rb'),
                file_name=os.path.basename(filename),
                mime="video/mp4"
            )
        except Exception as e:
            st.error(f"Download failed: {e}")
    else:
        st.error("Selected quality not available.")
