#!/usr/bin/env python3
"""Turn soundwalk field observations into ISO 12913 site-time results.

Reads research/soundwalk_observation_template.csv (one row per participant per
site-time), computes ISO Pleasantness and Eventfulness per the protocol's
projection formula, aggregates to site-time means with 95% confidence
intervals, and prints a table plus the predictor-vs-Eventfulness scatter rows.

This is the CSV-reading path that research/iso_pe_calculator.js lacked: that
file has the same math but only a hand-written runExample(), so it could never
touch real field data. The math here is a direct port and is checked against
the calculator's documented example by research/test_research.py.

Written in Python rather than the Node script DEVELOPMENT_PLAN.md called for
because every analysis script in research/ is already Python, and Node is not
installed on the machine this was developed on — an unrunnable script is worse
than a runnable one in the project's established language. iso_pe_calculator.js
stays as-is for browser use.

Usage:
    python3 research/analyze_soundwalk.py
    python3 research/analyze_soundwalk.py --csv path/to/other.csv
    python3 research/analyze_soundwalk.py --predictor pedestrians_per_minute

No third-party dependencies.
"""

import argparse
import csv
import math
import os
import sys
from collections import OrderedDict

COS45 = math.sqrt(0.5)          # cos(45°)
NORM = 4 + math.sqrt(32)        # the protocol's fixed denominator

ATTRIBUTES = ["pleasant", "chaotic", "vibrant", "uneventful",
              "calm", "annoying", "eventful", "monotonous"]

DEFAULT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "soundwalk_observation_template.csv")


def iso_coordinates(r):
    """ISO Pleasantness/Eventfulness for one participant's eight 1-5 ratings."""
    for key in ATTRIBUTES:
        v = r.get(key)
        if not isinstance(v, (int, float)) or not (1 <= v <= 5):
            raise ValueError(f'"{key}" must be a 1-5 rating, got {v!r}')
    pleasantness = ((r["pleasant"] - r["annoying"])
                    + COS45 * (r["calm"] - r["chaotic"])
                    + COS45 * (r["vibrant"] - r["monotonous"])) / NORM
    eventfulness = ((r["eventful"] - r["uneventful"])
                    + COS45 * (r["chaotic"] - r["calm"])
                    + COS45 * (r["vibrant"] - r["monotonous"])) / NORM
    return pleasantness, eventfulness


def summarize(values):
    """Mean and 95% CI. Uses a t-interval: pilot cells are small (~5-10), where
    the normal approximation is too narrow. Falls back to no interval at n=1."""
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return {"n": n, "mean": mean, "lo": float("nan"), "hi": float("nan")}
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    se = math.sqrt(var / n)
    margin = t_critical_95(n - 1) * se
    return {"n": n, "mean": mean, "lo": mean - margin, "hi": mean + margin}


# Two-tailed t at 95% for small df; beyond df=30 the normal value is close enough.
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
        8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160,
        14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
        26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}


def t_critical_95(df):
    return _T95.get(df, 1.96)


def _num(value):
    """Parse a numeric cell; blank/absent means genuinely missing, never zero."""
    if value is None:
        return None
    s = value.strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return [], []
        return list(reader), reader.fieldnames


def group_site_times(rows):
    """Group participant rows into site-time observations, per the protocol's
    rule that the unit of analysis is the site-time, not the province."""
    groups = OrderedDict()
    skipped = []
    for i, row in enumerate(rows, start=2):  # start=2: row 1 is the header
        ratings, blank, unparseable = {}, [], []
        for a in ATTRIBUTES:
            raw = (row.get(f"{a}_1_5") or "").strip()
            value = _num(raw)
            ratings[a] = value
            if value is None:
                (blank if raw == "" else unparseable).append(
                    a if raw == "" else f"{a}={raw!r}")
        if blank or unparseable:
            parts = []
            if blank:
                parts.append(f"blank ratings: {', '.join(blank)}")
            if unparseable:
                parts.append(f"non-numeric ratings: {', '.join(unparseable)}")
            skipped.append((i, "; ".join(parts)))
            continue
        try:
            p, e = iso_coordinates(ratings)
        except ValueError as exc:
            skipped.append((i, str(exc)))
            continue
        key = (row.get("site_name", "").strip(),
               row.get("date", "").strip(),
               row.get("start_time", "").strip())
        groups.setdefault(key, {"pleasantness": [], "eventfulness": [],
                                "predictor": [], "rows": []})
        groups[key]["pleasantness"].append(p)
        groups[key]["eventfulness"].append(e)
        groups[key]["rows"].append(row)
    return groups, skipped


