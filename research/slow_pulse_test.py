#!/usr/bin/env python3
"""Slow-request test: does stating a steady pulse in the prompt make Suno follow the three slowest tempo requests?

Clips: clip01 Gyeongbokgung Palace (42 BPM), clip02 Hanbat Arboretum (62), clip03 Naganeupseong Folk Village (68).
Treatment: the app's current prompt for the place (as exported in paper_model_export.json) plus one sentence stating a
soft steady pulse at the requested tempo. Request shape = the app's current one (custom mode, style + title,
instrumental). 3 generations per clip = 9 API calls (about 18 credits each). The first returned track of each call is analysed.

Success rules, fixed BEFORE any audio was generated or analysed (2026-10-11):
  present  : requested tempo q is within 5% of one of the three strongest autocorrelation-tempogram peaks (30-300 BPM)
  dominant : the single global tempo estimate (default prior) is within 5% of q
Comparison: the same two quantities for the same clips in round 1 and round 2 (paper_audio_reanalysis.json).
Every generated track is reported, including failures. Nine tracks can suggest an effect, not establish one.

    python3 research/slow_pulse_test.py generate
    python3 research/slow_pulse_test.py analyze
"""
import argparse
import concurrent.futures as cf
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import prompt_ablation_experiment as ab  # noqa: E402  (reuses the key loader, request runner and downloader)

PLACES = {'clip01': 'Gyeongbokgung Palace', 'clip02': 'Hanbat Arboretum', 'clip03': 'Naganeupseong Folk Village'}
BPM = {'clip01': 42, 'clip02': 62, 'clip03': 68}
REPS = 3
LOG = ROOT / 'slow_pulse_log.json'
OUT_JSON = ROOT / 'slow_pulse_results.json'
AUDIO = ROOT / 'listener_clips'


def pulse_phrase(bpm):
    return f' A soft, steady pulse at {bpm} BPM with sparse low percussion keeps the beat clear.'


def build_jobs():
    export = json.loads((ROOT / 'paper_model_export.json').read_text())
    prompt = {p['name']: p['prompt'] for p in export['places']}
    jobs = []
    for clip, place in PLACES.items():
        base = prompt[place]
        for r in range(REPS):
            payload = {'customMode': True, 'instrumental': True, 'model': ab.MODEL, 'style': (base + pulse_phrase(BPM[clip]))[:1000],
                       'title': f'{place} - Moodscape pulse test', 'callBackUrl': 'https://httpbin.org/post'}
            jobs.append(dict(clip_id=clip, condition='pulse_anchor', rep=r, payload=payload))
    return jobs


def generate(args):
    k = ab.key()
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    done = {(j['clip_id'], j['rep']) for j in log if j.get('status') == 'SUCCESS'}
    jobs = [j for j in build_jobs() if (j['clip_id'], j['rep']) not in done]
    log = [j for j in log if j.get('status') == 'SUCCESS']
    print(f'{len(jobs)} calls to run', flush=True)
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        futs = {pool.submit(ab.run_job, j, k): j for j in jobs}
        for f in cf.as_completed(futs):
            j = futs[f]
            try:
                job = f.result()
                job['tracks'] = job['tracks'][:1]  # first returned track only, as in the earlier rounds
                for t in job['tracks']:
                    path = AUDIO / f"slowpulse_{job['clip_id']}_r{job['rep']}.mp3"
                    r = ab.requests.get(t['audio_url'], timeout=120); r.raise_for_status(); path.write_bytes(r.content); t['file'] = str(path)
                log.append(job); print('ok  ', job['clip_id'], job['rep'], job['task_id'], flush=True)
            except Exception as e:  # noqa: BLE001
                j['status'] = 'FAILED'; j['error'] = str(e); log.append(j); print('FAIL', j['clip_id'], j['rep'], e, flush=True)
            LOG.write_text(json.dumps(log, indent=1))


def analyze(args):
    import librosa
    import numpy as np
    import scipy.stats as st
    from analyze_generated_audio import detect_key
    out = []
    for j in json.loads(LOG.read_text()):
        if j.get('status') != 'SUCCESS':
            continue
        t = j['tracks'][0]
        y, sr = librosa.load(t['file'], sr=None, mono=True)
        oenv = librosa.onset.onset_strength(y=y, sr=sr)
        single = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr))[0])
        tg = librosa.feature.tempogram(onset_envelope=oenv, sr=sr); ac = tg.mean(axis=1)
        b = librosa.tempo_frequencies(tg.shape[0], sr=sr); idx = np.where((b >= 30) & (b <= 300))[0]
        pk = [i for i in idx[1:-1] if ac[i] > ac[i - 1] and ac[i] > ac[i + 1]]
        top3 = [round(float(b[i]), 1) for i in sorted(pk, key=lambda i: -ac[i])[:3]]
        q = BPM[j['clip_id']]
        root, mode, conf = detect_key(y, sr)
        out.append(dict(clip=j['clip_id'], rep=j['rep'], task_id=j['task_id'], requested=q, single=round(single, 1), top3=top3,
                        present=any(abs(c - q) / q <= .05 for c in top3), dominant=abs(single - q) / q <= .05, key=f'{root} {mode}', duration_s=round(len(y) / sr, 1)))
        print(out[-1], flush=True)
    prev = {(r['clip'], r['group']): r for r in json.loads((ROOT / 'paper_audio_reanalysis.json').read_text())}
    cmp_ = {}
    for clip in PLACES:
        q = BPM[clip]
        for grp in ('round1', 'round2'):
            r = prev[(clip, grp)]
            cmp_[f'{clip}_{grp}'] = dict(single=r['tempo_default_prior'], top3=r['top3'], present=any(abs(c - q) / q <= .05 for c in r['top3']),
                                         dominant=abs(r['tempo_default_prior'] - q) / q <= .05)
    n = len(out)
    summary = dict(n=n, present=sum(o['present'] for o in out), dominant=sum(o['dominant'] for o in out),
                   earlier_present=sum(v['present'] for v in cmp_.values()), earlier_dominant=sum(v['dominant'] for v in cmp_.values()), earlier_n=len(cmp_))
    OUT_JSON.write_text(json.dumps(dict(summary=summary, tracks=out, earlier=cmp_), indent=1))
    print(json.dumps(summary))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['generate', 'analyze'])
    a = ap.parse_args()
    generate(a) if a.cmd == 'generate' else analyze(a)
