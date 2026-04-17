# Getting Started Guide

Welcome! This guide walks you through everything from cloning the repo to getting your first subtitle file — no technical experience needed.

---

## Step 1 — Clone or Download the Repo

**Option A — Git (recommended)**
```bash
git clone https://github.com/yourusername/whisper-subtitles.git
cd whisper-subtitles
```

**Option B — Download ZIP**
1. Click the green **Code** button on GitHub
2. Click **Download ZIP**
3. Extract the zip anywhere on your computer (e.g. `C:\Tools\whisper-subtitles`)

---

## Step 2 — Run Setup (one time only)

Open the `whisper-subtitles` folder and **double-click `setup.bat`**.

A black terminal window will open and run through these steps automatically:

```
[1/6] Checking Python...         OK  Python 3.11.x found
[2/6] Checking ffmpeg...         OK  ffmpeg found
[3/6] Creating virtual env...    OK  venv created
[4/6] Upgrading pip...           OK  pip upgraded
[5/6] Installing dependencies... OK  All dependencies installed
[6/6] Creating config file...    OK  config.env created
```

> If Python is missing, it will tell you — download it from https://python.org and re-run setup.bat.

---

## Step 3 — Tell the Tool Where Your Videos Are

Open the file called **`config.env`** in any text editor (Notepad is fine).

You will see this at the top:

```
VIDEO_FOLDER=D:/@Claude Code for Professional Developers
```

**Change this to your actual video folder path.** Examples:

| Your situation | What to type |
|---|---|
| Videos on D: drive | `VIDEO_FOLDER=D:/My Course Videos` |
| Videos on Desktop | `VIDEO_FOLDER=C:/Users/YourName/Desktop/Videos` |
| Videos on E: drive | `VIDEO_FOLDER=E:/Courses/Python Tutorials` |

### How to find your folder path

1. Open **File Explorer** and navigate to your video folder
2. Click the **address bar** at the top — it shows the full path
3. Copy and paste it into `config.env`

![Address bar example](docs/addressbar.png)

> Use **forward slashes** `/` or **double backslashes** `\\` in the path.
> Single backslash `\` will NOT work.
>
> ✅ `D:/My Videos`
> ✅ `D:\\My Videos`
> ❌ `D:\My Videos`

---

## Step 4 — (Optional) Choose Your Model

Still in `config.env`, you can change the `MODEL` setting:

```
MODEL=medium
```

| Model | Speed on CPU | Quality | Recommended for |
|---|---|---|---|
| `tiny` | Very fast | Lower | Quick drafts |
| `base` | Fast | OK | CPU, clear audio |
| `small` | Medium | Good | **CPU users** ← use this |
| `medium` | Slow | Great | **GPU users** ← use this |
| `large-v3` | Very slow | Best | GPU, multiple languages |

**Don't have a GPU?** Change to `MODEL=small` — much faster on CPU with still good results.

Not sure if you have a GPU? Leave it as `medium` — the tool will detect it automatically and tell you at startup.

---

## Step 5 — Run the Generator

Double-click **`generate.bat`**.

You will see progress for each video:

```
  ╔══════════════════════════════════════════════════╗
  ║    Whisper Subtitle Generator  —  Generate      ║
  ╚══════════════════════════════════════════════════╝

  Folder  : D:/My Course Videos
  Model   : medium
  Device  : cuda        ← GPU active (fast!)
  Language: en

  Found 97 video(s)

  ✓ Model ready

  [  1/97] ...   01-introduction.mp4
  [  1/97] ✓ OK  01-introduction.mp4  (1m 23s)
  [  2/97] ...   02-setup.mp4
  [  2/97] ✓ OK  02-setup.mp4  (2m 10s)
  ...
```

When finished:
```
  ────────────────────────────────────────────────
  ✓ Generated  :  97 subtitle file(s)
  ⏱ Total time  :  2h 14m
  ────────────────────────────────────────────────
```

---

## What gets created

After running, every video will have a matching `.srt` file right next to it:

```
📁 D:/My Course Videos/
├── 🎬 01-introduction.mp4
├── 📄 01-introduction.srt    ← new!
├── 🎬 02-setup.mp4
├── 📄 02-setup.srt           ← new!
├── 🎬 03-variables.mp4
├── 📄 03-variables.srt       ← new!
└── ...
```

---

## How to use the subtitle files

**VLC Media Player**
- Open your video in VLC
- Subtitles usually load automatically if the `.srt` file has the same name as the video
- If not: go to **Subtitle → Add Subtitle File** and select the `.srt`

**MPC-HC / MPC-BE**
- Subtitles load automatically — no extra steps needed

**Plex / Jellyfin / Emby**
- Place the `.srt` file in the same folder as the video
- It will appear as a subtitle track automatically

**YouTube / Web upload**
- Change `OUTPUT_FORMAT=vtt` in `config.env`
- Upload the `.vtt` file as a subtitle track

---

## Interrupted? No problem.

If the script stops halfway (power cut, you closed it, etc.) — just double-click `generate.bat` again.

With `SKIP_EXISTING=true` (the default), it will **skip all videos that already have subtitles** and continue from where it left off.

---

## Common questions

**Q: How long will it take?**

Depends on your hardware and model choice:

| Setup | Time per 1 hour of video |
|---|---|
| GPU + medium model | ~5 minutes |
| GPU + large-v3 | ~10 minutes |
| CPU + small model | ~20 minutes |
| CPU + medium model | ~35 minutes |

For 100 videos averaging 10 minutes each (~17 hrs of footage):
- GPU: ~2–3 hours
- CPU (small): ~6 hours (run overnight)

**Q: The subtitles have some mistakes — how do I fix them?**

Open the `.srt` file in any text editor (Notepad, VS Code) — it's plain text and easy to edit. Or use [Subtitle Edit](https://www.nikse.dk/subtitleedit) — a free GUI tool for editing subtitles.

**Q: My videos are in subfolders — will it find them?**

Yes! The tool scans recursively. Point `VIDEO_FOLDER` to the top-level folder and it will find all videos inside any subfolders.

**Q: Can I add more videos later?**

Yes — add new videos to the folder and run `generate.bat` again. With `SKIP_EXISTING=true`, it only processes the new ones.

**Q: What video formats are supported?**

`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.webm`, `.flv`, `.m4v`

---

## Folder path examples (copy-paste ready)

| Location | config.env entry |
|---|---|
| Desktop folder | `VIDEO_FOLDER=C:/Users/YourName/Desktop/Videos` |
| D: drive root | `VIDEO_FOLDER=D:/Videos` |
| External drive E: | `VIDEO_FOLDER=E:/Course Recordings` |
| Downloads folder | `VIDEO_FOLDER=C:/Users/YourName/Downloads/Lectures` |

> Replace `YourName` with your actual Windows username.

---

## Still stuck?

Open an issue on GitHub with:
1. A screenshot of the error message
2. Your Windows version
3. Output of `python --version` in CMD
