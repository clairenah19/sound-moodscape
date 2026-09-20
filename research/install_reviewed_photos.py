"""Install the reviewed source list into photos[] entries.

The default remains safe for first installation and refuses existing galleries.
Use --refresh to resync already-installed galleries after reviewed metadata changes.
"""
import csv
import json
import re
import argparse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def matching_end(text, start, opener, closer):
    depth, quote, escaped = 0, None, False
    for pos in range(start, len(text)):
        char = text[pos]
        if quote:
            if escaped: escaped = False
            elif char == '\\': escaped = True
            elif char == quote: quote = None
        elif char in ('"', "'"): quote = char
        elif char == opener: depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0: return pos
    raise ValueError(f'Unclosed {opener} at offset {start}')

def main(refresh=False):
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
        end = matching_end(text, start, '{', '}')
        gallery = [{ 'url': p['thumb'], 'originalUrl': p['url'], 'page': p['page'],
                     'artist': p['artist'], 'license': p['license'],
                     'licenseUrl': p['licenseUrl'], 'caption': p['caption']} for p in photos]
        marker = text.find('photos:', start, end)
        if marker >= 0:
            if not refresh:
                raise ValueError(f'Existing gallery: {name}; use --refresh to sync reviewed metadata')
            array_start = text.find('[', marker, end)
            array_end = matching_end(text, array_start, '[', ']')
            text = text[:array_start] + json.dumps(gallery, ensure_ascii=False) + text[array_end + 1:]
        else:
            text = text[:end].rstrip() + ', photos: ' + json.dumps(gallery, ensure_ascii=False) + ' ' + text[end:]
    (ROOT / 'data.js').write_text(text)
    with (ROOT / 'research/landmark_photo_sources.csv').open('w', newline='') as file:
        keys = ['state','place','url','thumb','page','artist','license','licenseUrl','caption','review']
        writer = csv.DictWriter(file, fieldnames=keys, extrasaction='ignore', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    print(f'Installed {len(rows)} photos for {len(groups)} places')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true', help='replace existing photos[] galleries')
    args = parser.parse_args()
    main(refresh=args.refresh)
