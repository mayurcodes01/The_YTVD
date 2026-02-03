import customtkinter as ctk
from tkinter import messagebox
import yt_dlp

# Initialize CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video Downloader")
        self.geometry("500x400")
        
        # URL input
        self.url_label = ctk.CTkLabel(self, text="YouTube URL:")
        self.url_label.pack(pady=(20, 5))
        self.url_entry = ctk.CTkEntry(self, width=400)
        self.url_entry.pack(pady=5)
        
        # Button to fetch available qualities
        self.fetch_button = ctk.CTkButton(self, text="Fetch Qualities", command=self.fetch_qualities)
        self.fetch_button.pack(pady=10)
        
        # Quality dropdown
        self.quality_var = ctk.StringVar()
        self.quality_dropdown = ctk.CTkOptionMenu(self, values=[], variable=self.quality_var)
        self.quality_dropdown.pack(pady=10)
        
        # Download button
        self.download_button = ctk.CTkButton(self, text="Download Video", command=self.download_video)
        self.download_button.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=10)
        
        # Store formats
        self.formats = []
    
    def fetch_qualities(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        self.status_label.configure(text="Fetching available qualities...")
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                self.formats = [f for f in info['formats'] if f.get('height')]  # only video formats with resolution
                qualities = [f"{f['height']}p" for f in self.formats]
                self.quality_dropdown.configure(values=qualities)
                if qualities:
                    self.quality_var.set(qualities[0])
                self.status_label.configure(text="Select quality and click download")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch qualities:\n{e}")
            self.status_label.configure(text="")
    
    def download_video(self):
        url = self.url_entry.get()
        selected_quality = self.quality_var.get()
        
        if not url or not selected_quality:
            messagebox.showerror("Error", "Please enter URL and select a quality")
            return
        
        # Find the format corresponding to selected quality
        format_to_download = None
        for f in self.formats:
            if f.get('height') and f['height'] == int(selected_quality.replace('p', '')):
                format_to_download = f['format_id']
                break
        
        if not format_to_download:
            messagebox.showerror("Error", "Selected quality not available")
            return
        
        self.status_label.configure(text="Downloading...")
        
        ydl_opts = {
            'format': format_to_download,
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook]
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="Download completed!")
            messagebox.showinfo("Success", "Video downloaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed:\n{e}")
            self.status_label.configure(text="")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percent = downloaded / total * 100
            self.status_label.configure(text=f"Downloading... {percent:.2f}%")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
