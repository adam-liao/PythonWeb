# 2025/09/13-12:20
from pathlib import Path
import sys, time, textwrap

AUDIO_PATH = Path("/Users/adamliao/Downloads/YT2Text/2025_05_27_早上.wav")
OUT_DIR    = AUDIO_PATH.parent
MODEL_SIZE = "small"      # 比 medium 輕很多，先確保能跑完
LANG       = "zh"         # 若內容主要中文，固定語言較穩；不確定可改 None

def srt_timestamp(sec: float) -> str:
    ms = int(max(sec, 0) * 1000)
    h, r = divmod(ms, 3600_000)
    m, r = divmod(r, 60_000)
    s, ms = divmod(r, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def write_srt(segments, srt_path: Path, width=28):
    with srt_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            text = textwrap.fill(seg["text"].strip(), width=width)
            f.write(f"{i}\n{srt_timestamp(seg['start'])} --> {srt_timestamp(seg['end'])}\n{text}\n\n")

def main():
    print("python =", sys.executable)
    if not AUDIO_PATH.exists():
        print("找不到音訊檔：", AUDIO_PATH)
        sys.exit(1)

    from faster_whisper import WhisperModel
    print("載入模型中（第一次會讀快取/下載）…", MODEL_SIZE)
    t0 = time.time()
    model = WhisperModel(MODEL_SIZE, device="auto", compute_type="int8_float16")
    print(f"模型就緒，耗時 {time.time()-t0:.1f}s")

    print("開始轉錄…")
    seg_iter, info = model.transcribe(
        str(AUDIO_PATH),
        language=LANG,
        vad_filter=True,
        vad_parameters={"min_speech_duration_ms": 300},
    )

    segs, full = [], []
    n = 0
    for seg in seg_iter:
        n += 1
        if n % 10 == 1:
            print(f"  進度：第 {n} 段，{seg.start:.1f}s → {seg.end:.1f}s")
        segs.append({"start": seg.start, "end": seg.end, "text": seg.text})
        full.append(seg.text)

    title = AUDIO_PATH.stem
    txt_path = OUT_DIR / f"{title}.txt"
    srt_path = OUT_DIR / f"{title}.srt"

    # 輸出
    txt_path.write_text(("".join(full)).strip() + "\n", encoding="utf-8")
    write_srt(segs, srt_path)
    print("✅ 完成：")
    print("   TXT →", txt_path)
    print("   SRT →", srt_path)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("❌ 轉錄失敗：", e)
        traceback.print_exc()
        sys.exit(2)