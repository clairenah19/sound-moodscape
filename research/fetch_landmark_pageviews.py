#!/usr/bin/env python3
"""Collect pageviews; retain missing/error rows, never substitute missing counts with zero."""
import argparse
import calendar
import csv
import datetime as dt
import json
import math
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
BASE = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article'
FIELDS = ['state', 'place', 'wikipedia_title', 'article_scope', 'project', 'access', 'agent',
          'start', 'end', 'avg_monthly_views', 'total_views', 'months_covered', 'expected_months',
          'popularity_offset_0_100', 'status', 'retrieved_utc', 'source_url', 'error']

def last_complete_year(today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    end = today.replace(day=1) - dt.timedelta(days=1)
    start = dt.date(end.year - (end.month < 12), end.month % 12 + 1, 1)
    return start, end

def month_keys(start, end):
    out = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        out.append(f'{year:04}{month:02}')
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return out

def request_json(url, user_agent, attempts=3):
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': user_agent})
            with urllib.request.urlopen(req, timeout=25) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
            retry = exc.headers.get('Retry-After', '')
            time.sleep(min(30, int(retry)) if retry.isdigit() else 2 ** attempt)
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)

def summarize(items, expected):
    counts = {}
    for item in items:
        month = str(item['timestamp'])[:6]
        count = item['views']
        if month not in expected or month in counts or not isinstance(count, int) or count < 0:
            raise ValueError('Invalid, duplicate or out-of-period monthly count')
        counts[month] = count
    total = sum(counts.values())
    return total, len(counts), round(total / len(counts), 3) if counts else ''

def scale_rows(rows):
    eligible = [r for r in rows if r['status'] == 'ok']
    if not eligible:
        return
    values = [math.log1p(float(r['avg_monthly_views'])) for r in eligible]
    lo, hi = min(values), max(values)
    for row, value in zip(eligible, values):
        # Constant cohorts have no ranking information; neutral rather than division by zero.
        row['popularity_offset_0_100'] = round(100 * (value - lo) / (hi - lo), 2) if hi > lo else 50.0

def main():
    start_default, end_default = last_complete_year()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=ROOT / 'landmark_inventory.json')
    parser.add_argument('--start', type=dt.date.fromisoformat, default=start_default)
    parser.add_argument('--end', type=dt.date.fromisoformat, default=end_default)
    parser.add_argument('--user-agent', default=os.environ.get('WIKIMEDIA_USER_AGENT',
                        'MoodscapeResearch/1.0 (https://github.com/clairenah19/sound-moodscape)'))
    parser.add_argument('--output', type=Path, default=ROOT / 'moodscape_landmark_pageviews.csv')
    parser.add_argument('--json-output', type=Path, default=ROOT / 'moodscape_landmark_pageviews.json')
    parser.add_argument('--cache-dir', type=Path, default=ROOT / 'pageview_cache')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    if args.start.day != 1 or args.end.day != calendar.monthrange(args.end.year, args.end.month)[1] or args.start > args.end:
        parser.error('Use a first-of-month start and last-of-month end, in chronological order')
    if args.end >= dt.datetime.now(dt.timezone.utc).date().replace(day=1):
        parser.error('Only complete past months are comparable')
    expected = month_keys(args.start, args.end)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    overrides_path = ROOT / 'landmark_wikipedia_overrides.json'
    overrides = json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    rows = []
    for place in json.loads(args.inventory.read_text()):
        row = dict.fromkeys(FIELDS, '')
        row.update(state=place['state'], place=place['place'], project='en.wikipedia.org',
                   access='all-access', agent='user', start=str(args.start), end=str(args.end),
                   expected_months=len(expected), status='no_wikipedia_article')
        override = overrides.get(place['state'] + '__' + place['place'], {})
        url = urllib.parse.urlparse(place.get('photoPage', ''))
        title = override.get('title') or (urllib.parse.unquote(url.path[6:]) if url.hostname == 'en.wikipedia.org' and url.path.startswith('/wiki/') else '')
        row['article_scope'] = override.get('scope', 'linked article; may describe a wider area')
        if title:
            row['wikipedia_title'] = title
            article = urllib.parse.quote(title.replace(' ', '_'), safe='')
            endpoint = f'{BASE}/en.wikipedia.org/all-access/user/{article}/monthly/{args.start:%Y%m%d}00/{args.end:%Y%m%d}00'
            row['source_url'] = endpoint
            import hashlib
            cache = args.cache_dir / (hashlib.sha256(endpoint.encode()).hexdigest() + '.json')
            try:
                if cache.exists() and not args.refresh:
                    record = json.loads(cache.read_text())
                else:
                    payload = request_json(endpoint, args.user_agent)
                    record = {'retrieved_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'payload': payload}
                    cache.write_text(json.dumps(record, ensure_ascii=False))
                    time.sleep(0.12)
                total, months, avg = summarize(record['payload']['items'], expected)
                row.update(total_views=total, months_covered=months, avg_monthly_views=avg,
                           status='ok' if months == len(expected) else 'partial', retrieved_utc=record['retrieved_utc'])
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
                row.update(status='error', error=str(exc)[:250], retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        rows.append(row)
        print(f"{row['state']} / {row['place']}: {row['status']}", flush=True)
    scale_rows(rows)
    with args.output.open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    args.json_output.write_text(json.dumps({'method': 'log1p-minmax-complete-months-v1',
        'interpretation': 'Wikipedia readership popularity proxy, not soundscape measurement; does not alter audio or mood scores',
        'rows': rows}, ensure_ascii=False, indent=2) + '\n')
    print(f"Saved {len(rows)} rows; {sum(r['status'] == 'ok' for r in rows)} complete. Missing/partial/error rows have no offset.")

if __name__ == '__main__':
    main()