def analyze(groups, predictor):
    results = []
    for (site, date, start), g in groups.items():
        pred_values = [v for v in (_num(r.get(predictor)) for r in g["rows"])
                       if v is not None]
        results.append({
            "site": site, "date": date, "start": start,
            "pleasantness": summarize(g["pleasantness"]),
            "eventfulness": summarize(g["eventfulness"]),
            "predictor": (sum(pred_values) / len(pred_values)) if pred_values else None,
            "predictor_n": len(pred_values),
        })
    return results


def fmt(x, width=6, places=3):
    return " " * width if x is None or (isinstance(x, float) and math.isnan(x)) \
        else f"{x:{width}.{places}f}"


def print_report(results, predictor, skipped, total_rows):
    print(f"Soundwalk pilot — {len(results)} site-time observation(s) "
          f"from {total_rows} participant row(s)\n")

    header = (f"{'site':28s} {'date':10s} {'time':6s} {'n':>3s}  "
              f"{'Pleasant':>8s} {'95% CI':>17s}  "
              f"{'Eventful':>8s} {'95% CI':>17s}  {predictor:>14s}")
    print(header)
    print("-" * len(header))
    for r in results:
        p, e = r["pleasantness"], r["eventfulness"]
        print(f"{r['site'][:28]:28s} {r['date'][:10]:10s} {r['start'][:6]:6s} "
              f"{p['n']:3d}  {fmt(p['mean'],8)} [{fmt(p['lo'])},{fmt(p['hi'])}]  "
              f"{fmt(e['mean'],8)} [{fmt(e['lo'])},{fmt(e['hi'])}]  "
              f"{fmt(r['predictor'],14,1)}")

    usable = [r for r in results if r["predictor"] is not None]
    print(f"\nScatter rows ({predictor} vs Eventfulness), "
          f"{len(usable)} of {len(results)} with a predictor value:")
    for r in usable:
        e = r["eventfulness"]
        print(f"  x={r['predictor']:.2f}  y={e['mean']:.4f}  "
              f"[{e['lo']:.4f}, {e['hi']:.4f}]  n={e['n']}  {r['site']}")

    if skipped:
        print(f"\n{len(skipped)} row(s) skipped:")
        for line_no, why in skipped[:20]:
            print(f"  line {line_no}: {why}")
        if len(skipped) > 20:
            print(f"  … and {len(skipped) - 20} more")

    print("\nReminders from the protocol:")
    print("  - The unit of analysis is the site-time observation, not the province.")
    print("  - Target ~10 independent ratings per site-time; fewer widens the CI.")
    print("  - Plot every predictor against Eventfulness before fitting any model.")
    print("  - If the proxies do not improve held-out prediction, report that.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default=DEFAULT_CSV, help="observations CSV")
    ap.add_argument("--predictor", default="laeq_db",
                    help="column plotted against Eventfulness (default: laeq_db)")
    args = ap.parse_args(argv)

    if not os.path.exists(args.csv):
        print(f"No such file: {args.csv}", file=sys.stderr)
        return 2

    rows, fieldnames = load_rows(args.csv)

    # The expected early state: the template exists but no fieldwork has happened.
    # Say so plainly instead of looking like a crash.
    if not rows:
        print(f"0 rows found in {os.path.relpath(args.csv)} — no field data "
              f"collected yet.\n")
        print("This is the expected result until the Priority 1 soundwalk pilot runs.")
        print("Add one row per participant per site-time, then run this again.")
        print(f"\nThe file's {len(fieldnames or [])} columns are ready to fill in.")
        return 0

    if args.predictor not in (fieldnames or []):
        print(f"Predictor column '{args.predictor}' is not in the CSV.",
              file=sys.stderr)
        print(f"Available: {', '.join(fieldnames or [])}", file=sys.stderr)
        return 2

    groups, skipped = group_site_times(rows)
    if not groups:
        print(f"{len(rows)} row(s) read, but none had a complete set of the "
              f"eight 1-5 ratings, so no ISO coordinates could be computed.\n")
        for line_no, why in skipped[:20]:
            print(f"  line {line_no}: {why}")
        return 1

    print_report(analyze(groups, args.predictor), args.predictor, skipped, len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
