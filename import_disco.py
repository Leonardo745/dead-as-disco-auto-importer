import os
import sys
import json
import hashlib
import librosa
import numpy as np
from pydub import AudioSegment


def get_file_md5(file_path):
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def process_and_import(file_path):
    if not os.path.exists(file_path):
        print("❌ File not found!")
        return

    # Identify artist and song from the file name ("Artist - Song Name").
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    if " - " in base_name:
        artist, song_name = base_name.split(" - ", 1)
    else:
        artist = "Unknown"
        song_name = base_name

    folder_name = f"{artist} - {song_name}"

    # Target folder structure inside the game's imported songs directory.
    local_app_data = os.getenv('LOCALAPPDATA')
    target_dir = os.path.join(local_app_data, "Pagoda", "Saved", "ImportedSongs", folder_name)
    os.makedirs(target_dir, exist_ok=True)

    target_audio_path = os.path.join(target_dir, "Audio.ogg")
    target_meta_path = os.path.join(target_dir, "meta.json")

    print(f"🎵 Processing: {folder_name}...")

    # Convert to OGG and match the format the engine expects.
    print("   ↳ Converting, normalizing and formatting audio...")
    audio = AudioSegment.from_file(file_path)

    audio = audio.set_channels(2)        # Force stereo
    audio = audio.set_frame_rate(48000)  # Force 48000 Hz

    # Normalize volume to the game target (-19.5 dBFS).
    target_dBFS = -19.5
    volume_change = target_dBFS - audio.dBFS

    if volume_change < -0.5:
        audio = audio + volume_change
        print(f"      [Audio normalized: volume reduced by {abs(volume_change):.2f} dB]")
    elif volume_change > 0.5:
        audio = audio + volume_change
        print(f"      [Audio normalized: volume increased by {volume_change:.2f} dB]")
    else:
        print("      [Audio already at the ideal volume]")

    audio.export(target_audio_path, format="ogg")

    # Universal DSP analysis for BPM and offset.
    print("   ↳ Analyzing BPM and offset...")

    hop_length = 256
    y, sr = librosa.load(file_path, sr=None)

    # Onset strength envelope across the whole track.
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

    # --- Offset: time of the first real beat ---
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=hop_length, backtrack=True)

    if len(onsets) > 0:
        # Use the mean onset strength as a dynamic threshold, so detection is
        # not hard-coded to a specific genre or mix. A beat must reach at least
        # 50% of the average strength to count.
        global_mean_strength = np.mean(onset_env)
        dynamic_threshold = global_mean_strength * 0.5

        valid_onsets = [o for o in onsets if onset_env[o] > dynamic_threshold]

        if len(valid_onsets) > 0:
            first_beat_time = librosa.frames_to_time(valid_onsets[0], sr=sr, hop_length=hop_length)
            beat_offset_ms = int(np.round(first_beat_time * 1000))
        else:
            # Safe fallback for unusual tracks with no dominant beat.
            first_beat_time = librosa.frames_to_time(onsets[0], sr=sr, hop_length=hop_length)
            beat_offset_ms = int(np.round(first_beat_time * 1000))
    else:
        beat_offset_ms = 0

    # --- BPM: robust interval math, ignoring outliers ---
    _, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length, start_bpm=140.0)

    if len(beats) > 1:
        beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=hop_length)
        intervals = np.diff(beat_times)
        median_interval = np.median(intervals)

        valid_intervals = intervals[(intervals > 0.8 * median_interval) & (intervals < 1.2 * median_interval)]

        if len(valid_intervals) > 0:
            exact_bpm = 60.0 / np.mean(valid_intervals)
        else:
            exact_bpm = 60.0 / median_interval

        bpm_final = int(np.round(exact_bpm))
    else:
        bpm_final = 120

    # Octave correction for rhythm games.
    if bpm_final < 110:
        bpm_final *= 2
    elif bpm_final > 220:
        bpm_final = int(np.round(bpm_final / 2))

    # The game UI truncates large offsets, which desyncs other BPMs. Wrap the
    # offset so it always fits within a single beat.
    if bpm_final > 0:
        ms_per_beat = int(np.round(60000.0 / bpm_final))
        beat_offset_ms = beat_offset_ms % ms_per_beat

    print(f"   📊 [DEBUG] Detected BPM: {bpm_final} | Normalized offset: {beat_offset_ms}ms")

    # Deterministic IDs derived from the file hash.
    print("   ↳ Building meta.json with deterministic IDs...")
    file_hash = get_file_md5(file_path)

    unique_id = int(file_hash[0:8], 16)
    seed = int(file_hash[8:16], 16)

    meta_data = {
        "version": 1,
        "uniqueId": unique_id,
        "songName": song_name,
        "performedBy": [artist],
        "writtenBy": [],
        "seed": seed,
        "tempo": bpm_final,
        "customTempoSections": [],
        "beatOffset": beat_offset_ms,
        "startSongOffset": 0,
        "endSongOffset": 0,
        "uEAssetName": folder_name,
        "originalAudioFileHash": file_hash,
        "originalAudioFilePath": file_path.replace("\\", "/")
    }

    with open(target_meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, indent=4, ensure_ascii=False)

    print("✅ Success! Track imported. Open the game to test.\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for input_file in sys.argv[1:]:
            process_and_import(input_file)
    else:
        print("Usage: python import_disco.py \"C:\\path\\song1.mp3\" \"C:\\path\\song2.wav\"")
