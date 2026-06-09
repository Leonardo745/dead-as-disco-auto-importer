# Dead as Disco — Auto Importer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

Import custom songs into **Dead as Disco** automatically — no manual BPM or beat
offset calibration needed.

---

## The Problem

Dead as Disco ships with a manual importer where you have to calibrate the
**BPM** and the **beat offset** of every song by hand. Getting this right is
hard: a wrong value makes the whole track feel off.

## The Solution

This script does the tedious part for you. For each audio file you give it:

- Converts the audio to **OGG, stereo, 48 kHz** (the format the engine expects)
- Normalizes the volume to **−19.5 dBFS** (the game's target level)
- Detects the **BPM** automatically using DSP analysis
- Detects the **beat offset** (time of the first real beat)
- Writes everything into the game's imported songs folder — ready to play

---

## Requirements

- **Windows** (the script writes to `%LOCALAPPDATA%`)
- **Python 3.8+**
- **FFmpeg** available on your `PATH` — [download here](https://ffmpeg.org/download.html)

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/Leonardo745/dead-as-disco-auto-import.git
cd dead-as-disco-auto-import
```

**2. (Optional) Create a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. Install Python dependencies**

```bash
pip install -r requirements.txt
```

---

## Usage

Name your audio files as `Artist - Song Name.ext` and run:

```bash
python import_disco.py "C:\path\to\Artist - Song Name.mp3"
```

You can import several songs in one go:

```bash
python import_disco.py "C:\songs\Daft Punk - One More Time.mp3" "C:\songs\Justice - D.A.N.C.E..wav"
```

> If the file name has no `" - "` separator, the artist is set to `Unknown`.

After running the script, open Dead as Disco — the tracks will be in the
imported songs list, ready to play.

---

## How It Works

| Step | What happens |
|------|-------------|
| **Parse** | Reads artist and song name from the file name |
| **Convert** | Exports audio as OGG stereo 48 kHz |
| **Normalize** | Adjusts volume to −19.5 dBFS |
| **BPM detection** | Computes median beat interval, ignoring outliers; applies octave correction to keep values in a sane range for a rhythm game |
| **Offset detection** | Finds the first strong onset using a dynamic threshold (50% of the track's mean onset strength), then wraps the value to fit within a single beat |
| **Write** | Generates `Audio.ogg` and `meta.json` with deterministic IDs under `%LOCALAPPDATA%\Pagoda\Saved\ImportedSongs\` |

---

## Notes

- Detection is fully automatic and works well for most tracks. If a song still
  feels slightly off, you can open `meta.json` and tweak `tempo` or
  `beatOffset` manually.
- BPM values outside the 110–220 range are automatically doubled or halved, a
  common correction needed for rhythm games.
- The beat offset is always wrapped to fit within a single beat to avoid a
  known truncation bug in the game's UI.

---

## License

[MIT](LICENSE)
