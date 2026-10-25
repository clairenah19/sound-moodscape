#!/usr/bin/env python3
"""Second minor-key retest, for clip07 (Government Complex Sejong) and clip10
(Hyundai Motor Asan Plant) — testing a genuinely DIFFERENT technical approach,
not just reworded text.

Finding that motivated this: the original 10-clip test (2026-09-13) and the
clip09 retest both sent {customMode: false, prompt: "..."} — a flat natural-
language prompt Suno "auto-interprets" freely. But the live app's real
buildSunoGenerationRequest() (prompt.js), as of commit 52b0d62 (2026-09-20),
actually sends {customMode: true, style: "...", title: "..."} instead — Suno's
documented "custom mode" where style is meant to be treated as explicit,
structured control rather than prose Suno reinterprets. That switch happened
AFTER the real-audio test, so neither prior test reflects what the live app
currently does. This script matches buildSunoGenerationRequest() exactly.
"""
import os
import sys
import time

import requests

BASE = "https://api.sunoapi.org"
GEN_PATH = "/api/v1/generate"
POLL_PATH = "/api/v1/generate/record-info"
MODEL = "V4_5"

CLIPS = {
    "clip07_sejong": {
        "style": (
            "Music for a decentralized government complex with the world's longest "
            "rooftop garden connecting 15 ministries. In D# minor key — melancholic, "
            "somber, shadowed tonality, no major-key brightness. ambient IDM, glitchy "
            "minimalist electronic, synthesizer pads, cleanroom atmosphere, precise, "
            "around 95 BPM. Instrumentation: quiet corridor echo, rooftop-garden breeze, "
            "official footsteps. Cinematic, atmospheric, no vocals, no lyrics."
        ),
        "title": "Government Complex Sejong — Moodscape",
        "requested_bpm": 95,
        "requested_mode": "minor",
    },
    "clip10_asan": {
        "style": (
            "Music for a 300,000-car-a-year assembly plant building Sonatas and "
            "electric IONIQs. In G minor key — melancholic, somber, shadowed tonality, "
            "no major-key brightness. futuristic progressive electronic, clean "
            "high-tech synth layers, driving modular rhythm, around 138 BPM. "
            "Instrumentation: press-line stamping thud, paint-booth mist hiss, "
            "engine-line torque wrench. Cinematic, atmospheric, no vocals, no lyrics."
        ),
        "title": "Hyundai Motor Asan Plant — Moodscape",
        "requested_bpm": 138,
        "requested_mode": "minor",
    },
}


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


def generate_one(style, title, key):
    # Mirrors buildSunoGenerationRequest() in prompt.js exactly: customMode true,
    # fully-instrumental style+title controls, no freeform "prompt" field.
    payload = {
        "customMode": True,
        "instrumental": True,
        "model": MODEL,
        "style": style,
        "title": title[:80],
        "callBackUrl": "https://httpbin.org/post",
    }
    gen_res = requests.post(
        BASE + GEN_PATH,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        json=payload,
        timeout=30,
    )
    if not gen_res.ok:
        raise RuntimeError(f"generate HTTP {gen_res.status_code}: {gen_res.text[:300]}")
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
    for clip_id, spec in CLIPS.items():
        print(f"\n=== {clip_id} ===")
        print("Style sent to Suno (customMode=true):")
        print(spec["style"])
        audio_url = generate_one(spec["style"], spec["title"], key)
        out_path = f"research/listener_clips/{clip_id}_retest_custommode.mp3"
        audio_res = requests.get(audio_url, timeout=60)
        audio_res.raise_for_status()
        with open(out_path, "wb") as out:
            out.write(audio_res.content)
        print(f"Saved {out_path} ({len(audio_res.content)} bytes)")


if __name__ == "__main__":
    main()
