#!/usr/bin/env python3
"""Why did Suno return the wrong mode? Ablation on the three clips that asked for minor (clip07, 09, 10).

Three conditions, N repetitions each, same model (V4_5) as the original ten tracks:
  A  current   - the exact prompt from listener_stimulus_metadata.csv, non-custom mode (what produced the original clips)
  B  plain     - non-custom mode, mode + tempo only: "Instrumental music. Minor key, around N BPM. No vocals."
  C  custom    - customMode=true: style = the original genre/mood words + explicit root ("in A minor") + tempo.
                 Custom mode has no free-text scene description, so the scenic sentence and instrument list are dropped.

Condition C therefore changes two things at once (request mode and explicit root); read it as
"the best control the API offers", not as a single-variable test. Every returned track is analysed
(one API call usually returns two), so the unit is a track, and tracks from the same call are not independent.

Stages (resumable; the log records every task id):
    python3 research/prompt_ablation_experiment.py generate [--reps 5] [--pilot]
    python3 research/prompt_ablation_experiment.py analyze
The API key is read from .env (never printed). Audio goes to --audio-dir (default: outside the repo).
"""
import argparse
import concurrent.futures as cf
import csv
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
BASE, MODEL = 'https://api.sunoapi.org', 'V4_5'
CLIPS = ['clip07', 'clip09', 'clip10']
CONDITIONS = ['A_current', 'B_plain', 'C_custom']
ROOT_NOTE = 'A'
LOG = ROOT / 'prompt_ablation_log.json'
RESULTS = ROOT / 'prompt_ablation_results.csv'


def key():
    for line in open(ROOT.parent / '.env'):
        if line.startswith('SUNO_API_KEY=') and line.split('=', 1)[1].strip():
            return line.split('=', 1)[1].strip()
    sys.exit('SUNO_API_KEY missing from .env')


def clip_rows():
    with (ROOT / 'listener_stimulus_metadata.csv').open(newline='', encoding='utf-8') as f:
        return {r['clip_id']: r for r in csv.DictReader(f) if r['clip_id'] in CLIPS}


def style_words(prompt, mode_phrase):
    """The genre/mood sentence between the scene sentence and the 'minor key, around N BPM' clause."""
    body = prompt.split('. ', 1)[1]
    return body.split(', ' + mode_phrase)[0]


def payload(condition, row):
    bpm = int(float(row['bpm']))
    mode = row['intended_mode']  # 'minor key'
    base = {'instrumental': True, 'model': MODEL, 'callBackUrl': 'https://httpbin.org/post'}
    if condition == 'A_current':
        return {**base, 'customMode': False, 'prompt': row['prompt']}
    if condition == 'B_plain':
        return {**base, 'customMode': False, 'prompt': f'Instrumental music. {mode.capitalize()}, around {bpm} BPM. No vocals.'}
    if condition == 'C_custom':
        style = f"{style_words(row['prompt'], mode)}, in {ROOT_NOTE} minor, {bpm} BPM"
        return {**base, 'customMode': True, 'style': style, 'title': 'Moodscape ablation'}
    raise ValueError(condition)


def run_job(job, k):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + k}
    res = requests.post(BASE + '/api/v1/generate', headers=headers, json=job['payload'], timeout=30)
    body = res.json()
    task = (body.get('data') or {}).get('taskId')
    if not res.ok or not task:
        raise RuntimeError(f'generate failed: HTTP {res.status_code} {str(body)[:200]}')
    job['task_id'] = task
    for _ in range(140):  # up to ~7 minutes
        time.sleep(3)
        pj = requests.get(BASE + '/api/v1/generate/record-info', params={'taskId': task}, headers=headers, timeout=30).json()
        data = pj.get('data') or {}
        status = (data.get('status') or '').upper()
        if 'FAIL' in status or 'ERROR' in status:
            raise RuntimeError(f'task {task}: {status}')
        if status == 'SUCCESS':
            tracks = ((data.get('response') or {}).get('sunoData')) or []
            job['tracks'] = [{'id': t.get('id'), 'audio_url': t.get('audioUrl'), 'duration': t.get('duration')} for t in tracks if t.get('audioUrl')]
            job['status'] = 'SUCCESS'
            return job
    raise RuntimeError(f'task {task}: timed out')


