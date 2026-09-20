#!/usr/bin/env python3
"""Fetch attributable Commons photo candidates; never install unreviewed search results."""
import argparse
import concurrent.futures
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.parse
from fetch_landmark_pageviews import request_json

ROOT = Path(__file__).resolve().parent
QUERIES = {
 'Yangnim-dong': '"양림"', '5.18 National Cemetery': '"May 18th National Cemetery"',
 'E-World & Duryu Park': '"Duryu"', 'Ganghwa Dolmen Site': '"Ganghwa" "dolmen"',
 'Kia AutoLand Gwangju': '"Gwangju" "Kia"', '5.18 National Cemetery': '"May 18" "cemetery"',
 'Expo Park & Hanbit Tower': '"Daejeon" "Expo"', 'Taehwagang River Park': '"Taehwa"',
 'Hyundai Motor Ulsan Plant': '"Hyundai" "Ulsan"', 'Hyundai Heavy Industries Shipyard': '"Hyundai" "shipyard"',
 'Geumgang Riverside': '"Geum" "Sejong"', 'Government Complex Sejong': '"Government Complex Sejong"',
 'Suwon Hwaseong Fortress': '"Hwaseong" "fortress"', 'Nami Island': '"Namiseom"',
 'Woljeongsa & Odaesan': '"Woljeongsa"', 'Cheorwon Peace Observatory': '"Cheorwon" "observatory"',
 'SK Hynix Cheongju Campus': '"Hynix" "Cheongju"', 'Hyundai Motor Asan Plant': '"Hyundai" "Asan"',
 'Taean Beach': '"Taean" "beach"', 'Gunsan Modern History Street': '"Gunsan" "history"',
 'Muju Deogyusan Ski Resort': '"Muju" "ski"', 'Boseong Green Tea Fields': '"Boseong" "tea"',
 'Damyang Juknokwon': '"Juknokwon"', 'Gyeongju Historic Area': '"Gyeongju" "historic"',
 'POSCO Pohang Steelworks': '"Pohang" "POSCO"', 'Hanwha Ocean Geoje Shipyard': '"Daewoo" "shipbuilding"',
 'Manjanggul Cave': '"Manjanggul"', 'Donghwasa Temple': '"Donghwasa"',
 'Mudeungsan National Park': '"Mudeungsan"', 'Seoraksan National Park': '"Seoraksan"',
 'Songnisan National Park': '"Songnisan"', 'Naejangsan National Park': '"Naejangsan"',
 'Naganeupseong Folk Village': '"Naganeupseong"', 'Yangdong Folk Village': '"Yangdong"',
 'Yuseong Hot Springs': '"Yuseong" "hot"', 'Samsung Digital City': '"Samsung Digital City"',
}

QUERIES.update({
 '5.18 National Cemetery': 'intitle:cemetery Gwangju',
 'Daedeok Innopolis': 'ETRI Korea', 'Taehwagang River Park': 'Taehwagang',
 'Hyundai Motor Ulsan Plant': 'Hyundai car assembly Ulsan',
 'Samsung Digital City': 'Samsung Suwon headquarters',
 'SK Hynix Cheongju Campus': '하이닉스 청주',
 'Hyundai Motor Asan Plant': '현대자동차 아산공장',
 'POSCO Pohang Steelworks': 'incategory:"Pohang iron and steel works"',
 'Yangdong Folk Village': '"Yangdong Village"',
 'Buyeo': 'incategory:Buyeo -map -bus', 'Danyang': '"Danyang" "Korea"',
 'E-World & Duryu Park': '"Duryu Park"',
 'Nami Island': 'incategory:Namiseom -peacock -peahen -pavo -mallard -goose -ostrich',
 'Jeju City': 'intitle:"Jeju" intitle:"City"',
 'Gunsan Modern History Street': '"Gunsan" "museum"',
})

def clean(value):
    return html.unescape(re.sub('<[^>]+>', '', value or '')).strip()

def collect(place, cache_dir):
    query = QUERIES.get(place['place'], '"' + place['place'].replace('National Park', '').strip() + '"')
    params = dict(action='query', format='json', generator='search', gsrsearch=query + ' filetype:bitmap',
                  gsrnamespace=6, gsrlimit=8, prop='imageinfo', iiprop='url|extmetadata|size', iiurlwidth=320)
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    cache = cache_dir / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    try:
        if cache.exists():
            response = json.loads(cache.read_text())
        else:
            response = request_json(url, 'MoodscapeResearch/1.0 (https://github.com/clairenah19/sound-moodscape)')
            cache.write_text(json.dumps(response, ensure_ascii=False))
        photos = []
        for page in sorted(response.get('query', {}).get('pages', {}).values(), key=lambda x:x.get('index', 999)):
            info = page.get('imageinfo', [{}])[0]
            meta = info.get('extmetadata', {})
            val = lambda k: clean(meta.get(k, {}).get('value', ''))
            license_name = val('LicenseShortName')
            if not license_name or info.get('width', 0) < 500 or not re.search(r'\.(jpe?g|png|webp)$', urllib.parse.urlparse(info.get('url', '')).path, re.I):
                continue
            photos.append(dict(title=page['title'], url=info['url'], thumb=info.get('thumburl', info['url']),
                page=info['descriptionurl'], artist=val('Artist'), license=license_name,
                licenseUrl=val('LicenseUrl'), description=val('ImageDescription'), query=query))
        return {'state': place['state'], 'place': place['place'], 'query': query, 'candidates': photos}
    except Exception as exc:
        return {'state': place['state'], 'place': place['place'], 'query': query, 'candidates': [], 'error': str(exc)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'photo_candidates.json')
    args = parser.parse_args()
    cache_dir = ROOT / 'photo_cache'
    cache_dir.mkdir(exist_ok=True)
    places = [p for p in json.loads((ROOT/'landmark_inventory.json').read_text()) if len(p['photos']) < 2]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda p: collect(p, cache_dir), places))
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    for row in results:
        print(row['place'], len(row['candidates']), row.get('error', ''), flush=True)

if __name__ == '__main__':
    main()
