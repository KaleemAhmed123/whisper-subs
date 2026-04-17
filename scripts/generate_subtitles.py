"""
Whisper Subtitle Generator
Core generation script — called by generate.bat with args from config.env.
Can also be run directly:
    python scripts/generate_subtitles.py --folder "D:/Videos" --model medium
"""

import os
import glob
import time
import argparse
import sys
import warnings

# ── Silence HuggingFace warnings ──────────────────────────────────────────────
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_VERBOSITY"] = "error"   # suppress unauthenticated token warning
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub.*")

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    from faster_whisper import WhisperModel
    WHISPER_BACKEND = "faster-whisper"
except ImportError:
    try:
        import whisper
        WHISPER_BACKEND = "openai-whisper"
    except ImportError:
        print("\n[ERROR] No Whisper backend found.")
        print("Run setup.bat first, or manually: pip install openai-whisper\n")
        sys.exit(1)

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    HAVE_TRANSLITERATE = True
except ImportError:
    HAVE_TRANSLITERATE = False

# ── Terminal colors ───────────────────────────────────────────────────────────
class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

def col(text, color): return f"{color}{text}{C.RESET}"

# ── Helpers ───────────────────────────────────────────────────────────────────
VIDEO_EXTENSIONS = ("*.mp4", "*.mkv", "*.avi", "*.mov", "*.wmv", "*.webm", "*.flv", "*.m4v")

def format_ts_srt(seconds):
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def format_ts_vtt(seconds):
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

def segments_to_srt(segments, to_hinglish=False):
    lines = []
    for i, seg in enumerate(segments, 1):
        text = seg['text'].strip()
        if to_hinglish and HAVE_TRANSLITERATE:
            text = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        lines.append(
            f"{i}\n"
            f"{format_ts_srt(seg['start'])} --> {format_ts_srt(seg['end'])}\n"
            f"{text}\n"
        )
    return "\n".join(lines)

def segments_to_vtt(segments, to_hinglish=False):
    lines = ["WEBVTT\n"]
    for i, seg in enumerate(segments, 1):
        text = seg['text'].strip()
        if to_hinglish and HAVE_TRANSLITERATE:
            text = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        lines.append(
            f"{i}\n"
            f"{format_ts_vtt(seg['start'])} --> {format_ts_vtt(seg['end'])}\n"
            f"{text}\n"
        )
    return "\n".join(lines)

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    return f"{int(seconds // 60)}m {int(seconds % 60)}s"

def str_to_bool(val):
    return str(val).strip().lower() in ("true", "1", "yes")

# ── Transcription wrappers ────────────────────────────────────────────────────
def transcribe_openai(model, video_path, language, use_fp16=True):
    lang = None if language.lower() == "auto" else language
    result = model.transcribe(video_path, language=lang, task="transcribe", verbose=False, fp16=use_fp16)
    return result["segments"]

def transcribe_faster(model, video_path, language):
    lang = None if language.lower() == "auto" else language
    segments, info = model.transcribe(video_path, language=lang, task="transcribe")
    
    results = []
    duration = info.duration
    
    # We are on the line below the prefix. Let's write a progress percentage
    for s in segments:
        results.append({"start": s.start, "end": s.end, "text": s.text})
        percent = min(100.0, (s.end / duration) * 100.0) if duration > 0 else 0
        sys.stdout.write(f"\r        \033[96m↳\033[0m Progress: {percent:4.1f}%  ({s.end:.1f}s / {duration:.1f}s)    ")
        sys.stdout.flush()
        
    # Clear the progress line
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()
    return results

