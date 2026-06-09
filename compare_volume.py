import sys
import os
import librosa
import numpy as np
from pydub import AudioSegment


def analyze_audio_deep(file_path, label):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"🎵 Analyzing: {label}")

    # Physical analysis (pydub).
    audio = AudioSegment.from_file(file_path)
    print(f"   ↳ Average volume (RMS): {audio.dBFS:.2f} dB")
    print(f"   ↳ Channels: {audio.channels} (1=Mono, 2=Stereo)")
    print(f"   ↳ Sample rate: {audio.frame_rate} Hz")

    # Frequency / EQ analysis (librosa). Load as mono just for the math.
    y, sr = librosa.load(file_path, sr=None, mono=True)

    # Spectral centroid: the average "brightness" of the EQ.
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    mean_centroid = np.mean(centroid)
    print(f"   ↳ Spectral brightness (EQ centroid): {mean_centroid:.0f} Hz\n")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        file_game = sys.argv[1]
        file_script = sys.argv[2]

        print("=== ADVANCED AUDIO REPORT ===\n")
        analyze_audio_deep(file_game, "Imported by the GAME (official)")
        analyze_audio_deep(file_script, "Imported by OUR SCRIPT")
    else:
        print("Usage:")
        print('python compare_volume.py "C:\\...\\Game.ogg" "C:\\...\\Script.ogg"')
