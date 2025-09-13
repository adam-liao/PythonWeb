# 2025/09/13-13:25 沒有使用過
#"/Users/adamliao/文件/PythonWeb/.venv/bin/python3" /Users/adamliao/文件/PythonWeb/you2bedownload/yt2text_batch.py   --file /Users/adamliao/文件/PythonWeb/you2bedownload/urls.txt
#"/Users/adamliao/文件/PythonWeb/.venv/bin/python3" /Users/adamliao/文件/PythonWeb/you2bedownload/yt2text_batch.py   --file ~/download/urls.txt
import os
import re
import sys
import shutil
import datetime
from pathlib import Path
import argparse
import textwrap

import yt_dlp
from faster_whisper import WhisperModel


# ========== 工具 ==========
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

def write_srt(segments, srt_path: Path, width: int | None):
    with srt_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            text = seg["text"].strip()
            if width and width > 0:
                text = textwrap.fill(text, width=width)
            f.write(f"{i}\n{srt_timestamp(seg['start'])} --> {srt_timestamp(seg['end'])}\n{text}\n\n")

_SENT_SPLIT_RE = re.compile(r'([。！？；…]|(?<!\d)[.](?!\d))')  # 英文句號避免小數點
def wrap_plain_text(text: str, by_punct: bool, width: int | None) -> str:
    text = text.strip()
    if not text:
        return ""
    if not by_punct and (not width or width <= 0):
        return text + "\n"

    lines = []
    if by_punct:
        parts = _SENT_SPLIT_RE.split(text)
        sentences, buf = [], ""
        for part in parts:
            if _SENT_SPLIT_RE.fullmatch(part):
                sentences.append(buf + part); buf = ""
            else:
                buf = (buf + part) if buf else part
        if buf.strip():
            sentences.append(buf)
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if width and width > 0:
                lines.extend(textwrap.wrap(s, width=width))
            else:
                lines.append(s)
    else:
        if width and width > 0:
            lines = textwrap.wrap(text, width=width)
        else:
            lines = [text]
    return "\n".join(lines) + "\n"


# ========== 1) 嘗試抓字幕 ==========
def try_download_subtitles(url: str, out_dir: Path, langs: list[str]) -> tuple[Path | None, str]:
    ensure_dir(out_dir)
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = slugify(info.get("title") or "youtube_video")

    base = out_dir / title
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": langs,
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

    srt_candidates = sorted(out_dir.glob(f"{title}*.srt"))
    return (srt_candidates[0] if srt_candidates else None), title


# ========== 2) 沒字幕就抓音訊 ==========
def download_audio(url: str, out_dir: Path, audio_ext="wav") -> Path:
    ensure_dir(out_dir)
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


# ========== 3) faster-whisper 轉錄 ==========
def transcribe_faster_whisper(
    audio_path: Path,
    out_dir: Path,
    model_size: str,
    language: str | None,
    srt_wrap_width: int | None,
    txt_wrap_by_punct: bool,
    txt_wrap_width: int | None,
):
    print("③ 載入轉錄模型…（首次會讀快取/下載）")
    model = WhisperModel(
        model_size,
        device="cpu",               # Apple Silicon 上 CPU 後端穩定
        compute_type="int8",        # 相容性高
        cpu_threads=os.cpu_count()  # 吃滿執行緒
    )

    print("④ 開始轉錄…")
    seg_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
        vad_parameters={"min_speech_duration_ms": 300},
        beam_size=1,
        best_of=1,
    )

    segments, full_text = [], []
    n = 0
    for seg in seg_iter:
        n += 1
        if n % 10 == 1:
            print(f"   進度：第 {n} 段，{seg.start:.1f}s → {seg.end:.1f}s")
        segments.append({"start": seg.start, "end": seg.end, "text": seg.text})
        full_text.append(seg.text)

    title = audio_path.stem
    txt_path = out_dir / f"{title}.txt"
    srt_path = out_dir / f"{title}.srt"

    # 寫 .txt（預設不換行；可由參數控制）
    raw_text = ("".join(full_text)).strip()
    pretty = wrap_plain_text(raw_text, by_punct=txt_wrap_by_punct, width=txt_wrap_width)
    txt_path.write_text(pretty, encoding="utf-8")

    # 寫 .srt（可設定每行寬度）
    write_srt(segments, srt_path, width=srt_wrap_width)

    print("✅ 轉錄完成：")
    print("   TXT →", txt_path)
    print("   SRT →", srt_path)
    return txt_path, srt_path


