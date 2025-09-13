# 2025/09/13-11:20
import os
import re
import sys
import json
import datetime
from pathlib import Path

import yt_dlp

# ---- 你可以改這裡的影片網址 ----
VIDEO_URL = "https://youtu.be/6xXdlpmZwHI?si=-6rBOxq3LXGbZ6Ri"

# ---- 下載與輸出設定 ----
DOWNLOAD_DIR = os.path.expanduser("~/Downloads/YT2Text")  # 建議開一個子資料夾
PREFERRED_SUB_LANGS = ["zh-Hant", "zh-TW", "zh", "zh-Hans", "en"]  # 嘗試抓這些語言的字幕
AUDIO_FORMAT = "wav"  # 轉錄建議用無損/PCM (wav)
WHISPER_MODEL = "medium"  # 可改 "small" / "base" / "large-v3" 等
WHISPER_LANGUAGE = "zh"  # 設 None 自動偵測；若確定中文可設 "zh"

# ========== 工具函式 ==========
def slugify(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120]  # 避免檔名過長

def ensure_dir(p: str | Path):
    Path(p).mkdir(parents=True, exist_ok=True)

def srt_timestamp(sec: float) -> str:
    # 轉成 SRT 的 hh:mm:ss,ms
    td = datetime.timedelta(seconds=max(sec, 0))
    total_ms = int(td.total_seconds() * 1000)
    h, rem = divmod(total_ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def write_srt(segments, srt_path: Path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = srt_timestamp(seg["start"])
            end = srt_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

# ========== 第 1 階段：嘗試直接抓字幕 ==========
def try_download_subtitles(url: str, out_dir: Path) -> Path | None:
    """
    用 yt-dlp 嘗試下載官方字幕或自動字幕（優先使用 PREFERRED_SUB_LANGS）。
    成功時回傳 SRT 路徑，否則回傳 None。
    """
    ensure_dir(out_dir)
    # 先用 extract_info 拿到標題，組 outtmpl 用標題當檔名
    probe_opts = {"quiet": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = slugify(info.get("title") or "youtube_video")
    base = out_dir / title

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,  # 沒官方字幕就抓自動字幕
        "subtitleslangs": PREFERRED_SUB_LANGS,
        "subtitlesformat": "srt",
        "outtmpl": str(base) + ".%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [{"key": "FFmpegSubtitlesConvertor", "format": "srt"}],
    }

    had_subtitle = False
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            had_subtitle = True
        except Exception:
            had_subtitle = False

    if not had_subtitle:
        return None

    # 在輸出目錄中找對應的 .srt
    srt_candidates = list(out_dir.glob(f"{title}*.srt"))
    return srt_candidates[0] if srt_candidates else None

# ========== 第 2 階段：下載音訊 ==========
def download_audio(url: str, out_dir: Path, audio_ext=AUDIO_FORMAT) -> Path:
    ensure_dir(out_dir)
    # 先拿標題
    probe_opts = {"quiet": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(probe_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = slugify(info.get("title") or "youtube_audio")
    base = out_dir / title

    # 直接抽音並轉成目標格式（wav）
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(base) + ".%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": audio_ext, "preferredquality": "0"},
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # 下載後的檔名會是 base + .wav
    audio_path = out_dir / f"{base.name}.{audio_ext}"
    if not audio_path.exists():
        # 有些情況副檔名可能是大寫或其他，嘗試抓第一個同名開頭的 wav
        candidates = list(out_dir.glob(f"{base.name}*.{audio_ext}"))
        if not candidates:
            raise FileNotFoundError("找不到轉出的音訊檔。")
        audio_path = candidates[0]
    return audio_path

# ========== 第 3 階段：Whisper 轉錄 ==========
def transcribe_with_whisper(audio_path: Path, out_dir: Path, model_name=WHISPER_MODEL, language=WHISPER_LANGUAGE):
    import whisper  # 需要: pip install openai-whisper

    model = whisper.load_model(model_name)
    # 你也可以加入 fp16=False 來兼容 CPU（沒有 GPU）
    result = model.transcribe(str(audio_path), language=language)

    title = audio_path.stem
    txt_path = out_dir / f"{title}.txt"
    srt_path = out_dir / f"{title}.srt"

    # 儲存純文字
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result.get("text", "").strip() + "\n")

    # 儲存 SRT（根據 segments）
    segments = result.get("segments", [])
    if segments:
        write_srt(segments, srt_path)

    return txt_path, (srt_path if srt_path.exists() else None)

# ========== 主流程 ==========
def main():
    out_dir = Path(DOWNLOAD_DIR)
    ensure_dir(out_dir)

    print("① 嘗試下載字幕（若有官方或自動字幕會直接使用）…")
    srt_path = try_download_subtitles(VIDEO_URL, out_dir)
    if srt_path:
        print(f"✅ 找到字幕：{srt_path}")
        # 同步輸出一份 .txt（把 SRT 轉純文字）
        txt_path = srt_path.with_suffix(".txt")
        with open(srt_path, "r", encoding="utf-8") as f_in, open(txt_path, "w", encoding="utf-8") as f_out:
            # 簡單去除 SRT 序號與時間戳
            buf = []
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                if re.match(r"^\d+$", line):
                    continue
                if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} --> ", line):
                    continue
                buf.append(line)
            f_out.write("\n".join(buf) + "\n")
        print(f"✅ 已輸出純文字：{txt_path}")
        return

    print("② 沒有字幕，改下載音訊並使用 Whisper 轉錄…")
    audio_path = download_audio(VIDEO_URL, out_dir, audio_ext=AUDIO_FORMAT)
    print(f"✅ 音訊已就緒：{audio_path}")

    txt_path, srt_from_whisper = transcribe_with_whisper(audio_path, out_dir)
    print(f"✅ Whisper 轉錄完成：{txt_path}")
    if srt_from_whisper:
        print(f"✅ Whisper SRT：{srt_from_whisper}")
    else:
        print("⚠️ Whisper 沒有輸出 SRT（可能沒有 segments）")

if __name__ == "__main__":
    """
    先決條件：
      1) 安裝 ffmpeg：macOS 可用 `brew install ffmpeg`
      2) 安裝 yt-dlp：  `pip install -U yt-dlp`
      3) 安裝 Whisper：  `pip install -U openai-whisper`   # 首次使用會下載模型
         - 若想更快可用 `pip install -U faster-whisper`，但程式需改用其 API。
    """
    try:
        main()
    except Exception as e:
        print("發生錯誤：", e)
        sys.exit(1)