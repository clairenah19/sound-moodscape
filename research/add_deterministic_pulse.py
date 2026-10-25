#!/usr/bin/env python3
"""Add a reproducible, pitch-preserving quarter-note pulse to a PCM WAV file.

The source audio is not time-stretched. A synthesized kick is placed exactly on
each requested quarter note, with a quiet rim accent on beats 2 and 4. This makes
tempo control deterministic while retaining Suno's atmosphere and harmony.
"""
import argparse
import hashlib
import json
import math
import random
import wave
from array import array
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clamp16(value):
    return max(-32768, min(32767, int(round(value))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--bpm", type=float, default=95.0)
    parser.add_argument("--source-gain", type=float, default=0.82)
    parser.add_argument("--kick-gain", type=float, default=0.30)
    parser.add_argument("--rim-gain", type=float, default=0.10)
    parser.add_argument("--start-seconds", type=float, default=0.0)
    args = parser.parse_args()

    with wave.open(str(args.source), "rb") as reader:
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        sample_rate = reader.getframerate()
        frame_count = reader.getnframes()
        pcm = reader.readframes(frame_count)

    if sample_width != 2 or channels not in (1, 2):
        raise SystemExit("Source must be 16-bit mono or stereo PCM WAV")
    samples = array("h")
    samples.frombytes(pcm)

    # Leave conservative headroom before adding the pulse.
    for index in range(len(samples)):
        samples[index] = clamp16(samples[index] * args.source_gain)

    seconds_per_beat = 60.0 / args.bpm
    first_frame = max(0, round(args.start_seconds * sample_rate))
    total_frames = len(samples) // channels
    kick_length = round(0.14 * sample_rate)
    rim_length = round(0.045 * sample_rate)
    duck_length = round(0.075 * sample_rate)
    beat_number = 0
    beat_frame = first_frame
    rng = random.Random(9500)

    while beat_frame < total_frames:
        # Brief transparent ducking exposes the pulse without changing duration.
        for offset in range(min(duck_length, total_frames - beat_frame)):
            recovery = offset / max(1, duck_length - 1)
            factor = 0.76 + 0.24 * recovery
            base = (beat_frame + offset) * channels
            for channel in range(channels):
                samples[base + channel] = clamp16(samples[base + channel] * factor)

        # Short, soft synthesized kick. Beat 1 receives a small metrical accent.
        phase = 0.0
        accent = 1.18 if beat_number % 4 == 0 else 1.0
        for offset in range(min(kick_length, total_frames - beat_frame)):
            time_s = offset / sample_rate
            frequency = 48.0 + 52.0 * math.exp(-time_s * 28.0)
            phase += 2.0 * math.pi * frequency / sample_rate
            envelope = math.exp(-time_s * 30.0)
            click = math.exp(-time_s * 115.0) * math.sin(2.0 * math.pi * 720.0 * time_s)
            value = 32767.0 * args.kick_gain * accent * envelope * (0.86 * math.sin(phase) + 0.14 * click)
            base = (beat_frame + offset) * channels
            for channel in range(channels):
                samples[base + channel] = clamp16(samples[base + channel] + value)

        # Rim accents on beats 2 and 4 clarify 4/4 without creating an eighth-note grid.
        if beat_number % 4 in (1, 3):
            for offset in range(min(rim_length, total_frames - beat_frame)):
                time_s = offset / sample_rate
                envelope = math.exp(-time_s * 85.0)
                noise = rng.uniform(-1.0, 1.0)
                tone = math.sin(2.0 * math.pi * 1650.0 * time_s)
                value = 32767.0 * args.rim_gain * envelope * (0.68 * noise + 0.32 * tone)
                base = (beat_frame + offset) * channels
                for channel in range(channels):
                    samples[base + channel] = clamp16(samples[base + channel] + value)

        beat_number += 1
        beat_frame = first_frame + round(beat_number * seconds_per_beat * sample_rate)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(args.output), "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(sample_width)
        writer.setframerate(sample_rate)
        writer.writeframes(samples.tobytes())

    record = {
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_seconds": round(total_frames / sample_rate, 3),
        "bpm": args.bpm,
        "seconds_per_beat": seconds_per_beat,
        "source_gain": args.source_gain,
        "kick_gain": args.kick_gain,
        "rim_gain": args.rim_gain,
        "beat_count": beat_number,
        "pitch_or_duration_changed": False,
        "validation": "pending blind human tap-tempo test",
    }
    log_path = args.output.with_suffix(".json")
    log_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    print(f"Wrote {log_path}")


if __name__ == "__main__":
    main()