# ========== 主流程（批次） ==========
def process_url(
    url: str,
    out_dir: Path,
    langs: list[str],
    model_size: str,
    language: str | None,
    srt_wrap_width: int | None,
    txt_wrap_by_punct: bool,
    txt_wrap_width: int | None,
):
    print(f"\n=== 處理：{url} ===")
    if shutil.which("ffmpeg") is None:
        print("⚠️ 找不到 ffmpeg（macOS：brew install ffmpeg）")

    srt_path, _title = try_download_subtitles(url, out_dir)
    if srt_path and srt_path.exists():
        print(f"✅ 找到字幕：{srt_path}")
        # 另存 .txt（去除序號與時間）
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
        # 依使用者設定的 txt wrap 來寫
        txt_pretty = wrap_plain_text("\n".join(buf), by_punct=txt_wrap_by_punct, width=txt_wrap_width)
        txt_path.write_text(txt_pretty, encoding="utf-8")
        print(f"✅ 已輸出純文字：{txt_path}")
        return

    audio_path = download_audio(url, out_dir, audio_ext="wav")
    transcribe_faster_whisper(
        audio_path, out_dir, model_size, language,
        srt_wrap_width, txt_wrap_by_punct, txt_wrap_width
    )


def read_urls_from_file(fpath: Path) -> list[str]:
    urls = []
    for line in fpath.read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        urls.append(t)
    return urls


def main():
    parser = argparse.ArgumentParser(
        description="YouTube → 字幕/逐字稿（多 URL 批次），優先抓字幕，否則下載音訊並轉錄"
    )
    parser.add_argument("urls", nargs="*", help="YouTube 連結（可多個）")
    parser.add_argument("-f", "--file", type=str, help="包含多個 URL 的文字檔（每行一個，支援 # 註解）")
    parser.add_argument("-o", "--outdir", type=str, default=os.path.expanduser("~/Downloads/YT2Text"),
                        help="輸出資料夾（預設：~/Downloads/YT2Text）")
    parser.add_argument("--lang", type=str, default="zh", help='強制語言，如 "zh"；自動偵測用 None')
    parser.add_argument("--model", type=str, default="small",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="faster-whisper 模型大小（預設 small）")
    parser.add_argument("--subs", type=str, default="zh-Hant,zh-TW,zh,zh-Hans,en",
                        help="字幕語言優先序（逗點分隔）")
    parser.add_argument("--srt-width", type=int, default=28, help="SRT 每行字數上限（0=不限制）")
    parser.add_argument("--txt-wrap-punct", action="store_true",
                        help="TXT 依標點換行（預設不開）")
    parser.add_argument("--txt-width", type=int, default=0,
                        help="TXT 固定行寬（0=不固定；可與 --txt-wrap-punct 併用）")
    args = parser.parse_args()

    out_dir = Path(args.outdir)
    ensure_dir(out_dir)
    langs = [t.strip() for t in args.subs.split(",") if t.strip()]

    urls = []
    if args.file:
        urls.extend(read_urls_from_file(Path(args.file)))
    urls.extend(args.urls)
    # 去重保序
    seen, deduped = set(), []
    for u in urls:
        if u not in seen:
            deduped.append(u); seen.add(u)

    if not deduped:
        print("請提供至少一個 URL，或使用 --file 指定清單檔。")
        sys.exit(1)

    for url in deduped:
        try:
            process_url(
                url=url,
                out_dir=out_dir,
                langs=langs,
                model_size=args.model,
                language=(None if args.lang.lower() == "none" else args.lang),
                srt_wrap_width=(None if args.srt_width <= 0 else args.srt_width),
                txt_wrap_by_punct=bool(args.txt_wrap_punct),
                txt_wrap_width=(None if args.txt_width <= 0 else args.txt_width),
            )
        except Exception as e:
            print(f"❌ 失敗：{url} — {e}")

if __name__ == "__main__":
    main()
    
    
