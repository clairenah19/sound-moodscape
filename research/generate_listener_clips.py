#!/usr/bin/env python3
"""
Generate real Suno tracks for the listener-experiment stimulus set, mirroring
sunoGenerate() in prompt.js exactly (same endpoint, same payload shape, same
polling logic) so the resulting files are equivalent to what the live app
would produce.

Reads SUNO_API_KEY from a local .env file (never printed, never committed —
.env is in .gitignore). Reads prompts from listener_stimulus_metadata.csv,
downloads each resulting MP3 into research/listener_clips/, and updates the
metadata CSV's source_track / source_provenance / key_review columns in place.

Usage:
    source audio-analysis-venv/bin/activate
    python3 research/generate_listener_clips.py
"""
import csv
import os
import sys
import time

import requests

BASE = "https://api.sunoapi.org"
GEN_PATH = "/api/v1/generate"
POLL_PATH = "/api/v1/generate/record-info"
MODEL = "V4_5"


def load_env_key(env_path=".env"):
    if not os.path.isfile(env_path):
        sys.exit(f"{env_path} not found. Copy .env.example to .env and fill in SUNO_API_KEY first.")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("SUNO_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key:
                    return key
    sys.exit("SUNO_API_KEY not set (or empty) in .env")


def generate_one(prompt, key):
    gen_res = requests.post(
        BASE + GEN_PATH,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        json={"prompt": prompt, "customMode": False, "instrumental": True, "model": MODEL,
              "callBackUrl": "https://httpbin.org/post"},
        timeout=30,
    )
    if not gen_res.ok:
        raise RuntimeError(f"generate HTTP {gen_res.status_code}: {gen_res.text[:200]}")
    gen_json = gen_res.json()
    task_id = (gen_json.get("taskId") or gen_json.get("task_id")
               or (gen_json.get("data") or {}).get("taskId")
               or (gen_json.get("data") or {}).get("task_id"))
    if not task_id:
        raise RuntimeError(f"no taskId in response: {str(gen_json)[:200]}")

    for _ in range(50):  # ~2.5 min max, matching prompt.js
        time.sleep(3)
        poll_res = requests.get(
            BASE + POLL_PATH, params={"taskId": task_id},
            headers={"Authorization": "Bearer " + key}, timeout=30,
        )
        if not poll_res.ok:
            continue
        pj = poll_res.json()
        status = (pj.get("data") or {}).get("status", "")
        if status and ("FAIL" in status.upper() or "ERROR" in status.upper()):
            raise RuntimeError(f"generation failed: {status}")
        suno_data = (((pj.get("data") or {}).get("response") or {}).get("sunoData"))
        if isinstance(suno_data, list):
            for item in suno_data:
                audio_url = item.get("audioUrl") or item.get("streamAudioUrl")
                if audio_url:
                    return audio_url
    raise RuntimeError("generation timed out")


def main():
    key = load_env_key()
    metadata_path = "research/listener_stimulus_metadata.csv"
    clips_dir = "research/listener_clips"
    os.makedirs(clips_dir, exist_ok=True)

    with open(metadata_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

    for row in rows:
        clip_id = row["clip_id"]
        if row.get("source_track", "").strip():
            print(f"{clip_id}: already has a source_track, skipping.")
            continue

        prompt = row["prompt"]
        print(f"{clip_id} ({row.get('place', '?')}): generating...")
        try:
            audio_url = generate_one(prompt, key)
        except Exception as e:
            print(f"  FAILED: {e}")
            row["source_provenance"] = f"GENERATION FAILED: {e}"
            row["key_review"] = "FAILED"
            continue

        mp3_path = os.path.join(clips_dir, f"{clip_id}.mp3")
        audio_res = requests.get(audio_url, timeout=60)
        audio_res.raise_for_status()
        with open(mp3_path, "wb") as out:
            out.write(audio_res.content)

        row["source_track"] = mp3_path
        row["source_provenance"] = "sunoapi.org V4_5, generated " + time.strftime("%Y-%m-%d")
        row["key_review"] = "PENDING"  # human listen-through still recommended, not done here
        print(f"  saved {mp3_path} ({len(audio_res.content)} bytes)")

    with open(metadata_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nUpdated {metadata_path}.")


if __name__ == "__main__":
    main()
