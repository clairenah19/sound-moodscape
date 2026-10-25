#!/usr/bin/env python3
"""Regenerate clip 07 with an unmistakable perceived quarter-note pulse at 95 BPM.

This is intentionally stricter than the descriptive Moodscape prompt.  The goal is
not merely to let a tempo detector find 95 BPM, but to make 95 BPM the pulse a
listener is most likely to tap.  One Suno request may return more than one track;
all returned tracks are retained for listening rather than silently selecting one.
"""
import json
import argparse
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.sunoapi.org"
MODEL = "V4_5"
ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "listener_clips"
LOG = ROOT / "clip07_perceived_95_generation.json"

STYLE = (
    "Instrumental music for Government Complex Sejong and its rooftop garden. "
    "Calm, bright institutional ambient in D-sharp major, composed and understated, "
    "with soft airy synthesizer pads and subtle corridor ambience. "
    "STRICT TEMPO: exactly 95 BPM in 4/4. The main beat a listener taps must be the "
    "95 BPM quarter-note pulse. Start that pulse immediately and keep it unchanged "
    "for the entire track. Use a soft muted kick on every quarter note, a quiet rim "
    "click on beats 2 and 4, and delicate closed hi-hats on eighth notes so the "
    "95 BPM beat is unmistakable. No half-time feel, no double-time feel, no rubato, "
    "no beatless intro, no tempo changes, and no long free-floating passages. "
    "Include a light rooftop-garden breeze and restrained official footsteps without "
    "obscuring the beat. Cinematic and atmospheric, but clearly rhythmic. No vocals, "
    "no lyrics."
)

# Suno repeatedly rendered the direct 95 BPM instruction with a human-tapped
# pulse near 48 BPM.  This condition compensates for that observed 1:2 error:
# the production grid is requested at 190 while the kick/backbeat that a person
# should tap is explicitly placed on every other grid beat (95 pulses/minute).
COMPENSATED_STYLE = (
    "Instrumental rhythm-forward electronic music for Government Complex Sejong "
    "and its rooftop garden. Bright, composed and understated in D-sharp major, "
    "with soft airy synthesizer pads, a clean modern pulse, and subtle corridor "
    "ambience. Use a 190 BPM double-time production grid in 4/4, but make the "
    "PRIMARY HUMAN-TAPPED PULSE exactly 95 BPM: place a firm muted kick on every "
    "other 190 BPM grid beat, exactly 95 kick pulses per minute, with a clear snare "
    "backbeat and bass-note attack reinforcing that same 95 BPM pulse. The listener "
    "must naturally nod and tap at 95 BPM, never at 47 or 48 BPM. Start the 95 BPM "
    "kick immediately and keep it constant throughout. Midtempo minimal electronic "
    "groove, not beatless ambient; no slow half-speed pulse, no rubato, no tempo "
    "changes, no long intro. Light rooftop breeze and restrained footsteps must not "
    "obscure the beat. Cinematic, clean, atmospheric, no vocals, no lyrics."
)


def api_key():
    env_file = ROOT.parent / ".env"
    if not env_file.exists():
        sys.exit(".env not found")
    for line in env_file.read_text().splitlines():
        if line.startswith("SUNO_API_KEY="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value
    sys.exit("SUNO_API_KEY is missing from .env")


def task_id_from(payload):
    return (
        payload.get("taskId")
        or payload.get("task_id")
        or (payload.get("data") or {}).get("taskId")
        or (payload.get("data") or {}).get("task_id")
    )


def request_json(url, *, headers=None, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code} from Suno: {detail[:500]}") from error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compensated",
        action="store_true",
        help="request a 190 BPM grid to compensate for Suno's observed 1:2 perceptual error",
    )
    parser.add_argument(
        "--task-id",
        help="resume polling/downloading an existing Suno task without creating or charging for a new one",
    )
    args = parser.parse_args()
    style = COMPENSATED_STYLE if args.compensated else STYLE
    name = "clip07_sejong_perceived95_compensated" if args.compensated else "clip07_sejong_perceived95"
    log_path = ROOT / ("clip07_perceived_95_compensated_generation.json" if args.compensated else LOG.name)
    key = api_key()
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
        "User-Agent": "Mozilla/5.0 Moodscape-Audio-Research/1.0",
        "Accept": "application/json",
    }
    payload = {
        "customMode": True,
        "instrumental": True,
        "model": MODEL,
        "style": style[:1000],
        "title": "Government Complex Sejong - perceived 95 BPM compensated" if args.compensated else "Government Complex Sejong - clear 95 BPM pulse",
        "callBackUrl": "https://httpbin.org/post",
    }
    if args.task_id:
        task_id = args.task_id
        print(f"Resuming task {task_id}; waiting for audio...", flush=True)
    else:
        response = request_json(BASE + "/api/v1/generate", headers=headers, payload=payload)
        task_id = task_id_from(response)
        if not task_id:
            sys.exit("Suno response did not contain a task ID")
        print(f"Submitted task {task_id}; waiting for audio...", flush=True)

    for attempt in range(80):
        time.sleep(3)
        query = urllib.parse.urlencode({"taskId": task_id})
        body = request_json(
            BASE + "/api/v1/generate/record-info?" + query,
            headers={
                "Authorization": "Bearer " + key,
                "User-Agent": "Mozilla/5.0 Moodscape-Audio-Research/1.0",
                "Accept": "application/json",
            },
        )
        status = (body.get("data") or {}).get("status", "")
        if "FAIL" in status.upper() or "ERROR" in status.upper():
            sys.exit(f"Suno generation failed: {status}")
        tracks = (((body.get("data") or {}).get("response") or {}).get("sunoData"))
        if not isinstance(tracks, list) or not tracks:
            if attempt % 10 == 0:
                print(f"Still waiting ({status or 'pending'})...", flush=True)
            continue

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        saved = []
        for index, track in enumerate(tracks, 1):
            url = track.get("audioUrl") or track.get("streamAudioUrl")
            if not url:
                continue
            path = OUT_DIR / f"{name}_candidate{index}.mp3"
            audio_request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 Moodscape-Audio-Research/1.0"},
            )
            with urllib.request.urlopen(audio_request, timeout=120) as response:
                audio_content = response.read()
            path.write_bytes(audio_content)
            saved.append({
                "candidate": index,
                "file": str(path.relative_to(ROOT.parent)),
                "bytes": len(audio_content),
                "suno_id": track.get("id"),
            })
            print(f"Saved {path} ({len(audio_content)} bytes)", flush=True)
        log_path.write_text(json.dumps({
            "task_id": task_id,
            "model": MODEL,
            "target_bpm": 95,
            "success_rule": "median human tap tempo within 5% of 95 BPM",
            "prompt": style,
            "suno_instruction_bpm": 190 if args.compensated else 95,
            "compensation_for_observed_half_speed": args.compensated,
            "tracks": saved,
        }, indent=2))
        if not saved:
            sys.exit("Generation completed but no downloadable audio URL was returned")
        print(f"Wrote provenance log to {log_path}", flush=True)
        return
    sys.exit("Timed out waiting for Suno")


if __name__ == "__main__":
    main()
