#!/usr/bin/env python3
"""Pitch-preserving correction from a measured human BPM to a target BPM.

Use this only after a blind human tap test establishes the source pulse. The
entire recording is retimed, so the old pulse cannot remain as a competing
half-time layer. Duration changes by source_bpm / target_bpm; pitch does not.
"""
import argparse
import hashlib
import json
from pathlib import Path

import librosa
import soundfile as sf


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
    parser.add_argument("--source-bpm", type=float, required=True)
    parser.add_argument("--target-bpm", type=float, required=True)
    args = parser.parse_args()
    if args.source_bpm <= 0 or args.target_bpm <= 0:
        raise SystemExit("BPM values must be positive")

    audio, sample_rate = librosa.load(args.source, sr=None, mono=False)
    source_frames = audio.shape[-1]
    rate = args.target_bpm / args.source_bpm
    corrected = librosa.effects.time_stretch(audio, rate=rate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, corrected.T, sample_rate, subtype="PCM_16")

    record = {
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "human_measured_source_bpm": args.source_bpm,
        "target_bpm": args.target_bpm,
        "time_stretch_rate": rate,
        "pitch_preserved": True,
        "source_duration_seconds": round(source_frames / sample_rate, 3),
        "output_duration_seconds": round(corrected.shape[-1] / sample_rate, 3),
        "validation": "pending blind human tap-tempo test",
    }
    log_path = args.output.with_suffix(".json")
    log_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    print(f"Wrote {log_path}")


if __name__ == "__main__":
    main()
