#!/usr/bin/env python3
"""
Moodscape — generated-audio verification tool.

Compares what a Suno prompt ASKED for (BPM, major/minor key — taken from
buildSunoPrompt()'s output, already recorded per clip in
listener_stimulus_metadata.csv) against what a real generated MP3 ACTUALLY
contains (BPM and key/mode detected directly from the audio).

This is a "preparable now" tool: it does nothing useful until real Suno-
generated MP3 files exist (see DEVELOPMENT_PLAN.md / the listener-experiment
pipeline, which currently marks every clip's source_track as empty and
source_provenance as "PENDING real Suno generation"). Running this script
before that data exists is expected to report 0 analyzable clips, not error
out — that is deliberate, matching the same "handle the not-ready case
cleanly" principle used in analyze_soundwalk.js.

Setup (one-time, isolated — does not touch system Python):
    python3 -m venv audio-analysis-venv
    source audio-analysis-venv/bin/activate
    pip install -r research/requirements-audio-analysis.txt

Usage:
    python3 research/analyze_generated_audio.py \
        --metadata research/listener_stimulus_metadata.csv \
        --out research/audio_analysis_results.csv

Each row of the metadata CSV must have (already the case for
listener_stimulus_metadata.csv):
    clip_id, bpm, intended_mode, source_track, prompt
`source_track` should be a path (absolute or relative to this script's cwd)
to the real generated MP3 once one exists; leave it empty until then.
"""

import argparse
import csv
import os
import sys

import numpy as np

try:
    import librosa
except ImportError:
    sys.exit(
        "librosa is not installed. Set up the isolated environment first:\n"
        "  python3 -m venv audio-analysis-venv\n"
        "  source audio-analysis-venv/bin/activate\n"
        "  pip install -r research/requirements-audio-analysis.txt"
    )

# Krumhansl-Kessler key profiles — the standard, published algorithm for
# estimating major/minor tonality from a chroma vector. Not something
# invented for this project; these exact 24 profile values are the
# textbook Krumhansl & Kessler (1982) tone-profile numbers.
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def detect_key(y, sr):
    """Krumhansl-Schmuckler key estimation via chroma correlation.
    Returns (root_pitch_class, 'major'|'minor', correlation_confidence)."""
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    # Normalize so correlation isn't dominated by overall loudness
    if chroma_mean.std() > 0:
        chroma_mean = (chroma_mean - chroma_mean.mean()) / chroma_mean.std()

    best_corr, best_root, best_mode = -2.0, 0, "major"
    for root in range(12):
        for mode, profile in (("major", MAJOR_PROFILE), ("minor", MINOR_PROFILE)):
            rotated = np.roll(profile, root)
            rotated_norm = (rotated - rotated.mean()) / rotated.std()
            corr = float(np.dot(chroma_mean, rotated_norm) / len(chroma_mean))
            if corr > best_corr:
                best_corr, best_root, best_mode = corr, root, mode

    return PITCH_CLASSES[best_root], best_mode, best_corr


def detect_bpm(y, sr):
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # librosa can return a 0-d/1-element array depending on version
    return float(np.atleast_1d(tempo)[0])


# Metrical relations accepted as "the same tempo" — the standard set used in tempo-estimation evaluation
# (MIREX "Accuracy 2": the estimate may be 1/3, 1/2, 1, 2 or 3 times the reference). Automatic beat trackers lock onto
# a subdivision of slow, sparse, plucked or arpeggiated music, so a slow request is routinely reported at 2-3x.
# The raw deviation is still written out; this adds the octave-aware reading beside it instead of replacing it.
RELATIONS = ((1 / 3, "1/3x"), (1 / 2, "1/2x"), (1.0, "1x"), (2.0, "2x"), (3.0, "3x"))


def metrical_relation(requested, detected):
    """Return (relation label, % deviation from the nearest accepted multiple of the requested tempo)."""
    best = min(RELATIONS, key=lambda rel: abs(detected - requested * rel[0]) / (requested * rel[0]))
    target = requested * best[0]
    return best[1], abs(detected - target) / target * 100


