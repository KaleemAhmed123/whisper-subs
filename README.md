# Whisper Subtitle Generator

Automatically generate `.srt` / `.vtt` subtitle files for all your video files using OpenAI's Whisper — runs **100% locally**, no internet needed after setup, completely free.

---

## Quick Start

```bash
git clone https://github.com/yourusername/whisper-subtitles.git
cd whisper-subtitles
```

1. Double-click **`setup.bat`** — installs everything automatically
2. Open **`config.env`** — set your video folder path
3. Double-click **`generate.bat`** — sit back and wait

That's it. SRT files will appear next to every video.

> **New user?** Read the full step-by-step guide → [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)

### Setting your video folder path

Open `config.env` and update this line:

```
VIDEO_FOLDER=D:/Your/Videos/Folder
```

To find the path: open **File Explorer** → navigate to your video folder → click the address bar → copy the path.

Use **forward slashes** `/` or double backslashes `\\`. Single backslash `\` will not work.

```
✅  VIDEO_FOLDER=D:/My Course Videos
✅  VIDEO_FOLDER=D:\\My Course Videos
❌  VIDEO_FOLDER=D:\My Course Videos
```

---

## What gets installed

| Tool | Purpose |
|---|---|
| Python venv | Isolated environment, won't affect your system |
| openai-whisper | Core transcription engine by OpenAI |
| faster-whisper | Faster alternative (auto-used if available) |
| PyTorch | ML runtime (CPU or CUDA depending on your GPU) |
| ffmpeg | Audio extraction from video files |

---

## Config options (`config.env`)

| Option | Values | Default |
|---|---|---|
| `VIDEO_FOLDER` | Any path | `D:/@Claude Code for Professional Developers` |
| `MODEL` | `tiny` `base` `small` `medium` `large-v3` | `medium` |
| `LANGUAGE` | `en` `es` `fr` `de` `hi` `auto` … | `en` |
| `SKIP_EXISTING` | `true` / `false` | `true` |
| `OUTPUT_FORMAT` | `srt` / `vtt` / `both` | `srt` |

---

## Model selection guide

| Model | Size | CPU speed | GPU speed | Best for |
|---|---|---|---|---|
| `tiny` | 39 MB | ~5 min/hr | ~1 min/hr | Quick drafts, fast machines |
| `base` | 74 MB | ~10 min/hr | ~2 min/hr | CPU users who want speed |
| `small` | 244 MB | ~20 min/hr | ~3 min/hr | CPU users, good quality |
| `medium` | 769 MB | ~35 min/hr | ~5 min/hr | **GPU recommended** |
| `large-v3` | 1.5 GB | ~80 min/hr | ~10 min/hr | Best accuracy, GPU only |

> **No GPU?** Use `small` — it's the best quality/speed tradeoff on CPU.

---

## GPU acceleration

The setup script **auto-detects** your GPU:

- **NVIDIA GPU** → installs PyTorch with CUDA → full GPU acceleration
- **Apple Silicon (M1/M2/M3)** → uses MPS backend → partial acceleration
- **No GPU / Intel/AMD** → CPU mode (still works, just slower)

To check if GPU was detected, look for this line when running `generate.bat`:
```
Device  : cuda      ← GPU active
Device  : cpu       ← CPU only
```

---

## Running manually (without .bat files)

```bash
# Activate the environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# Run with default config
python scripts/generate_subtitles.py --folder "D:/Videos" --model medium

# All options
python scripts/generate_subtitles.py \
  --folder "D:/Videos" \
  --model medium \
  --language en \
  --skip-existing true \
  --output-format both
```

---

## Output

Each video gets a subtitle file in the same folder:

```
📁 Your Videos Folder/
├── 01-introduction.mp4
├── 01-introduction.srt   ← generated
├── 02-setup.mp4
├── 02-setup.srt          ← generated
└── ...
```

---

## Troubleshooting

**`python` not recognized**
→ Re-run the Python installer and check "Add Python to PATH"

**`ffmpeg` not found**
→ Run `winget install --id=Gyan.FFmpeg -e` in an admin CMD, then restart CMD

**CUDA not available despite having NVIDIA GPU**
→ Check your CUDA version with `nvidia-smi`, then reinstall PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```
Replace `cu121` with your actual CUDA version (cu118, cu121, cu124…)

**Out of memory error on GPU**
→ Switch to a smaller model in `config.env`: `MODEL=small`

**Script stops midway**
→ Just re-run `generate.bat`. With `SKIP_EXISTING=true`, it resumes from where it left off.

---

## Requirements

- Windows 10 / 11
- Python 3.10+
- ffmpeg (auto-installed by setup.bat)
- ~2GB disk space for model + venv
- NVIDIA GPU optional but recommended for speed

---

## License

MIT — free to use, modify, and distribute.
