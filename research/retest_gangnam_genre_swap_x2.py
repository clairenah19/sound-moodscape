#!/usr/bin/env python3
"""Run the exact same Gangnam genre-swap prompt 2 more times, to check whether
the first minor-key match was a real effect or just one lucky roll of Suno's
stochastic generation.
"""
import os
import sys
import time

import requests

BASE = "https://api.sunoapi.org"
GEN_PATH = "/api/v1/generate"
POLL_PATH = "/api/v1/generate/record-info"
MODEL = "V4_5"

STYLE = (
    "Music for a glittering high-rise district of designer boutiques and rooftop "
    "bars. In F minor key — melancholic, somber, shadowed tonality, no major-key "
    "brightness. dark synth-pop, moody downtempo electronic, atmospheric "
    "minor-key synths, around 115 BPM. Instrumentation: glossy K-pop synth-pop, "
    "sidechain-pumped bass, glass-tower shimmer. Cinematic, atmospheric, no "
    "vocals, no lyrics."
)
TITLE = "Gangnam — Moodscape (genre-swap test)"


def load_env_key(env_path=".env"):
    if not os.path.isfile(env_path):
        sys.exit(f"{env_path} not found.")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("SUNO_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key:
                    return key
    sys.exit("SUNO_API_KEY not set (or empty) in .env")


def generate_one(key):
    payload = {
        "customMode": True, "instrumental": True, "model": MODEL,
        "style": STYLE, "title": TITLE[:80],
        "callBackUrl": "https://httpbin.org/post",
    }
    gen_res = requests.post(
        BASE + GEN_PATH,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        json=payload, timeout=30,
    )
    gen_res.raise_for_status()
    gen_json = gen_res.json()
    task_id = (gen_json.get("taskId") or gen_json.get("task_id")
               or (gen_json.get("data") or {}).get("taskId")
               or (gen_json.get("data") or {}).get("task_id"))
    if not task_id:
        raise RuntimeError(f"no taskId in response: {str(gen_json)[:300]}")
    print(f"  taskId={task_id}, polling...")

    for i in range(60):
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
        if i % 5 == 0:
            print(f"  ...still waiting (status={status or 'pending'})")
    raise RuntimeError("generation timed out")


def main():
    key = load_env_key()
    for n in (2, 3):
        print(f"\n=== Gangnam genre-swap, run {n} ===")
        audio_url = generate_one(key)
        out_path = f"research/listener_clips/clip09_genre_swap_test_run{n}.mp3"
        audio_res = requests.get(audio_url, timeout=60)
        audio_res.raise_for_status()
        with open(out_path, "wb") as out:
            out.write(audio_res.content)
        print(f"Saved {out_path} ({len(audio_res.content)} bytes)")


if __name__ == "__main__":
    main()
