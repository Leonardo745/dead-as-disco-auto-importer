# Dead as Disco — Auto Import

Automatically import custom songs into **Dead as Disco**, with BPM and beat
offset detected for you.

The game ships with a manual importer where you have to calibrate the **BPM**
and the **beat offset** of every song by hand — which is hard to get right.
This script does the boring part: it converts the audio to the format the game
expects, normalizes the volume, detects the BPM and the first beat, and writes
the song straight into the game's imported songs folder.

## How it works

For each audio file you pass in, the script:

1. Reads the artist and song name from the file name (`Artist - Song Name.mp3`).
2. Converts the audio to **OGG, stereo, 48 kHz** and normalizes it to **-19.5 dBFS**.
3. Detects the **BPM** and the **beat offset** using [librosa](https://librosa.org/) DSP analysis.
4. Writes `Audio.ogg` and a `meta.json` (with deterministic IDs) into:
   `%LOCALAPPDATA%\Pagoda\Saved\ImportedSongs\Artist - Song Name\`

Open the game afterwards and the track will be there, ready to play.

## Requirements

- Windows (the script writes to `%LOCALAPPDATA%`)
- Python 3.8 or newer
- [FFmpeg](https://ffmpeg.org/) available on your `PATH` (required by pydub)
- Python packages:

  ```bash
  pip install librosa numpy pydub
  ```

## Usage

Name your files as `Artist - Song Name.ext` and run:

```bash
python import_disco.py "C:\path\Daft Punk - One More Time.mp3"
```

You can import several songs at once:

```bash
python import_disco.py "C:\songs\A - First.mp3" "C:\songs\B - Second.wav"
```

If the file name has no `" - "` separator, the artist is set to `Unknown`.

## compare_volume.py (optional)

A small helper to compare two audio files side by side — handy for checking how
a track imported by the script lines up against one imported by the game:

```bash
python compare_volume.py "C:\...\Game.ogg" "C:\...\Script.ogg"
```

It prints average volume (RMS), channels, sample rate and spectral brightness.

## Notes

- BPM detection includes octave correction (it doubles or halves values that
  fall outside a sane range for a rhythm game).
- The beat offset is wrapped to fit within a single beat, because the game's UI
  truncates large offsets.
- Detection is automatic and works well for most tracks, but you can always
  fine-tune the values in `meta.json` afterwards if a song feels off.

## License

[MIT](LICENSE)
