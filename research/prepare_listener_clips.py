#!/usr/bin/env python3
"""Install reviewed Suno clips after all metadata is supplied. Requires FFmpeg/ffprobe."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, default=ROOT/'listener_stimulus_metadata.csv')
    args = parser.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        parser.error('Install FFmpeg and ffprobe before preparing real clips')
    manifest_path = ROOT/'listener_stimuli.json'
    config = json.loads(manifest_path.read_text())
    if config['ready']:
        parser.error('This stimulus version is already frozen; create a new version before replacing clips')
    with args.metadata.open(newline='') as src:
        rows = {r['clip_id']:r for r in csv.DictReader(src)}
    if set(rows) != {c['id'] for c in config['clips']}:
        parser.error('Metadata must match every clip')
    for row in rows.values():
        if not row['source_track'] or not Path(row['source_track']).is_file():
            parser.error(f"Missing real source track for {row['clip_id']}")
        if 'Suno' not in row['source_provenance'] or 'PENDING' in row['source_provenance'] or not row['key_review'] or 'PENDING' in row['key_review']:
            parser.error('Document Suno provenance and a human mode review for every track first')
    # Stage all outputs before marking any stimulus set ready.
    with tempfile.TemporaryDirectory() as temp:
        for clip in config['clips']:
            row = rows[clip['id']]
            command = ['ffmpeg','-hide_banner','-nostdin','-y','-ss','5','-i',row['source_track'],'-t','25']
            first = subprocess.run(command + ['-af','loudnorm=I=-18:TP=-1:LRA=11:print_format=json','-f','null','-'], capture_output=True, text=True, check=True)
            matches = re.findall(r'\{\s*"input_i"[\s\S]*?\}', first.stderr)
            if not matches:
                raise ValueError('No loudness measurement returned')
            measured = json.loads(matches[-1])
            if any(v in ('-inf','inf','nan') for v in measured.values()):
                raise ValueError('Silent or invalid audio cannot be a study stimulus')
            filt = ('loudnorm=I=-18:TP=-1:LRA=11:linear=true:'
                f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
                f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}")
            output = Path(temp)/(clip['id']+'.mp3')
            subprocess.run(command + ['-af',filt,'-map_metadata','-1','-vn','-ar','44100','-ac','2','-codec:a','libmp3lame','-q:a','2',str(output)],capture_output=True,check=True)
            duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(output)]))
            if not 24.9 <= duration <= 25.2:
                raise ValueError(f'{clip["id"]}: source is too short for the fixed 5–30 second window')
            clip['sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
        for clip in config['clips']:
            destination = ROOT/clip['src']
            destination.parent.mkdir(exist_ok=True)
            shutil.copyfile(Path(temp)/(clip['id']+'.mp3'), destination)
    config['ready'] = True
    manifest_path.write_text(json.dumps(config, indent=2)+'\n')
    print('All clips installed and hashed. Perform a technical dry run before recruitment.')

if __name__ == '__main__':
    main()
