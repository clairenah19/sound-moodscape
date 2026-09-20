"""Install the reviewed source list into previously empty photos[] entries.
Run once from the project root. Existing galleries are never overwritten.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    rows = json.loads((ROOT / 'research/photo_selection.json').read_text())
    groups = defaultdict(list)
    for row in rows:
        if not row.get('review', '').startswith('Source metadata and preview visually reviewed'):
            raise ValueError('Unreviewed photo')
        groups[row['place']].append(row)
    text = (ROOT / 'data.js').read_text()
    for name, photos in groups.items():
        if len(photos) != 2 or len({p['url'] for p in photos}) != 2:
            raise ValueError(f'Two distinct photos required: {name}')
        matches = list(re.finditer(r'\{ name: ' + re.escape(json.dumps(name)), text))
        if len(matches) != 1:
            raise ValueError(f'Ambiguous place: {name}')
        start = matches[0].start()
        depth, quote, escaped = 0, None, False
        for end in range(start, len(text)):
            char = text[end]
            if quote:
                if escaped: escaped = False
                elif char == '\\': escaped = True
                elif char == quote: quote = None
            elif char in ('"', "'"): quote = char
            elif char == '{': depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0: break
        if 'photos:' in text[start:end]:
            raise ValueError(f'Existing gallery: {name}; installation is already applied')
        gallery = [{ 'url': p['thumb'], 'originalUrl': p['url'], 'page': p['page'],
                     'artist': p['artist'], 'license': p['license'],
                     'licenseUrl': p['licenseUrl'], 'caption': p['caption']} for p in photos]
        text = text[:end].rstrip() + ', photos: ' + json.dumps(gallery, ensure_ascii=False) + ' ' + text[end:]
    (ROOT / 'data.js').write_text(text)
    with (ROOT / 'research/landmark_photo_sources.csv').open('w', newline='') as file:
        keys = ['state','place','url','thumb','page','artist','license','licenseUrl','caption','review']
        writer = csv.DictWriter(file, fieldnames=keys, extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
    print(f'Installed {len(rows)} photos for {len(groups)} places')

if __name__ == '__main__': main()
