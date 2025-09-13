# 2025/05/18-10:45
import yt_dlp

# 影片網址（可以改成你要下載的）
video_url = "https://www.youtube.com/live/MNz1wuJ4LJQ"
video_url = "https://www.youtube.com/watch?v=QJjSLe8Kt4I&list=RDMMQJjSLe8Kt4I&start_radio=1"

# 設定 yt-dlp 的選項
ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # 選擇最佳畫質 mp4
    'outtmpl': '~/Downloads/%(title)s.%(ext)s',             # 
    
    'merge_output_format': 'mp4',                            # 合併後格式
    'noplaylist': True                                       # 不下載整個播放清單
}

# 開始下載
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
    
