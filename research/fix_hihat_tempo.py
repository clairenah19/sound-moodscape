#!/usr/bin/env python3
"""Suppress an embedded hi-hat pattern and replace it at a deterministic BPM."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--bpm", type=float, default=95.0)
    parser.add_argument("--cutoff", type=float, default=5200.0)
    parser.add_argument("--high-retain", type=float, default=0.12)
    parser.add_argument("--hat-gain", type=float, default=0.105)
    args = parser.parse_args()

    audio, sample_rate = sf.read(args.source, dtype="float32", always_2d=True)
    nyquist = sample_rate / 2.0
    if not 0 < args.cutoff < nyquist:
        raise SystemExit("cutoff must be between 0 Hz and Nyquist")

    # A high-shelf reduction suppresses Suno's existing cymbal/hi-hat energy
    # while retaining a small amount of air so the soundscape is not muffled.
    lowpass = signal.butter(6, args.cutoff / nyquist, btype="lowpass", output="sos")
    low = signal.sosfiltfilt(lowpass, audio, axis=0).astype(np.float32)
    high = audio - low
    corrected = low + args.high_retain * high

    # One closed hat per quarter note—no eighth-note or offbeat subdivisions.
    rng = np.random.default_rng(9500)
    hat_frames = round(0.045 * sample_rate)
    times = np.arange(hat_frames, dtype=np.float32) / sample_rate
    envelope = np.exp(-times * 92.0)
    noise = rng.uniform(-1.0, 1.0, hat_frames).astype(np.float32)
    highpass = signal.butter(3, 5800.0 / nyquist, btype="highpass", output="sos")
    noise = signal.sosfilt(highpass, noise).astype(np.float32)
    metallic = (
        0.28 * np.sin(2 * np.pi * 7300.0 * times)
        + 0.18 * np.sin(2 * np.pi * 10100.0 * times)
    )
    hat = args.hat_gain * envelope * (0.72 * noise + metallic)

    seconds_per_beat = 60.0 / args.bpm
    beat = 0
    frame = 0
    total_frames = corrected.shape[0]
    while frame < total_frames:
        length = min(hat_frames, total_frames - frame)
        # A mild bar accent establishes 4/4 without creating a slower hat rate.
        accent = 1.12 if beat % 4 == 0 else 1.0
        corrected[frame:frame + length, :] += (accent * hat[:length])[:, None]
        beat += 1
        frame = round(beat * seconds_per_beat * sample_rate)

    corrected = np.clip(corrected, -1.0, 1.0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, corrected, sample_rate, subtype="PCM_16")

    record = {
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "bpm": args.bpm,
        "seconds_per_hihat": seconds_per_beat,
        "hihat_pattern": "one closed hi-hat per quarter note; no subdivisions",
        "original_high_frequency_retain": args.high_retain,
        "shelf_cutoff_hz": args.cutoff,
        "replacement_hihat_gain": args.hat_gain,
        "replacement_hihat_count": beat,
        "validation": "pending blind human listening",
    }
    log = args.output.with_suffix(".json")
    log.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
