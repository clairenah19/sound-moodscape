#!/usr/bin/env python3
"""Rebuild the audio-verification figure and statistics from the analyzer's CSV output, so every number in
AUDIO_VERIFICATION_REPORT_EN/KO.md can be reproduced from the repository (the earlier figures came from a scratch
script that was never committed).

Inputs  (written by analyze_generated_audio.py):
    research/audio_analysis_results_octave_aware.csv      round 1 (original generation)
    research/audio_analysis_results_v2_octave_aware.csv   round 2 (regenerated with the revised prompts)
Outputs:
    research/audio_analysis_stats.csv      metric, round1, round2
    research/chart_bpm_comparison.png      requested vs detected BPM, both rounds, with the metrical relation

The octave-aware deviation allows the detected tempo to be 1/3, 1/2, 1, 2 or 3x the request. That is a statement
about the beat tracker, not about the audio: the files are untouched, and nobody has yet listened to confirm which
pulse a person would hear.

    python3 research/build_audio_report_figures.py
"""
import csv
import statistics as st
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
ROUNDS = {"round1": ROOT / "audio_analysis_results_octave_aware.csv",
          "round2": ROOT / "audio_analysis_results_v2_octave_aware.csv"}
WITHIN = 5.0  # % tolerance for "matches a standard multiple"


def load(path):
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        for k in ("requested_bpm", "detected_bpm", "bpm_diff_pct", "octave_aware_diff_pct",
                  "onsets_per_s", "events_per_requested_beat", "key_detection_confidence"):
            r[k] = float(r[k])
        r["mode_match"] = r["mode_match"] == "True"
    return rows


def stats(rows):
    n = len(rows)
    ok = [r for r in rows if r["octave_aware_diff_pct"] <= WITHIN]
    shifted = [r for r in ok if r["metrical_relation"] != "1x"]
    unexplained = [r for r in rows if r["octave_aware_diff_pct"] > WITHIN]
    match = [r["key_detection_confidence"] for r in rows if r["mode_match"]]
    miss = [r["key_detection_confidence"] for r in rows if not r["mode_match"]]
    return {
        "n": n,
        "mode_match_n": sum(r["mode_match"] for r in rows),
        "raw_bpm_mean_pct": round(st.mean(r["bpm_diff_pct"] for r in rows), 1),
        "raw_bpm_median_pct": round(st.median(r["bpm_diff_pct"] for r in rows), 1),
        "octave_aware_mean_pct": round(st.mean(r["octave_aware_diff_pct"] for r in rows), 1),
        "octave_aware_median_pct": round(st.median(r["octave_aware_diff_pct"] for r in rows), 1),
        "within_5pct_of_a_standard_multiple": len(ok),
        "of_which_at_1x": len(ok) - len(shifted),
        "of_which_at_2x_3x_half_or_third": len(shifted),
        "not_explained_by_any_standard_multiple": len(unexplained),
        "unexplained_clips": " ".join(r["clip_id"] for r in unexplained),
        "key_confidence_mean_on_match": round(st.mean(match), 3) if match else "",
        "key_confidence_mean_on_mismatch": round(st.mean(miss), 3) if miss else "",
        "mean_onsets_per_s_requested_le_81": round(st.mean(r["onsets_per_s"] for r in rows if r["requested_bpm"] <= 81), 2),
        "mean_onsets_per_s_requested_ge_107": round(st.mean(r["onsets_per_s"] for r in rows if r["requested_bpm"] >= 107), 2),
    }


def main():
    data = {k: load(p) for k, p in ROUNDS.items()}
    s = {k: stats(v) for k, v in data.items()}
    with (ROOT / "audio_analysis_stats.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "round1", "round2"])
        for m in s["round1"]:
            w.writerow([m, s["round1"][m], s["round2"][m]])
    for k in s:
        print(k, s[k])

    r1, r2 = data["round1"], data["round2"]
    ids = [r["clip_id"] for r in r1]
    x = np.arange(len(ids)); w = 0.27
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.bar(x - w, [r["requested_bpm"] for r in r1], w, label="Requested BPM (prompt)", color="#6c8fff")
    ax.bar(x, [r["detected_bpm"] for r in r1], w, label="Detected, round 1", color="#f59e0b")
    ax.bar(x + w, [r["detected_bpm"] for r in r2], w, label="Detected, round 2 (revised prompts)", color="#fcd34d")
    for i in range(len(ids)):
        for dx, r in ((0, r1[i]), (w, r2[i])):
            label = r["metrical_relation"] if r["octave_aware_diff_pct"] <= WITHIN else "no fit"
            ax.text(i + dx, r["detected_bpm"] + 2.5, label.replace("x", "×"), ha="center", fontsize=6.5,
                    color="#9096b4" if label != "no fit" else "#f0796a")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['clip_id']}\n{r['place'][:14]}" for r in r1], fontsize=7.5)
    ax.set_ylabel("BPM")
    ax.set_title("Requested vs. detected tempo, with the metrical relation each detection is closest to (within 5%)")
    ax.legend(fontsize=8, loc="upper left")
    fig.text(0.01, 0.005, "Labels describe the beat tracker's output only. The audio files are unchanged and no listener has confirmed "
             "which pulse is heard. 'no fit' = not within 5% of 1/3, 1/2, 1, 2 or 3x the request.", fontsize=6.5, color="#9096b4")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(ROOT / "chart_bpm_comparison.png", dpi=150)
    print("wrote chart_bpm_comparison.png and audio_analysis_stats.csv")


if __name__ == "__main__":
    main()