def event_density(y, sr, requested_bpm):
    """Onsets per second, and onsets per requested beat. Separates 'the music is sparse' from 'the tracker
    counted subdivisions': a slow request that is honoured has few events per second even when the tracker says 125."""
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    rate = len(onsets) / (len(y) / sr)
    return rate, rate / (requested_bpm / 60.0)


def analyze_clip(path, requested_bpm):
    y, sr = librosa.load(path, sr=None, mono=True)
    bpm = detect_bpm(y, sr)
    root, mode, confidence = detect_key(y, sr)
    rate, per_beat = event_density(y, sr, requested_bpm)
    return bpm, f"{root} {mode}", mode, confidence, rate, per_beat


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metadata", default="research/listener_stimulus_metadata.csv")
    ap.add_argument("--out", default="research/audio_analysis_results.csv")
    args = ap.parse_args()

    with open(args.metadata, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    analyzable = [r for r in rows if r.get("source_track", "").strip() and os.path.isfile(r["source_track"].strip())]

    if not analyzable:
        print(f"0 of {len(rows)} clips have a real generated audio file yet.")
        print('Every row\'s source_track is empty ("PENDING real Suno generation") — nothing to analyze.')
        print("This is expected until real Suno tracks are generated and their paths filled in.")
        return

    print(f"Analyzing {len(analyzable)} of {len(rows)} clips with real audio files...")
    results = []
    for r in analyzable:
        clip_id = r["clip_id"]
        path = r["source_track"].strip()
        requested_bpm = float(r["bpm"])
        requested_mode = "major" if "major" in r["intended_mode"].lower() else "minor"

        try:
            detected_bpm, detected_key_label, detected_mode, confidence, onset_rate, events_per_beat = analyze_clip(path, requested_bpm)
        except Exception as e:
            print(f"  {clip_id}: FAILED to analyze ({e})")
            continue

        bpm_diff_pct = abs(detected_bpm - requested_bpm) / requested_bpm * 100
        relation, octave_diff_pct = metrical_relation(requested_bpm, detected_bpm)
        mode_match = detected_mode == requested_mode

        results.append({
            "clip_id": clip_id,
            "place": r.get("place", ""),
            "requested_bpm": requested_bpm,
            "detected_bpm": round(detected_bpm, 1),
            "bpm_diff_pct": round(bpm_diff_pct, 1),
            "metrical_relation": relation,
            "octave_aware_diff_pct": round(octave_diff_pct, 1),
            "onsets_per_s": round(onset_rate, 2),
            "events_per_requested_beat": round(events_per_beat, 2),
            "requested_mode": requested_mode,
            "detected_key": detected_key_label,
            "mode_match": mode_match,
            "key_detection_confidence": round(confidence, 3),
        })
        print(f"  {clip_id}: requested {requested_bpm} BPM / {requested_mode} "
              f"-> detected {detected_bpm:.1f} BPM ({bpm_diff_pct:.1f}% off raw; {octave_diff_pct:.1f}% off as {relation}) / {detected_key_label} "
              f"({'MATCH' if mode_match else 'MISMATCH'})")

    if results:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)

        n = len(results)
        mode_matches = sum(1 for r in results if r["mode_match"])
        avg_bpm_diff = sum(r["bpm_diff_pct"] for r in results) / n
        avg_oct_diff = sum(r["octave_aware_diff_pct"] for r in results) / n
        within5 = sum(1 for r in results if r["octave_aware_diff_pct"] <= 5)
        print(f"\nSummary: {mode_matches}/{n} clips matched requested major/minor mode "
              f"({mode_matches/n*100:.0f}%); average BPM deviation {avg_bpm_diff:.1f}% raw, "
              f"{avg_oct_diff:.1f}% octave-aware; {within5}/{n} within 5% of a 1/3, 1/2, 1, 2 or 3x multiple.")
        print(f"Full results written to {args.out}")


if __name__ == "__main__":
    main()
