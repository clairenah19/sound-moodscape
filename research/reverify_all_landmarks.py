#!/usr/bin/env python3
"""Re-verify all 10 original landmark clips against real Suno audio, using:
  1. The CURRENT (fixed) buildSunoPrompt() output — institutional category fix,
     Sejong major-key fix, reworded minor-key mode clause.
  2. customMode:true with style+title fields, matching the live app's real
     buildSunoGenerationRequest() exactly (the original 2026-09-13 test used
     the older customMode:false + flat prompt shape, which the live app has
     not used since commit 52b0d62 on 2026-09-20).

Saves MP3s to research/listener_clips/v2_<clip_id>.mp3 and writes a comparison
CSV to research/reverify_v2_results.csv. Does not touch the original listener
experiment files.
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

CLIPS = [
    {"clip_id": "clip01", "name": "Gyeongbokgung Palace", "requested_bpm": 42, "requested_mode": "major",
     "style": "Music for a 14th-century royal palace at dawn, guards changing in ceremonial silence. In A major key — bright, open, uplifted tonality. serene traditional Korean meditation music, peaceful daegeum flute and gayageum pluck, warm, quiet, contemplative, around 42 BPM. Instrumentation: ceremonial court music, stone courtyard reverb, temple bell. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip02", "name": "Hanbat Arboretum", "requested_bpm": 62, "requested_mode": "major",
     "style": "Music for a quiet botanical garden in the middle of the science city. In B major key — bright, open, uplifted tonality. peaceful cinematic ambient, quiet nature soundscape, gentle acoustic strings, serene, warm, around 62 BPM. Instrumentation: birdsong, koto-like pluck, leaf rustle. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip03", "name": "Naganeupseong Folk Village", "requested_bpm": 68, "requested_mode": "major",
     "style": "Music for a 600-year-old walled town still farmed by about 100 households behind stone ramparts. In C major key — bright, open, uplifted tonality. serene traditional Korean meditation music, peaceful daegeum flute and gayageum pluck, warm, quiet, contemplative, around 68 BPM. Instrumentation: straw-roof wind, well-bucket creak, farmyard rooster. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip04", "name": "Korean Folk Village", "requested_bpm": 75, "requested_mode": "major",
     "style": "Music for a recreated Joseon-dynasty village with 260 relocated houses and live folk performances. In C# major key — bright, open, uplifted tonality. warm acoustic folk, beautiful traditional Korean court-fusion, serene and happy, gentle rhythm, around 75 BPM. Instrumentation: farmer's percussion band, tightrope-walker gasp, thatched-roof wind. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip05", "name": "Oeam Folk Village", "requested_bpm": 81, "requested_mode": "major",
     "style": "Music for a 500-year-old village of thatched and tiled hanok where residents still farm the land. In C# major key — bright, open, uplifted tonality. warm acoustic folk, beautiful traditional Korean court-fusion, serene and happy, gentle rhythm, around 81 BPM. Instrumentation: thatched-roof wind rustle, stream trickle, wooden gate creak. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip06", "name": "Gunsan Modern History Street", "requested_bpm": 88, "requested_mode": "major",
     "style": "Music for a preserved 1920s colonial port street of Japanese banks and warehouses turned museums. In D major key — bright, open, uplifted tonality. calm lo-fi, soft mellow keys, gentle warmth, relaxed, around 88 BPM. Instrumentation: old bank-vault echo, tram-bell ghost, retro film-reel flutter. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip07", "name": "Government Complex Sejong", "requested_bpm": 95, "requested_mode": "major",
     "style": "Music for a decentralized government complex with the world's longest rooftop garden connecting 15 ministries. In D# major key — bright, open, uplifted tonality. calm institutional ambient, soft airy pads, quiet rooftop-garden breeze, composed, understated, around 95 BPM. Instrumentation: quiet corridor echo, rooftop-garden breeze, official footsteps. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip08", "name": "Kia AutoLand Gwangju", "requested_bpm": 107, "requested_mode": "major",
     "style": "Music for a car rolling off the line every few seconds inside a vast automated assembly plant. In E major key — bright, open, uplifted tonality. ambient IDM, glitchy minimalist electronic, warm synthesizer pads, cleanroom atmosphere, precise, around 107 BPM. Instrumentation: robotic-arm servo whine, conveyor-belt clank, assembly-line rhythm. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip09", "name": "Gangnam", "requested_bpm": 115, "requested_mode": "minor",
     "style": "Music for a glittering high-rise district of designer boutiques and rooftop bars. In F minor key — melancholic, somber, shadowed tonality, no major-key brightness. lo-fi hip-hop, relaxing city-pop synth pads, urban beat, around 115 BPM. Instrumentation: glossy K-pop synth-pop, sidechain-pumped bass, glass-tower shimmer. Cinematic, atmospheric, no vocals, no lyrics."},
    {"clip_id": "clip10", "name": "Hyundai Motor Asan Plant", "requested_bpm": 138, "requested_mode": "minor",
     "style": "Music for a 300,000-car-a-year assembly plant building Sonatas and electric IONIQs. In G minor key — melancholic, somber, shadowed tonality, no major-key brightness. futuristic progressive electronic, clean high-tech synth layers, driving modular rhythm, around 138 BPM. Instrumentation: press-line stamping thud, paint-booth mist hiss, engine-line torque wrench. Cinematic, atmospheric, no vocals, no lyrics."},
]


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
    payload = {
        "customMode": True, "instrumental": True, "model": MODEL,
        "style": style, "title": title[:80],
        "callBackUrl": "https://httpbin.org/post",
    }
    gen_res = requests.post(
        BASE + GEN_PATH,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        json=payload, timeout=30,
    )
    if not gen_res.ok:
        raise RuntimeError(f"generate HTTP {gen_res.status_code}: {gen_res.text[:300]}")
    gen_json = gen_res.json()
    task_id = (gen_json.get("taskId") or gen_json.get("task_id")
               or (gen_json.get("data") or {}).get("taskId")
               or (gen_json.get("data") or {}).get("task_id"))
    if not task_id:
        raise RuntimeError(f"no taskId in response: {str(gen_json)[:300]}")

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
    raise RuntimeError("generation timed out")


def main():
    key = load_env_key()
    clips_dir = "research/listener_clips"
    os.makedirs(clips_dir, exist_ok=True)
    results = []

    for spec in CLIPS:
        clip_id, name = spec["clip_id"], spec["name"]
        print(f"\n=== {clip_id} ({name}) ===")
        out_path = os.path.join(clips_dir, f"v2_{clip_id}.mp3")
        if os.path.isfile(out_path):
            print(f"  already exists, skipping generation")
            results.append({**spec, "path": out_path, "status": "already_had"})
            continue
        try:
            audio_url = generate_one(spec["style"], f"{name} — Moodscape", key)
            audio_res = requests.get(audio_url, timeout=60)
            audio_res.raise_for_status()
            with open(out_path, "wb") as out:
                out.write(audio_res.content)
            print(f"  saved {out_path} ({len(audio_res.content)} bytes)")
            results.append({**spec, "path": out_path, "status": "ok"})
        except Exception as e:
            print(f"  FAILED: {e}")
            results.append({**spec, "path": "", "status": f"FAILED: {e}"})

    with open("research/reverify_v2_manifest.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["clip_id", "name", "requested_bpm", "requested_mode", "path", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    print("\nWrote research/reverify_v2_manifest.csv")


if __name__ == "__main__":
    main()
