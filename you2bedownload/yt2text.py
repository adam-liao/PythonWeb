# 2025/09/13-12:45 OK
#"/Users/adamliao/文件/PythonWeb/.venv/bin/python3" /Users/adamliao/文件/PythonWeb/you2bedownload/yt2text.py
import os
import re
import shutil
import datetime
from pathlib import Path
import textwrap

import yt_dlp
from faster_whisper import WhisperModel


# ========= 可調參數 =========
# 1) 要處理的 YouTube 連結（更改這行就能換影片）
VIDEO_URL = "https://youtube.com/live/MNz1wuJ4LJQ"

# 2) 輸出資料夾（預設放在 ~/Downloads/YT2Text）
DOWNLOAD_DIR = os.path.expanduser("~/Downloads/YT2Text")

# 3) 若影片多為中文，建議固定語言 "zh"（不確定可設 None 自動偵測）
FORCE_LANGUAGE = "zh"  # 或 None

# 4) 模型大小：tiny/base/small/medium/large-v3
MODEL_SIZE = "small"   # M4 上建議先用 small（速度/準度平衡）

# 5) 嘗試抓的字幕語言優先序
PREFERRED_SUB_LANGS = ["zh-Hant", "zh-TW", "zh", "zh-Hans", "en"]

# 6) SRT 每行最大字元數（讓字幕較好讀）
SRT_WRAP_WIDTH = 28


# ========= 小工具 =========
def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def slugify(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120]

def srt_timestamp(sec: float) -> str:
    td = datetime.timedelta(seconds=max(sec, 0))
    total_ms = int(td.total_seconds() * 1000)
    h, rem = divmod(total_ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def write_srt(segments, srt_path: Path, width=SRT_WRAP_WIDTH):
    with srt_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            text = textwrap.fill(seg["text"].strip(), width=width)
            f.write(f"{i}\n{srt_timestamp(seg['start'])} --> {srt_timestamp(seg['end'])}\n{text}\n\n")


# ========= 1) 先嘗試抓字幕 =========
def try_download_subtitles(url: str, out_dir: Path) -> tuple[Path | None, str]:
    """
    嘗試下載官方/自動字幕（優先 PREFERRED_SUB_LANGS）
    回傳：(srt_path or None, normalized_title)
    """
    ensure_dir(out_dir)

    # 先探測影片資訊，取標題
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = slugify(info.get("title") or "youtube_video")

    base = out_dir / title
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": PREFERRED_SUB_LANGS,
        "subtitlesformat": "srt",
        "outtmpl": str(base) + ".%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [{"key": "FFmpegSubtitlesConvertor", "format": "srt"}],
    }

    print("① 嘗試下載字幕…")
    had_sub = False
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            had_sub = True
    except Exception:
        had_sub = False

    if not had_sub:
        return None, title

    # 取得第一個 srt
    srt_candidates = sorted(out_dir.glob(f"{title}*.srt"))
    return (srt_candidates[0] if srt_candidates else None), title


# ========= 2) 沒字幕就抓音訊（wav） =========
def download_audio(url: str, out_dir: Path, audio_ext="wav") -> Path:
    ensure_dir(out_dir)

    # 先探測標題
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = slugify(info.get("title") or "youtube_audio")

    base = out_dir / title
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(base) + ".%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": audio_ext, "preferredquality": "0"},
        ],
    }

    print("② 沒有字幕，改下載音訊…")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    audio_path = out_dir / f"{base.name}.{audio_ext}"
    if not audio_path.exists():
        candidates = sorted(out_dir.glob(f"{base.name}*.{audio_ext}"))
        if not candidates:
            raise FileNotFoundError("找不到轉出的音訊檔")
        audio_path = candidates[0]

    print(f"✅ 音訊已就緒：{audio_path}")
    return audio_path


# ========= 3) 用 faster-whisper 轉錄 =========
def transcribe_with_faster_whisper(audio_path: Path, out_dir: Path, model_size=MODEL_SIZE, language=FORCE_LANGUAGE):
    print("③ 載入轉錄模型…（首次會讀快取/下載）")
    model = WhisperModel(
        model_size,
        device="cpu",                # 在 Apple Silicon 上用 CPU 後端最穩
        compute_type="int8",         # 相容性高、速度佳
        cpu_threads=os.cpu_count()   # 吃滿 CPU 執行緒
    )

    print("④ 開始轉錄…")
    seg_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
        vad_parameters={"min_speech_duration_ms": 300},
        beam_size=1,   # 貪婪解碼，較快
        best_of=1,
    )

    segments, full_text = [], []
    n = 0
    for seg in seg_iter:
        n += 1
        if n % 10 == 1:  # 每 10 段回報一次進度
            print(f"   進度：第 {n} 段，{seg.start:.1f}s → {seg.end:.1f}s")
        segments.append({"start": seg.start, "end": seg.end, "text": seg.text})
        full_text.append(seg.text)

    title = audio_path.stem
    txt_path = out_dir / f"{title}.txt"
    srt_path = out_dir / f"{title}.srt"

    txt_path.write_text(("".join(full_text)).strip() + "\n", encoding="utf-8")
    write_srt(segments, srt_path)

    print("✅ 轉錄完成：")
    print("   TXT →", txt_path)
    print("   SRT →", srt_path)
    return txt_path, srt_path


# ========= 主流程 =========
def main():
    out_dir = Path(DOWNLOAD_DIR)
    ensure_dir(out_dir)

    if shutil.which("ffmpeg") is None:
        print("⚠️ 找不到 ffmpeg，請在 macOS 裝：brew install ffmpeg")

    srt_path, title = try_download_subtitles(VIDEO_URL, out_dir)
    if srt_path and srt_path.exists():
        print(f"✅ 找到字幕：{srt_path}")
        # 另存純文字（去除序號與時間戳）
        txt_path = srt_path.with_suffix(".txt")
        buf = []
        for line in srt_path.read_text(encoding="utf-8").splitlines():
            t = line.strip()
            if not t:
                continue
            if re.fullmatch(r"\d+", t):
                continue
            if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} --> ", t):
                continue
            buf.append(t)
        txt_path.write_text("\n".join(buf) + "\n", encoding="utf-8")
        print(f"✅ 已輸出純文字：{txt_path}")
        return

    # 沒有字幕 → 下載音訊並轉錄
    audio_path = download_audio(VIDEO_URL, out_dir, audio_ext="wav")
    transcribe_with_faster_whisper(audio_path, out_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("發生錯誤：", e)
        traceback.print_exc()
        raise