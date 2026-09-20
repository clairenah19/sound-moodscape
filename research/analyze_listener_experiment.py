#!/usr/bin/env python3
"""Analyze real exported sessions. Clip-level Spearman permutation test; no invented observations."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ATTRS = ['pleasant', 'chaotic', 'vibrant', 'uneventful', 'calm', 'annoying', 'eventful', 'monotonous']
ROOT = Path(__file__).resolve().parent

def iso_eventfulness(row):
    r = {}
    for key in ATTRS:
        value = float(row[key + '_1_5'])
        if not math.isfinite(value) or value not in range(1, 6):
            raise ValueError('All eight ratings must be integers from 1 to 5')
        r[key] = value
    return ((r['eventful'] - r['uneventful']) + math.sqrt(.5) *
            (r['chaotic'] - r['calm'] + r['vibrant'] - r['monotonous'])) / (4 + math.sqrt(32))

def validated_sessions(rows, metadata, config):
    clips = {c['id']: c for c in config['clips']}
    targets = {r['clip_id']: r for r in metadata}
    if set(clips) != set(targets) or len(targets) != len(metadata):
        raise ValueError('Stimulus metadata must match the unique published clips')
    sessions, excluded = {}, []
    seen = {}
    for row in rows:
        pid = row['participant_id']
        cid = row['clip_id']
        if not pid or cid not in clips:
            raise ValueError('Unknown clip or missing participant ID')
        key = (pid, cid)
        if key in seen:
            if seen[key] == row:
                continue  # Repeated copies of the exact same download are deduplicated.
            raise ValueError(f'Conflicting duplicate response for {pid}/{cid}')
        seen[key] = row
        if row['stimulus_version'] != config['version'] or row['protocol_version'] != config['protocol_version']:
            raise ValueError('Do not mix protocol or stimulus versions')
        if row['clip_sha256'] != clips[cid]['sha256'] or not clips[cid]['sha256']:
            raise ValueError('Clip hash does not match the frozen stimulus manifest')
        if not row['consent_utc']:
            raise ValueError('Consent timestamp is required')
        heard = float(row['listened_seconds'])
        duration = float(row['clip_duration_seconds'])
        response = float(row['response_seconds'])
        if not all(math.isfinite(x) for x in (heard, duration, response)) or duration != clips[cid]['duration_seconds'] or heard < duration - .25 or response < duration - .25:
            raise ValueError('Incomplete clip playback or invalid timing')
        iso_eventfulness(row)
        sessions.setdefault(pid, {})[cid] = row
    complete = {}
    for pid, ratings in sessions.items():
        if set(ratings) != set(clips):
            excluded.append(pid)
        elif sorted(int(r['presentation_order']) for r in ratings.values()) != list(range(1,len(clips)+1)):
            raise ValueError('Invalid presentation order')
        else:
            complete[pid] = ratings
    return complete, excluded

def analyze(rows, metadata, config, permutations=49999, bootstrap=5000, seed=20260913):
    import numpy as np
    from scipy.stats import rankdata, spearmanr
    sessions, excluded = validated_sessions(rows, metadata, config)
    if len(sessions) < 15:
        return None, f'{len(sessions)} complete participants; minimum exploratory cohort is 15. {len(excluded)} incomplete sessions excluded.'
    ids = [c['id'] for c in config['clips']]
    targets = {r['clip_id']: r for r in metadata}
    scores = np.array([float(targets[c]['activity_score_0_100']) for c in ids])
    matrix = np.array([[iso_eventfulness(session[c]) for c in ids] for session in sessions.values()])
    means = matrix.mean(axis=0)
    if len(set(scores)) < 2 or len(set(means)) < 2:
        raise ValueError('Correlation undefined: constant stimulus scores or constant clip-mean ratings')
    rho = float(spearmanr(scores, means).statistic)
    rng = np.random.default_rng(seed)
    x = rankdata(scores); x -= x.mean(); x /= np.linalg.norm(x)
    y = rankdata(means); y -= y.mean(); y /= np.linalg.norm(y)
    extreme = sum(abs(float(np.dot(x, rng.permutation(y)))) >= abs(rho) - 1e-12 for _ in range(permutations))
    p = (extreme + 1) / (permutations + 1)
    boot = []
    for _ in range(bootstrap):
        sample = matrix[rng.integers(0, len(matrix), len(matrix))].mean(axis=0)
        if len(set(sample)) > 1:
            boot.append(float(spearmanr(scores, sample).statistic))
    ci = np.quantile(boot, [.025, .975]).tolist() if boot else None
    return dict(participants=len(sessions), excluded_incomplete=len(excluded), clips=len(ids),
        rho=rho, p_two_sided=p, ci_participant_bootstrap=ci, valid_bootstraps=len(boot),
        permutations=permutations, seed=seed,
        clip_means=[{'clip_id':c,'score':float(scores[i]),'mean_eventfulness':float(means[i])} for i,c in enumerate(ids)]), ''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('responses', nargs='*', type=Path)
    parser.add_argument('--manifest', type=Path, default=ROOT/'listener_stimuli.json')
    parser.add_argument('--metadata', type=Path, default=ROOT/'listener_stimulus_metadata.csv')
    parser.add_argument('--output', type=Path, default=ROOT/'listener_experiment_results.md')
    args = parser.parse_args()
    rows = []
    for file in args.responses:
        with file.open(newline='', encoding='utf-8-sig') as src:
            rows.extend(csv.DictReader(src))
    if not rows:
        print('0 rows found — no listener data collected yet. Results remain [PENDING].')
        return
    config = json.loads(args.manifest.read_text())
    if not config.get('ready'):
        parser.error('Stimulus manifest is not ready; do not analyze placeholder clips')
    with args.metadata.open(newline='') as src:
        metadata = list(csv.DictReader(src))
    try:
        result, pending = analyze(rows, metadata, config)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    if result is None:
        print('[PENDING] ' + pending)
        return
    evidence = '\n'.join(f'- `{p.name}`: SHA-256 `{hashlib.sha256(p.read_bytes()).hexdigest()}`' for p in args.responses)
    direction = 'Positive association' if result['rho'] > 0 else 'Non-positive association'
    decision = 'Meets the prespecified positive-direction and p < .05 criterion for these clips.' if result['rho'] > 0 and result['p_two_sided'] < .05 else 'Does not meet the prespecified positive-direction and p < .05 criterion.'
    text = '# Listener experiment results\n\n'
    text += f"{result['participants']} complete participants; {result['clips']} independently permuted clip units. {result['excluded_incomplete']} incomplete sessions excluded.\n\n"
    text += f"Spearman rho = {result['rho']:.4f}; two-sided Monte Carlo permutation p = {result['p_two_sided']:.5f} ({result['permutations']} permutations; seed {result['seed']}). {direction}. {decision}\n\n"
    text += f"Participant-bootstrap 95% interval, conditional on this fixed stimulus set: {result['ci_participant_bootstrap']} ({result['valid_bootstraps']} valid resamples).\n\n"
    text += 'This tests the musical encoding of modelled activity. It does not validate the model against real places, establish causation, or generalize to all music or all regions. Musical ratings use adapted soundscape descriptors, not in-situ ISO measurements.\n\n'
    text += '| Clip | Generating score | Mean rated Eventfulness |\n|---|---:|---:|\n'
    text += ''.join(f"| {r['clip_id']} | {r['score']:.2f} | {r['mean_eventfulness']:.4f} |\n" for r in result['clip_means'])
    text += '\n## Input provenance\n\n' + evidence + '\n'
    args.output.write_text(text)
    print(f'Wrote {args.output}')

if __name__ == '__main__':
    main()