# ── Banner ────────────────────────────────────────────────────────────────────
def print_banner(args, backend, device):
    print()
    print(col("  ╔══════════════════════════════════════════════════╗", C.CYAN))
    print(col("  ║     Whisper Subtitle Generator  v1.0            ║", C.CYAN))
    print(col("  ╚══════════════════════════════════════════════════╝", C.CYAN))
    print()
    print(f"  {col('Folder  :', C.BOLD)} {args.folder}")
    print(f"  {col('Model   :', C.BOLD)} {args.model}  {col(f'[{backend}]', C.DIM)}")
    print(f"  {col('Device  :', C.BOLD)} {col(device, C.GREEN if device != 'cpu' else C.YELLOW)}")
    print(f"  {col('Language:', C.BOLD)} {args.language}")
    print(f"  {col('Format  :', C.BOLD)} {args.output_format}")
    if str_to_bool(args.hinglish):
        print(f"  {col('Hinglish:', C.BOLD)} {col('Enabled', C.GREEN)}")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Batch subtitle generator using Whisper")
    parser.add_argument("--folder",        default=".",        help="Path to video folder")
    parser.add_argument("--model",         default="medium",   help="Whisper model size")
    parser.add_argument("--language",      default="en",       help="Language code or 'auto'")
    parser.add_argument("--skip-existing", default="true",     help="Skip if .srt already exists")
    parser.add_argument("--output-format", default="srt",      help="srt | vtt | both")
    parser.add_argument("--hinglish",      default="false",    help="Convert Devanagari to Roman (Hinglish)")
    args = parser.parse_args()

    skip_existing = str_to_bool(args.skip_existing)
    output_format = args.output_format.strip().lower()
    to_hinglish   = str_to_bool(args.hinglish)

    # ── Detect device & load model ────────────────────────────────────────────
    device = "cpu"
    use_fp16 = False
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            if "1650" in gpu_name or "1660" in gpu_name:
                use_fp16 = False
            else:
                use_fp16 = True
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"  # Apple Silicon
    except ImportError:
        pass

    print_banner(args, WHISPER_BACKEND, device)

    # ── Validate folder ───────────────────────────────────────────────────────
    if not os.path.isdir(args.folder):
        print(col(f"  [ERROR] Folder not found: {args.folder}", C.RED))
        print(col("  Edit VIDEO_FOLDER in config.env and try again.\n", C.YELLOW))
        sys.exit(1)

    # ── Gather videos ─────────────────────────────────────────────────────────
    videos = []
    for ext in VIDEO_EXTENSIONS:
        videos.extend(glob.glob(os.path.join(args.folder, "**", ext), recursive=True))
    videos.sort()

    if not videos:
        print(col(f"  [ERROR] No video files found in: {args.folder}\n", C.RED))
        sys.exit(1)

    print(col(f"  Found {len(videos)} video(s)\n", C.GREEN))

    # ── Load Whisper model ────────────────────────────────────────────────────
    print(col(f"  Loading model '{args.model}'...", C.CYAN))
    print(col("  (First run downloads the model — one-time only)\n", C.DIM))

    if WHISPER_BACKEND == "openai-whisper":
        model = whisper.load_model(args.model, device=device)
        transcribe_fn = lambda path: transcribe_openai(model, path, args.language, use_fp16)
    else:
        if device == "cuda":
            compute_type = "float16" if use_fp16 else "int8"
        else:
            compute_type = "int8"
        model = WhisperModel(args.model, device=device, compute_type=compute_type)
        transcribe_fn = lambda path: transcribe_faster(model, path, args.language)

    print(col(f"  ✓ Model ready\n", C.GREEN))

    # ── Batch process ─────────────────────────────────────────────────────────
    total_start   = time.time()
    success_count = 0
    skip_count    = 0
    error_count   = 0
    errors        = []

    for idx, video_path in enumerate(videos, 1):
        filename  = os.path.basename(video_path)
        base_path = os.path.splitext(video_path)[0]
        srt_path  = base_path + ".srt"
        vtt_path  = base_path + ".vtt"
        prefix    = f"[{idx:>3}/{len(videos)}]"

        # Check skip
        already_done = (
            (output_format in ("srt", "both") and os.path.exists(srt_path)) or
            (output_format in ("vtt", "both") and os.path.exists(vtt_path))
        )
        if skip_existing and already_done:
            print(f"  {col(prefix, C.YELLOW)} {col('SKIP', C.YELLOW)}  {col(filename, C.DIM)}")
            skip_count += 1
            continue

        print(f"  {col(prefix, C.CYAN)} {col('...', C.DIM)}   {filename}")
        step_start = time.time()

        try:
            segments = transcribe_fn(video_path)

            if output_format in ("srt", "both"):
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(segments_to_srt(segments, to_hinglish=to_hinglish))

            if output_format in ("vtt", "both"):
                with open(vtt_path, "w", encoding="utf-8") as f:
                    f.write(segments_to_vtt(segments, to_hinglish=to_hinglish))

            elapsed = time.time() - step_start
            print(f"  {col(prefix, C.CYAN)} {col('✓ OK', C.GREEN)}   {filename}  {col(f'({format_duration(elapsed)})', C.YELLOW)}")
            success_count += 1

        except Exception as e:
            elapsed = time.time() - step_start
            print(f"  {col(prefix, C.CYAN)} {col('✗ ERR', C.RED)}  {filename}")
            print(f"           {col(str(e), C.RED)}")
            error_count += 1
            errors.append((filename, str(e)))

    # ── Summary ───────────────────────────────────────────────────────────────
    total_elapsed = time.time() - total_start
    print()
    print(col("  " + "─" * 48, C.CYAN))
    print(f"  {col('✓ Generated  :', C.GREEN)}  {success_count} subtitle file(s)")
    if skip_count:
        print(f"  {col('⊘ Skipped    :', C.YELLOW)}  {skip_count} (already existed)")
    if error_count:
        print(f"  {col('✗ Errors     :', C.RED)}  {error_count}")
        for name, err in errors:
            print(f"    {col(name, C.RED)}: {err}")
    print(f"  {col('⏱ Total time  :', C.CYAN)}  {format_duration(total_elapsed)}")
    print(col("  " + "─" * 48, C.CYAN))
    print()


if __name__ == "__main__":
    main()