def download(job, audio_dir):
    audio_dir.mkdir(parents=True, exist_ok=True)
    for n, t in enumerate(job['tracks']):
        path = audio_dir / f"{job['clip_id']}_{job['condition']}_r{job['rep']}_t{n}.mp3"
        if not path.exists():
            r = requests.get(t['audio_url'], timeout=90)
            r.raise_for_status()
            path.write_bytes(r.content)
        t['file'] = str(path)


def load_log():
    return json.loads(LOG.read_text()) if LOG.exists() else []


def save_log(log):
    LOG.write_text(json.dumps(log, indent=1))


def generate(args):
    k = key()
    rows = clip_rows()
    log = load_log()
    done = {(j['clip_id'], j['condition'], j['rep']) for j in log if j.get('status') == 'SUCCESS'}
    jobs = [dict(clip_id=c, condition=cond, rep=r, payload=payload(cond, rows[c]))
            for r in range(args.reps) for c in (args.clips or CLIPS) for cond in (args.conditions or CONDITIONS)
            if (c, cond, r) not in done]
    if args.pilot:
        jobs = [j for j in jobs if j['condition'] == 'C_custom'][:1]
    print(f'{len(jobs)} generation calls to run ({len(done)} already done)', flush=True)
    log = [j for j in log if j.get('status') == 'SUCCESS']
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_job, j, k): j for j in jobs}
        for fut in cf.as_completed(futures):
            j = futures[fut]
            try:
                job = fut.result()
                download(job, Path(args.audio_dir))
                log.append(job)
                print(f"ok   {job['clip_id']} {job['condition']} r{job['rep']} task={job['task_id']} tracks={len(job['tracks'])}", flush=True)
            except Exception as e:
                j['status'] = 'FAILED'; j['error'] = str(e)
                log.append(j)
                print(f"FAIL {j['clip_id']} {j['condition']} r{j['rep']}: {e}", flush=True)
            save_log(log)


def analyze(args):
    sys.path.insert(0, str(ROOT))
    from analyze_generated_audio import analyze_clip
    rows = clip_rows()
    out = []
    for j in load_log():
        if j.get('status') != 'SUCCESS':
            continue
        req_bpm = float(rows[j['clip_id']]['bpm'])
        for n, t in enumerate(j['tracks']):
            if not t.get('file') or not os.path.isfile(t['file']):
                continue
            bpm, key_label, mode, conf = analyze_clip(t['file'])
            best = min((bpm / 2, bpm, bpm * 2), key=lambda c: abs(c - req_bpm))
            out.append(dict(clip_id=j['clip_id'], condition=j['condition'], rep=j['rep'], track=n, task_id=j['task_id'],
                            requested_bpm=req_bpm, detected_bpm=round(bpm, 1), octave_corrected_err_pct=round(abs(best - req_bpm) / req_bpm * 100, 1),
                            requested_mode='minor', detected_key=key_label, detected_mode=mode, mode_match=mode == 'minor',
                            key_confidence=round(conf, 3), duration_s=t.get('duration')))
            print(out[-1]['clip_id'], out[-1]['condition'], out[-1]['detected_key'], out[-1]['detected_bpm'], flush=True)
    if not out:
        sys.exit('nothing to analyze')
    with RESULTS.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(f'Wrote {RESULTS} ({len(out)} tracks)')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('generate'); g.add_argument('--reps', type=int, default=5); g.add_argument('--workers', type=int, default=5)
    g.add_argument('--pilot', action='store_true'); g.add_argument('--clips', nargs='+', choices=CLIPS); g.add_argument('--conditions', nargs='+', choices=CONDITIONS); g.add_argument('--audio-dir', default=os.environ.get('ABLATION_AUDIO_DIR', str(ROOT.parent / '.ablation_audio')))
    sub.add_parser('analyze')
    args = ap.parse_args()
    generate(args) if args.cmd == 'generate' else analyze(args)


if __name__ == '__main__':
    main()
