import streamlit as st
import yt_dlp
import tempfile
import os

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("YouTube Downloader (Safe 1080p+)")

url = st.text_input("Enter YouTube URL:")

formats = []
selected_format_id = None

if url:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            # Get all formats that are video or video+audio
            formats = [f for f in info['formats'] if f.get('height')]
            format_options = []
            for f in formats:
                audio_flag = "with audio" if f.get('acodec') != "none" else "video-only"
                label = f"{f.get('height')}p ({audio_flag}) - {f.get('format_id')}"
                format_options.append(label)
            selected_label = st.selectbox("Select Quality", format_options)
            if selected_label:
                # Extract format_id from label
                selected_format_id = selected_label.split("-")[-1].strip()
    except Exception as e:
        st.error(f"Failed to fetch formats: {e}")

if st.button("Download Video") and url and selected_format_id:
    temp_path = tempfile.gettempdir()
    ydl_opts = {
        'format': selected_format_id,
        'outtmpl': os.path.join(temp_path, '%(title)s.%(ext)s'),
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
