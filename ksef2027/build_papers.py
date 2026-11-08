#!/usr/bin/env python3
"""Build the KSEF 2027 National (Korean) and International (English) research papers.

Both papers are written into the official KSEF paper template (붙임3 논문양식.docx) and exported to PDF
with Apple Pages. Numbers come from research/paper/stats.json and the audio-measurement CSVs, which the
existing analysis scripts produce; nothing here is typed in by hand except wording.

Run from the repository root:
    python3 ksef2027/build_papers.py [--template PATH] [--no-pdf]
Needs python-docx (and pypdf to report page counts).
"""
import argparse
import csv
import json
from pathlib import Path

from docx import Document
from docx.shared import Cm

from docx_tools import (DOTUM, MYEONGJO, academic_table, add_runs, clear, export_pdf_with_pages, fmt, remove,
                        set_font)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RES = ROOT / 'research'
FIG = RES / 'paper' / 'figures'
S = json.loads((RES / 'paper' / 'stats.json').read_text())
DEFAULT_TEMPLATE = Path('/Users/claireyunhanah/Downloads/[KSEF 2027] National(국내분야)/붙임3. KSEF National(국내분야) 논문양식.docx')

TAG = 'ksef2027-submission'
REPO = 'https://github.com/clairenah19/sound-moodscape'
BLOB = f'{REPO}/blob/{TAG}/'
TREE = f'{REPO}/tree/{TAG}/'
DEMO = 'https://clairenah19.github.io/sound-moodscape/'


def rows(name):
    with (RES / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


R1, R2 = rows('audio_analysis_results_octave_aware.csv'), rows('audio_analysis_results_v2_octave_aware.csv')
META = {r['clip_id']: r for r in rows('listener_stimulus_metadata.csv')}
r1, r2 = S['round1'], S['round2']
T1, T2 = S['tempo_diag']['round1'], S['tempo_diag']['round2']
PV, POP, KR, PF, MCL, MCG = S['place_variance'], S['popularity'], S['key_rules'], S['prompt_features'], S['mc_local'], S['mc_global']
ref = S['reference_check']
pct = lambda x: f'{100 * x:.1f}%'
f2 = lambda x: f'{x:.2f}'
ci = lambda c: f'{100 * c[0]:.0f}–{100 * c[1]:.0f}%'
n_pleas = KR['Regional Pleasantness default']['major key'] + KR['Regional Pleasantness default']['minor key']
key = lambda k: k.replace('#', '♯')

# Sejong perceptual-tempo diagnostic (one informal listener; values from the project's report and the
# correction record research/listener_clips/clip07_sejong_retimed_hihat_fixed.json)
TFV = json.loads((RES / 'listener_clips' / 'clip07_sejong_retimed_hihat_fixed.json').read_text())
HV = TFV['human_validation']


def clip_rows(lang):
    out = []
    for a, b in zip(R1, R2):
        m = META[a['clip_id']]
        name = a['place']
        asked = a['requested_mode'] if a['requested_mode'] == b['requested_mode'] else f"{a['requested_mode']}→{b['requested_mode']}"
        if lang == 'ko':
            asked = asked.replace('major', '장조').replace('minor', '단조')
        mark = lambda r: '✓' if r['mode_match'] == 'True' else '✗'
        out.append([a['clip_id'][-2:], name, f"{float(m['activity_score_0_100']):.0f}", f"{float(a['requested_bpm']):.0f}",
                    f"{float(a['detected_bpm']):.0f}", f"{float(b['detected_bpm']):.0f}", asked,
                    f"{key(a['detected_key'])} {mark(a)}", f"{key(b['detected_key'])} {mark(b)}"])
    return out


# ---------------------------------------------------------------------------------------------- references
# Citation order. Authors written given-name first, as the template requires. Journal entries were checked
# against their Crossref records on 2026-11-08.
REFS = [
    dict(ko='International Organization for Standardization, ISO 12913-1:2014 Acoustics — Soundscape — Part 1: Definition and conceptual framework, ISO, 2014.',
         en='International Organization for Standardization, ISO 12913-1:2014 Acoustics — Soundscape — Part 1: Definition and conceptual framework, ISO, 2014.'),
    dict(ko='International Organization for Standardization, ISO/TS 12913-2:2018 Acoustics — Soundscape — Part 2: Data collection and reporting requirements, ISO, 2018.',
         en='International Organization for Standardization, ISO/TS 12913-2:2018 Acoustics — Soundscape — Part 2: Data collection and reporting requirements, ISO, 2018.'),
    dict(ko='International Organization for Standardization, ISO/TS 12913-3:2019 Acoustics — Soundscape — Part 3: Data analysis, ISO, 2019.',
         en='International Organization for Standardization, ISO/TS 12913-3:2019 Acoustics — Soundscape — Part 3: Data analysis, ISO, 2019.'),
    dict(ko='Östen Axelsson, Mats E. Nilsson, Birgitta Berglund, A principal components model of soundscape perception, The Journal of the Acoustical Society of America, 128, 5, 2836–2846, 2010. doi:10.1121/1.3493436'),
    dict(ko='Tin Oberman, Arianna Latini, Francesco Aletta, Giacomo Gozzi, Jian Kang, Simone Torresin, Human sounds and associated tonality disrupting perceived soundscapes in protected natural areas, Scientific Reports, 15, 1, 28759, 2025. doi:10.1038/s41598-025-08524-y'),
    dict(ko='Haixia Zhao, Catherine Plaisant, Ben Shneiderman, Jonathan Lazar, Data sonification for users with visual impairment: a case study with georeferenced data, ACM Transactions on Computer-Human Interaction, 15, 1, 1–28, 2008. doi:10.1145/1352782.1352786'),
    dict(ko='통계청, 국가지표체계: 인구밀도, 통계청, 2025, ', en='Statistics Korea, e-National Indicators: Population density, Statistics Korea, 2025, ',
         url='https://www.index.go.kr/unity/potal/eNara/sub/showStblGams3.do?freq=Y&idx_cd=1007&period=N&stts_cd=100701', when=('2026년 9월 인용', 'accessed Sep 2026')),
    dict(ko='한국관광공사, 2024 국민여행조사(표 19-2-1, 19-14-1, 20-2-1, 21-2-1), 한국관광 데이터랩, 2025, ', en='Korea Tourism Organization, 2024 National Travel Survey (tables 19-2-1, 19-14-1, 20-2-1, 21-2-1), Korea Tourism Data Lab, 2025, ',
         url='https://datalab.visitkorea.or.kr/site/portal/ex/bbs/View.do?bcIdx=309282&cbIdx=1127', when=('2026년 9월 인용', 'accessed Sep 2026')),
    dict(ko='환경부, 2023 소음·진동 민원 및 배출시설 현황, 환경부, 2024, ', en='Ministry of Environment (Korea), 2023 noise and vibration complaints and regulated emission facilities, Ministry of Environment, 2024, ',
         url='https://me.go.kr', when=('2026년 9월 인용', 'accessed Sep 2026')),
    dict(ko='Joo Young Hong, Jin Yong Jeon, Comparing associations among sound sources, human behaviors, and soundscapes on central business and commercial streets in Seoul, Korea, Building and Environment, 186, 107327, 2020. doi:10.1016/j.buildenv.2020.107327'),
    dict(ko='Wikimedia Foundation, Analytics API: page views, Wikimedia Foundation, 2026, ', en='Wikimedia Foundation, Analytics API: page views, Wikimedia Foundation, 2026, ',
         url='https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html', when=('2026년 9월 인용', 'accessed Sep 2026')),
    dict(ko='Brian McFee, Colin Raffel, Dawen Liang, Daniel Ellis, Matt McVicar, Eric Battenberg, Oriol Nieto, librosa: Audio and Music Signal Analysis in Python, Proceedings of the 14th Python in Science Conference, 18–24, 2015. doi:10.25080/Majora-7b98e3ed-003'),
    dict(ko='Carol L. Krumhansl, Edward J. Kessler, Tracing the dynamic changes in perceived tonal organization in a spatial representation of musical keys, Psychological Review, 89, 4, 334–368, 1982. doi:10.1037/0033-295X.89.4.334'),
    dict(ko='C. J. Clopper, E. S. Pearson, The use of confidence or fiducial limits illustrated in the case of the binomial, Biometrika, 26, 4, 404–413, 1934. doi:10.1093/biomet/26.4.404'),
    dict(ko='Patrick E. Shrout, Joseph L. Fleiss, Intraclass correlations: Uses in assessing rater reliability, Psychological Bulletin, 86, 2, 420–428, 1979. doi:10.1037/0033-2909.86.2.420'),
    dict(ko='Lawrence I-Kuei Lin, A concordance correlation coefficient to evaluate reproducibility, Biometrics, 45, 1, 255–268, 1989. doi:10.2307/2532051'),
    dict(ko='Moodscape 프로젝트, 소스 코드·데이터·분석 스크립트, GitHub, 2026, ', en='Moodscape project, Source code, data and analysis scripts, GitHub, 2026, ',
         url=TREE, when=('2026년 11월 인용', 'accessed Nov 2026')),
    dict(ko='Moodscape 프로젝트, 웹 데모, GitHub Pages, 2026, ', en='Moodscape project, Web demo, GitHub Pages, 2026, ',
         url=DEMO, when=('2026년 11월 인용', 'accessed Nov 2026')),
    dict(ko='Moodscape 프로젝트, 생성 음원(1차 clip01–10, 2차 v2_clip01–10, 후속 생성), GitHub, 2026, ', en='Moodscape project, Generated audio (round 1 clip01–10, round 2 v2_clip01–10, follow-ups), GitHub, 2026, ',
         url=TREE + 'research/listener_clips', when=('2026년 11월 인용', 'accessed Nov 2026')),
    dict(ko='Moodscape 프로젝트, 세종 클립 템포 보정 전 원본(사람 탭 48 BPM), GitHub, 2026, ', en='Moodscape project, Sejong clip before tempo correction (tapped at 48 BPM), GitHub, 2026, ',
         url=BLOB + 'research/listener_clips/clip07_sejong_perceived95_candidate2.mp3', when=('2026년 11월 인용', 'accessed Nov 2026')),
    dict(ko='Moodscape 프로젝트, 세종 클립 템포 보정 후 25초 청취 파일(사람 탭 96 BPM), GitHub, 2026, ', en='Moodscape project, Sejong clip after tempo correction, 25-s listening file (tapped at 96 BPM), GitHub, 2026, ',
         url=BLOB + 'research/listener_clips/clip07_hihat_fixed_blind_test.wav', when=('2026년 11월 인용', 'accessed Nov 2026')),
    dict(ko='Moodscape 프로젝트, 강남 장르어 교체 생성 3회(단조 3/3), GitHub, 2026, ', en='Moodscape project, Gangnam genre-swap generations, 3 runs (minor 3/3), GitHub, 2026, ',
         url=BLOB + 'research/listener_clips/clip09_genre_swap_test.mp3', when=('2026년 11월 인용', 'accessed Nov 2026')),
]


# ---------------------------------------------------------------------------------------------- content
def P(*parts):
    return ('p', list(parts))


def B(*parts):
    return ('b', list(parts))


def content_ko():
    c = []
    c += [('h1', '1. 서론'), ('h2', '1.1 문제 인식')]
    c += [P('지도는 장소의 차이를 색과 글자로 전달한다. 그래서 화면을 볼 수 없는 사람에게는 어느 지역이 붐비고 어느 지역이 한적한지가 전달되지 않는다. 소리는 같은 정보를 다른 감각으로 전할 수 있는 후보이며, 지리 데이터를 소리로 바꾸어 시각장애인의 탐색을 돕는 선행 사례가 있다[6]. 그러나 소리로 바꾸는 순간 또 하나의 문제가 생긴다. 사운드스케이프 연구는 소리 환경을 “사람이 맥락 속에서 지각한 음향 환경”으로 정의하고[1], 설문과 측정으로 쾌적성(Pleasantness)과 사건성(Eventfulness)이라는 두 축을 평가한다[2–4]. Oberman 등은 보호 자연지역 28개 지점에서 443부의 설문을 수집하여, 음압 수준 하나보다 지각된 음원 우세도와 심리음향 지표가 장소의 지각을 더 잘 설명함을 보였다[5]. 즉 하나의 숫자로 계산한 “분위기”가 실제 장소나 실제 청취 경험과 일치한다고 가정할 수 없다.')]
    c += [P('본 연구는 이 두 문제에서 출발하였다. 첫째, 공식 통계로 장소의 성격을 음악으로 표현하는 도구가 필요하다. 둘째, 그 도구는 데이터 → 점수 → 음악 사양 → 생성 음원 → 지각으로 이어지는 사슬이며, 각 연결은 따로 실패할 수 있으므로 하나씩 검증되어야 한다.')]
    c += [('h2', '1.2 연구 목적과 연구 질문')]
    c += [P('연구 목적은 (1) 공식 지역 통계를 음악 사양으로 바꾸는 재현 가능한 웹 프로토타입 Moodscape를 개발하고, (2) 사슬의 각 연결을 독립된 연구 질문(RQ)으로 검증하여 어느 연결이 강하고 어느 연결이 약한지 밝히며, (3) 그 결과로 개선 방향을 제시하는 것이다. 연구 질문은 다음과 같다.')]
    for t in ['RQ1. 공식 통계가 어떻게 지역 활동 점수가 되며, 그 순위는 가정(가중치)이 바뀌어도 안정적인가?',
              'RQ2. 지역 값이 어떻게 장소(랜드마크) 점수가 되는가?',
              'RQ3. 점수가 어떻게 템포·조성·스타일의 음악 사양이 되며, 어떤 규칙이 각 선택을 결정하는가?',
              'RQ4. 사양이 실제 생성 음원에 반영되는가? 반영을 바꾸는 요인은 무엇인가?',
              'RQ5. AI 구성요소(Gemini 스타일 예측, 생성 요청 형식)는 사양을 어떻게 바꾸는가?',
              'RQ6–RQ8. 청취자 지각, 실제 장소의 지각, 시각장애 사용자의 접근성(프로토콜 준비, 데이터 미수집).']:
        c.append(B(t))

    c += [('h1', '2. 아이디어와 시스템 개발')]
    c += [('h2', '2.1 아이디어: 데이터에서 소리까지의 사슬')]
    c += [P('핵심 아이디어는 지역의 “활발함”을 템포와 음높이로, 방문객 만족을 장조/단조로 옮기는 것이다. 그림 1은 구현한 사슬과 각 연결을 검증하는 연구 질문을 보여준다. 웹 앱은 정적 HTML/JavaScript와 D3 지도로 만들었으며, 17개 시·도와 75개 장소마다 점수, 음악 사양, 사진, 설명, 생성 음원을 보여준다[17][18].')]
    c += [('fig', FIG / 'fig1_chain.png', 15.5, '검증한 사슬(그림 내 라벨은 영문). 각 상자는 하나의 연결이며 위에 이를 검증하는 연구 질문을 표시하였다. 초록: 프로젝트 데이터로 계산, 주황: 생성 음원 측정 또는 수작업 모의, 회색: 데이터 미수집.')]
    c += [('h2', '2.2 데이터와 점수 (RQ1, RQ2)')]
    c += [P('17개 시·도에 대해 공식 지표 9종을 사용하였다. 2025년 인구와 인구밀도(통계청[7]), 2024년 국내 관광 횟수와 방문객 설문 4종(전반 만족, 추천 의향, 재방문 의향, 혼잡 만족; 국민여행조사[8]), 2023년 소음·진동 민원과 소음 배출시설 수(환경부[9])이다. 모든 값은 원 출처 링크와 함께 수기로 옮겨 적었고 자동 수집(스크래핑)은 사용하지 않았다. 활동 성분 5개(인구밀도, 1인당 관광 횟수, 인구 10만 명당 민원, 10만 명당 배출시설, 혼잡 압력 = 100 − 혼잡 만족)를 log1p 변환 후 17개 지역 안에서 0–1로 최소–최대 정규화하여 다음과 같이 합성하였다.')]
    c += [('eq', '활동 프록시 = 100 × (0.35 인구밀도 + 0.30 관광 + 0.15 민원 + 0.10 배출시설 + 0.10 혼잡 압력)')]
    c += [('eq', '방문객 쾌적성 = 0.40 전반 만족 + 0.25 추천 + 0.20 재방문 + 0.15 혼잡 만족')]
    c += [P('가중치는 실험으로 맞춘 계수가 아니라 명시한 설계 가설이다. 활동 프록시는 ISO 12913의 사건성 좌표가 아니며, 이를 실제 지각과 비교하는 현장 검증(RQ7)을 별도로 설계하였다. 장소 점수는 지역 활동 프록시에 연구자가 정한 장소별 오프셋을 더해 [0, 1]로 자른 값이며, 앱에서 “예시(illustrative)”로 표시하였다.')]
    c += [('h2', '2.3 점수에서 음악 사양으로 (RQ3)')]
    c += [P(f'템포는 round(42 + 110 × 점수) BPM으로 정하여 75개 장소가 {S["spec"]["bpm_min"]}–{S["spec"]["bpm_max"]} BPM에 분포한다. 음높이는 A4(440 Hz)에서 round(12 × 점수) 반음 위로 정한다. 조성은 세 규칙을 순서대로 적용한다. ① 추모·묘지·전망대·동굴 등 엄숙한 장소는 단조, ② 한옥·사찰·궁궐·공원·해변·행정기관 등 전통·자연 장소는 장조, ③ 나머지는 지역 방문객 쾌적성이 17개 지역 중앙값({S["pleasantness_median"]:.2f}) 이상이면 장조, 미만이면 단조이다. 장르·분위기 단어는 장소 유형과 점수 구간으로 고르며, 이를 장면 문장, 조성 문장, 템포, 악기, 보컬 지시와 합쳐 하나의 생성 요청문을 만든다. 예를 들어 강남(단조, 115 BPM)의 요청문은 “Music for a glittering high-rise district … In a minor key (around F) — melancholic, somber, shadowed tonality … lo-fi hip-hop, relaxing city-pop synth pads, urban beat, around 115 BPM …”이다.')]
    c += [('h2', '2.4 생성, AI 구성요소, 접근성 인터페이스')]
    c += [P('음원은 sunoapi.org를 통해 Suno V4_5 모델로 생성한다. Gemini(gemini-3.5-flash-lite)는 장소 사진과 설명으로 장르·악기·분위기를 제안하는 기능에 쓰이며, 템포·조성·근음·보컬은 데이터 매핑이 고정값으로 넘겨 AI가 바꿀 수 없도록 설계하였다. 시각 정보 없이 탐색할 수 있도록 17개 지역은 키보드로 이동 가능하고, 화면낭독기용 라벨이 점수와 근거를 읽어 주며, 초점이 옮겨질 때 점수를 음높이로, 동서 위치를 좌우 스테레오로 재생하고, 화살표 키로 가장 가까운 지역으로 이동한다.')]
    c += [('fig', HERE / 'figures' / 'app_map.png', 15.0, '개발한 웹 앱의 첫 화면(현재 개발 브랜치). 지역 색은 활동 점수(파랑: 한적, 빨강: 활발)이며, 지역을 고르면 장소별 점수, 음악 사양, 사진, 생성 음원이 열린다. 오른쪽 안내문은 음원이 MP3 또는 사용자의 Suno 키를 필요로 하고 점수의 가중치가 가설임을 명시한다.')]

    c += [('h1', '3. 검증 방법')]
    c += [P('사슬의 연결마다 증거 등급을 구분하였다. 계산(프로젝트 데이터와 코드로 산출), 측정(생성 음원을 소프트웨어로 분석), 수작업 모의(연구자가 함수의 지시를 손으로 따름, 실제 모델 출력 아님), 미수집(데이터 없음)이다. 모든 통계는 저장소의 분석 스크립트로 다시 계산되며 난수 시드는 20260920으로 고정하였다[17].')]
    c += [B([('RQ1 가중치 민감도. ', {'bold': True}), '각 성분과 최종 점수의 스피어먼 순위상관, 성분 하나를 뺀 순위의 일치도, 그리고 명시 가중치 중심의 디리클레 분포(집중도 20)와 균등 디리클레 분포에서 각각 10,000개 가중치를 뽑아 순위가 얼마나 유지되는지 계산하였다. 공개 연구값이 있는 두 지역(서울[10], 대전)과 순서를 비교하였다.'])]
    c += [B([('RQ2 분산 분해. ', {'bold': True}), '75개 장소 점수를 지역으로 나눈 일원 분석에서 η²와 ICC(1)을 구하였다. 위키백과 영문 조회수(2025.9–2026.8, 12개월)[11]의 로그 지수와 장소 점수의 상관을 순열검정으로 보았다.'])]
    c += [B([('RQ4 생성 음원 측정. ', {'bold': True}), '75개 점수의 순위 분위수에서 10개 장소를 고르고(단조 사례를 넣기 위해 강남 포함) 두 차례 생성하였다. 1차는 원래 요청문과 단일 텍스트 요청 형식, 2차는 개정 요청문과 Suno의 사용자 지정(custom) 형식이다. 음원은 librosa 1.0.0[12]으로 분석하였다. 조성은 크로마 벡터와 Krumhansl–Kessler 조성 프로파일[13]의 상관이 가장 큰 조를 고르고 그 상관을 “조성 적합도”로 보고한다(정답 확률이 아님). 템포는 단일 추정값과, 템포그램 자기상관의 상위 3개 피크 중 하나가 요청 템포의 ±5% 안에 있는지를 함께 보았다. 후자의 우연 기대값은 요청값을 클립 사이에서 20,000번 섞어 구하였다. 비율의 구간은 Clopper–Pearson[14], 2×2 비교는 Fisher 정확검정을 썼다.'])]
    c += [B([('변인. ', {'bold': True}), '독립변인은 요청문 문구(조성 문장의 위치와 표현), 요청 형식(단일 텍스트 대 사용자 지정), 장르 단어이고, 종속변인은 측정된 조성과 템포이다. 생성 모델(V4_5), 분석 절차, 분석 버전은 고정하였다. 같은 요청도 매번 다른 음원이 나오므로(확률적 생성), 한 번의 성공을 개선으로 보지 않았다.'])]
    c += [B([('사람의 박 확인. ', {'bold': True}), '세종 클립 하나에 대해 연구자 외 1인이 이름과 목표를 모르는 상태에서 25초 파일의 주 박을 탭하였다. 이것은 한 사람, 한 클립의 공학적 진단이며 청취자 실험(RQ6)이 아니다.'])]

    c += [('h1', '4. 결과')]
    c += [('h2', '4.1 RQ1: 지역 순위는 그럴듯하지만 가중치에 민감하다')]
    c += [P(f'활동 프록시는 32.9–61.3에 분포하였고 서울·부산·제주가 가장 높고 광주가 가장 낮았다. 방문객 쾌적성은 {S["pleasantness_band"][0]:.1f}–{S["pleasantness_band"][1]:.1f}의 좁은 범위였다. 그러나 표 1과 같이 성분의 실제 영향은 명시 가중치와 달랐다. 0.30의 가중치를 받은 관광 성분은 최종 점수와 순위상관이 거의 없었고(ρ = {S["component_vs_activity_rho"]["tourism"]:.2f}), 인구밀도를 빼면 순위 일치가 ρ = {S["drop_one_rho"]["density"]:.2f}로 떨어졌다. 명시 가중치 근처로 교란한 경우 순위 일치의 중앙값은 ρ = {MCL["rho_median"]:.2f}였지만 하위 5%는 {MCL["rho_p5"]:.2f}였고, ρ ≥ 0.9를 유지한 비율은 {pct(MCL["share_rho_ge_90"])}에 그쳤다(그림 2). 공개 연구값이 있는 두 지역은 모델(서울 {ref["seoul_activity"]:.1f}, 1위; 대전 {ref["daejeon_activity"]:.1f}, {ref["daejeon_rank"]}위)과 공개 사건성(78, 45)의 순서가 같았으나, 두 점은 모순을 보여줄 수는 있어도 모델을 검증하지는 못한다.')]
    comp = [('인구밀도', 'density', 0.35), ('1인당 관광 횟수', 'tourism', 0.30), ('10만 명당 민원', 'complaints', 0.15),
            ('10만 명당 배출시설', 'facilities', 0.10), ('혼잡 압력', 'crowding', 0.10)]
    c += [('table', '활동 프록시 성분의 명시 가중치와 실제 영향(17개 지역). ρ(성분)은 정규화한 성분과 최종 점수의 스피어먼 상관, ρ(제외)는 그 성분을 빼고 다시 계산한 순위와 원래 순위의 일치도이다.',
           ['성분', '가중치', 'ρ(성분)', 'ρ(제외)'],
           [[n, f'{w:.2f}', f2(S['component_vs_activity_rho'][k]), f2(S['drop_one_rho'][k])] for n, k, w in comp],
           [6, 2.4, 2.4, 2.4], None)]
    c += [('fig', FIG / 'fig3_sensitivity.png', 15.5, '가중치 민감도(그림 내 라벨은 영문). (a) 명시 가중치에서의 지역 순위(점)와 교란 가중치 10,000개에서의 95% 범위(막대). (b) 교란 순위와 명시 순위의 스피어먼 ρ 분포. 파랑: 명시값 근처, 주황: 임의 가중치. 점선: ρ = 0.9.')]
    c += [('h2', '4.2 RQ2: 장소의 소리는 대부분 연구자가 정한 오프셋에서 온다')]
    c += [P(f'장소 점수 분산 중 지역이 설명한 비율은 {pct(PV["eta_sq"])}(η²)였고 ICC(1)은 0과 구별되지 않았다. 장소 오프셋의 표준편차(0.21)가 지역 점수의 표준편차(0.08)보다 훨씬 컸다. 따라서 장소 단위의 소리는 공식 통계보다 연구자의 판단을 더 많이 반영하며, 앱은 이를 “예시 점수”로 표시한다. 위키백과 조회 지수는 {POP["n_complete"]}개 장소에서 장소 점수와 약한 양의 관계를 보였으나(ρ = {POP["rho"]:.2f}, 순열 p = {POP["p_perm"]:.3f}) 5% 수준에서 0과 구별되지 않았다. 조회수는 온라인 관심이지 유동인구나 소음이 아니므로 음악에는 반영하지 않았다.')]
    c += [('h2', '4.3 RQ3: 방문객 쾌적성이 조성을 정하는 장소는 절반 이하이다')]
    c += [P(f'75개 장소 중 40곳({pct(40 / 75)})은 엄숙 규칙이나 전통·자연 규칙이 조성을 정하였고, 방문객 쾌적성 규칙이 정한 곳은 {n_pleas}곳({pct(n_pleas / 75)})이었다(표 2). 단조를 요청하는 장소는 {S["n_minor"]}곳이다. 쾌적성 값은 17개 지역이 6.7점 범위에 몰려 있고 {S["n_regions_within1_of_median"]}개 지역이 중앙값에서 1점 이내이므로, 작은 설문 차이가 장조/단조라는 범주적 차이로 바뀐다. 또 쾌적성은 지역 값이라서 같은 지역의 기본 규칙 장소(예: 홍대, 강남, N서울타워)는 모두 같은 이유로 단조가 된다.')]
    c += [('table', '조성을 결정한 규칙(현재 코드, 75개 장소). 규칙은 위에서부터 적용된다.',
           ['결정 규칙', '장조', '단조', '장소 수'],
           [['엄숙 규칙(추모, 묘지, 전망대, 동굴 등)', 0, KR['Solemn override']['minor key'], KR['Solemn override']['minor key']],
            ['전통·자연 규칙(한옥, 사찰, 궁궐, 공원, 해변, 행정기관 등)', KR['Traditional/nature override']['major key'], 0, KR['Traditional/nature override']['major key']],
            ['지역 방문객 쾌적성(17개 지역 중앙값 기준)', KR['Regional Pleasantness default']['major key'], KR['Regional Pleasantness default']['minor key'], n_pleas],
            ['합계', 75 - S['n_minor'], S['n_minor'], 75]],
           [8.6, 1.8, 1.8, 2], None)]
    c += [('h2', '4.4 RQ4: 생성 음원은 요청을 부분적으로만 따른다')]
    c += [P(f'1차에서 요청 조성은 10개 중 {r1["mode_hits"]}개에서 검출되었다(95% 구간 {ci(r1["mode_ci"])}). 장조 요청은 {r1["major_hits"]}/{r1["major_n"]}, 단조 요청은 {r1["minor_hits"]}/{r1["minor_n"]}이었다. 2차에서는 {r2["mode_hits"]}/10(구간 {ci(r2["mode_ci"])})이었으나 단조 요청은 여전히 {r2["minor_hits"]}/{r2["minor_n"]}이었다(표 3, 그림 3). 2차의 향상은 세종이 사실 정정으로 장조 요청으로 바뀐 영향을 포함하고, 요청이 바뀌지 않은 클립 05·06·08도 결과가 뒤바뀌었으므로(생성의 무작위성), 향상의 원인을 문구 수정으로 돌릴 수 없다. 강남의 오검출(A♯ 장조)은 조성 적합도 0.92로, 검출기가 망설인 결과가 아니었다.')]
    c += [('table', '10개 장소의 요청과 측정값. 측정 BPM은 librosa 단일 추정값, ✓는 요청 조성 검출, ✗는 반대 조성이다. 세종(07)은 1차에서 단조, 2차에서 장조를 요청하였다.',
           ['클립', '장소', '점수', '요청 BPM', '1차 BPM', '2차 BPM', '요청 조성', '1차 조성', '2차 조성'],
           clip_rows('ko'), [0.9, 4.4, 1.0, 1.3, 1.2, 1.2, 1.7, 1.9, 1.9], ['center', 'left'] + ['center'] * 7)]
    c += [('fig', FIG / 'fig7_audio_fidelity.png', 14.5, '사양 대비 생성 음원(그림 내 라벨은 영문). (a) 요청 대 측정 템포, 1차(채움)와 2차(빈 원). 실선은 일치, 파선·점선은 2배·절반 템포. 마름모는 측정값의 절반 또는 2배 환산값으로, 같은 숫자를 다르게 읽은 것일 뿐 음원은 바뀌지 않는다. (b) 클립별 검출 조성과 조성 적합도. 파랑: 요청 조성, 주황: 반대 조성.')]
    c += [P(f'템포는 단일 추정값으로 보면 거의 따르지 않았다. 요청과 측정의 순위상관은 1차 ρ = {r1["rho"]:.2f}, 2차 ρ = {r2["rho"]:.2f}였고, 1차 측정값 10개 중 9개가 114–161 BPM에 몰렸다. 그러나 템포그램의 상위 3개 피크에는 요청 템포가 1차 {T1["top3_hits"]}/10, 2차 {T2["top3_hits"]}/10 포함되어, 요청을 무작위로 섞었을 때의 기대값(약 {T1["null_mean"]:.1f}, {T2["null_mean"]:.1f})보다 훨씬 많았다(두 차수 모두 순열 p < 0.0001). 즉 요청한 박은 대체로 음원 안에 있지만 가장 강한 박 단위가 아닌 경우가 많았다. 가장 느린 42 BPM 요청은 다섯 번의 생성에서 한 번도 상위 피크에 들지 않았다.')]
    c += [('h2', '4.5 사람이 들은 박: 세종 95 BPM 사례')]
    c += [P(f'2차 세종 클립은 95 BPM을 요청했고 자동 추정도 95.3 BPM이었으므로 성공처럼 보였다. 그러나 이름과 목표를 모르는 청취자 1인은 주 박을 48 BPM으로 탭하였다(표 4). 95 BPM 4분음표를 엄격히 요구한 재생성도 48 BPM, 정확한 95 BPM 킥·림을 덧입힌 음원도 47 BPM으로 들렸다. 덧입힌 박이 기존의 느린 박의 세분으로 흡수된 것이다. 마지막으로 사람의 측정값 47 BPM에서 목표 95 BPM으로 음높이를 유지한 채 시간축을 {TFV["retime_rate"]:.3f}배 압축하고, 충돌하던 하이햇을 4분음표마다 하나로 교체하자 새 익명 파일은 {HV["blind_tap_bpm"]:.0f} BPM으로 탭되었다(오차 {HV["absolute_error_percent"]:.1f}%, 사전 기준 ±5%)[20][21].')]
    c += [('table', '세종 클립의 지각 템포 진단과 보정 단계. 자동값은 librosa 추정, 사람 값은 같은 1인의 블라인드 탭이다. 마지막 행은 생성 원본이 아니라 후처리한 음원이다.',
           ['단계', '목표', '자동 BPM', '사람 탭', '판정'],
           [['2차 Suno 원본', 95, '95.3', 48, '실패'], ['엄격한 95 BPM 요청으로 재생성', 95, '95.3', 48, '실패'],
            ['원본 + 95 BPM 킥·림 덧입힘', 95, '95.3', 47, '실패'],
            ['47→95 시간축 보정 + 하이햇 교체', 95, '95.3', int(HV['blind_tap_bpm']), f'통과({HV["absolute_error_percent"]:.1f}%)']],
           [6.4, 1.4, 2, 1.8, 2.4], None)]
    c += [P('이 사례는 한 장소, 한 청취자의 순차적 공학 진단(n = 1)이므로 효과 크기나 성공률을 추정하지 않는다. 다만 자동으로 측정한 BPM 일치가 사람이 느끼는 박을 보장하지 않는다는 점, 그리고 정확한 템포가 의미를 가지는 경우 생성 모델보다 결정론적 후처리가 템포를 책임져야 한다는 점을 보여준다.')]
    c += [('h2', '4.6 무엇이 조성을 바꾸는가: 장르 단어')]
    c += [P(f'단조로 계속 실패한 강남과 아산 공장을 추가로 생성하였다(그림 4). 강남은 원래 장르 단어(“lo-fi hip-hop, city-pop”)를 유지한 5번의 생성에서 문구, 요청 형식, 근음 지정과 관계없이 단조가 한 번도 나오지 않았다. 장르 단어를 빼면 1/2, “dark synth-pop, moody downtempo”로 바꾸면 3/3이 단조였다[22]. 그러나 같은 방법을 아산에 적용하자 0/3이었다. 단조 요청 전체 {PF["n"]}건을 모으면 {PF["k"]}건({pct(PF["k"] / PF["n"])})이 단조였고, 사용자 지정 형식 {PF["shape"]["custom"]["k"]}/{PF["shape"]["custom"]["n"]} 대 단일 텍스트 {PF["shape"]["non-custom"]["k"]}/{PF["shape"]["non-custom"]["n"]}(Fisher p = {PF["p_shape"]:.3f}) 등 어떤 요인도 이 표본 크기에서 우연과 구별되지 않았다. 강남의 장르 교체 3/3 대 나머지 1/7(p = {PF["p_gangnam"]:.3f})은 여러 비교 중 하나이며 보정하지 않은 탐색적 결과이다. 지정한 근음은 강남 단조 3곡 중 1곡에서만 맞았다.')]
    c += [('fig', FIG / 'fig9_genre_words.png', 15.5, '단조를 요청한 두 장소의 모든 생성 결과(그림 내 라벨은 영문). 삼각형: 단조 검출(요청대로), 원: 장조 검출. 테두리 색: 회색 원래 장르 단어, 갈색 장르 단어 없음, 초록 교체한 장르 단어. (a) 강남 (b) 아산 공장.')]
    c += [('h2', '4.7 RQ5–RQ8')]
    c += [P('Gemini 스타일 예측은 구현되었고 요청 형식과 모델 식별자는 확인하였지만, 실제 API 키로 실행한 출력은 저장소에 기록되어 있지 않다. 따라서 규칙 기반 조성과 사진 기반 예측의 비교는 연구자가 함수의 지시를 실제 사진과 설명에 손으로 적용한 수작업 모의이며, 5곳 중 4곳이 일치하였다(홍대만 불일치). 청취자 실험(RQ6)은 사전 등록 프로토콜, 블라인드 평가 양식, 분석 스크립트(스피어먼 ρ, 순열검정, 쌍별 순서 정확도[15][16])가 준비되었으나 참가자 데이터는 없다. 현장 검증(RQ7)은 47열 관찰 양식과 한국어 설문이 준비되었고, 접근성(RQ8)은 기능 구현과 기술 점검만 했을 뿐 시각장애 사용자 평가는 하지 않았다.')]

    c += [('h1', '5. 피드백에 따른 개선 과정')]
    c += [P('검증 결과와 피드백은 바로 시스템 수정으로 이어졌다. 표 5는 주요 수정과 그 효과를 정리한 것이다. 가장 분명한 개선은 외부 모델의 문구를 바꾼 것보다 프로젝트 자신의 규칙과 데이터의 결함을 고친 데서 나왔다.')]
    c += [('table', '피드백과 검증에서 발견한 문제와 수정.',
           ['발견한 문제', '수정', '결과'],
           [['“complex” 키워드 충돌로 세종 행정기관이 반도체 공장 스타일을 받음', '행정기관(institutional) 범주 신설', '스타일 정상화, 이후 생성 95.3 BPM'],
            ['세종은 젊은 가족이 많은 계획도시라는 사실 누락(사용자 피드백)', '행정기관을 장조 규칙에 추가, 설명 수정', 'D♯ 장조, 적합도 0.94'],
            ['단조 요청 옆에 “warm, mellow” 등 밝은 단어', '단조일 때 밝은 단어 제거', '필요하지만 충분하지 않음(강남 실패)'],
            ['조성 단어가 긴 형용사 목록 끝에 묻힘', '조성을 앞쪽 별도 문장으로, 근음은 “around”로', '근음은 제어되지 않음'],
            ['자동 BPM 일치가 사람의 박과 다름', '시간축 보정 + 하이햇 교체', '1인 탭 96 BPM(1.1%)'],
            ['API 키가 공개 중계 서버를 거침, AI 요청문 무시, 미완성 음원 반환', '직접 호출, 화면의 요청문 사용, 완료 대기', '모의 네트워크로 확인']],
           [6.2, 5.0, 4.6], ['left', 'left', 'left'])]

    c += [('h1', '6. 논의, 한계 및 발전 방향')]
    c += [P('사슬은 구조적으로 끝까지 이어지지만 연결마다 강도가 다르다. 지역 순위는 상위권이 그럴듯하지만 가중치에 민감하고, 장소 점수는 주로 연구자의 오프셋이며, 조성 규칙은 지역 단위로 거칠고, 생성 모델은 단조와 사람이 느끼는 박을 보장하지 않는다. 이 결과는 청취자 실험의 해석에도 중요하다. 음원이 요청한 템포와 조성을 담지 못하면, 청취자 결과가 나빠도 지각의 실패인지 생성의 실패인지 구별할 수 없다.')]
    c += [P([('한계. ', {'bold': True}), '생성 음원은 한 제공자, 한 모델 버전의 20곡과 약 20곡의 후속 생성으로 작다. 후속 비교는 사전 등록되지 않았고 한 번에 여러 요소를 바꾸었다. 사람의 확인은 세종 클립 1개를 1인이 탭한 것뿐이며 나머지 조성·템포는 자동 검출이다. 가중치는 맞춘 값이 아니고 장소 점수는 측정값이 아니다. 서울·대전의 입력값은 15개 지역 원본 파일 밖에 있어 출처 대조가 남아 있다. Gemini 출력은 기록되지 않았다.'])]
    c += [P([('발전 방향. ', {'bold': True}), '노력 대비 가치가 큰 순서로, (1) 여러 청취자가 모든 클립의 박을 블라인드로 탭하고 음악 전공자가 조성을 확인한다. (2) 요청문 하나를 여러 번 생성한 뒤에만 개선을 주장한다. (3) 장르 단어 가설을 더 많은 장소에서 시험한다. (4) 클립 세트를 고정하고 성인 15–24명으로 청취자 실험을 한다. (5) 6–10개 지점, 2개 시간대로 현장 예비조사를 한다. (6) 실제 키로 Gemini를 점검한다. (7) 가능하면 시각장애 사용자와 인터페이스를 평가한다. (8) 현장 자료로 가설 가중치를 보정한다. 템포가 의미를 갖는 곳에서는 생성 음원을 화성·음색 재료로 쓰고 템포는 결정론적 보정으로 맞추는 구조를 제안한다.'])]

    c += [('h1', '7. 결론')]
    c += [P('Moodscape는 공식 통계에서 소리까지의 사슬을 끝까지 추적할 수 있게 만들었고, 앞의 네 연결을 계산과 측정으로 검증하였다. 지역 순위는 그럴듯하지만 가중치에 민감하고, 장소 점수는 대부분 연구자의 판단이며, 조성 규칙은 지역 단위로 거칠다. 생성 모델은 단조 요청을 지키지 못했고(두 차례 0/5), 자동으로 맞은 템포가 사람에게는 절반으로 들릴 수 있었다. 세종 사례에서 결정론적 시간축 보정이 사람이 느끼는 박을 목표에 맞출 수 있음을 확인하였다. 청취자가 의도한 순서를 듣는지, 모델이 실제 장소를 설명하는지, 인터페이스가 지도를 볼 수 없는 사람을 돕는지는 준비된 검증으로 남아 있다.')]
    c += [P([('자료 공개 및 AI 도구 사용. ', {'bold': True}), '모든 입력 데이터, 분석 스크립트, 생성 음원은 저장소에 공개하였다[17–22]. 생성 음원은 제공자의 이용 약관을 따르며 사진은 각자의 라이선스를 따른다. 시스템은 Gemini와 Suno를 구성요소로 사용하며, 분석 스크립트와 원고 일부는 연구자의 지시 아래 Claude(Anthropic)의 도움을 받아 작성하였다. 모든 수치는 저장소의 데이터에서 다시 계산하였고 내용에 대한 책임은 연구자에게 있다.'])]
    return c


def content_en():
    c = []
    c += [('h1', '1. Research Motivation')]
    c += [P('Maps show how places differ through color and labels, so a person who cannot see the screen does not learn which regions are busy and which are quiet. Sound can carry some of the same information, and sonified maps for users with visual impairment have precedent [6]. Turning data into sound raises a second problem, however. Soundscape research defines a soundscape as the acoustic environment as perceived by people in context [1] and measures it on two perceptual axes, Pleasantness and Eventfulness [2–4]. Oberman et al. collected 443 questionnaires at 28 points in protected natural areas and showed that perceived sound-source dominance and psychoacoustic measures predicted perception better than sound pressure level alone [5]. A single computed “mood” number therefore cannot be assumed to match what a place sounds like or what a listener hears.')]
    c += [P('This project starts from both problems. We need a tool that expresses a place’s character as music from official statistics, and because that tool is a chain (data → score → musical specification → generated audio → perception) in which every link can fail on its own, each link has to be tested separately.')]
    c += [('h1', '2. Objectives and Research Questions')]
    c += [P('The objectives are (1) to build Moodscape, a reproducible web prototype that turns official regional statistics into musical specifications for South Korean places; (2) to test each link of the chain as its own research question (RQ), to find out which links are strong and which are weak; and (3) to derive concrete improvements from the results.')]
    for t in ['RQ1. How do official statistics become a regional activity score, and is the ranking stable when the weights change?',
              'RQ2. How do regional values become landmark scores?',
              'RQ3. How does a score become a tempo, mode and style specification, and which rule decides each choice?',
              'RQ4. Does generated audio carry the specification, and what changes that?',
              'RQ5. How do the AI components (Gemini style prediction, request format) change the specification?',
              'RQ6–RQ8. Listener perception, perception in real places, and accessibility for blind users (protocols ready; no data).']:
        c.append(B(t))
    c += [('h1', '3. Methodology')]
    c += [('h2', '3.1 System design: from data to sound')]
    c += [P('The idea is to map a region’s activity onto tempo and pitch, and visitor satisfaction onto major or minor mode. Fig. 1 shows the implemented chain and the research question that tests each link. The web app uses static HTML/JavaScript and a D3 map, and for 17 provinces and 75 landmarks shows a score, the musical specification, photos, an explanation and generated audio [17][18].')]
    c += [('fig', FIG / 'fig1_chain.png', 15.5, 'The chain tested in this study. Each box is one link, labelled with the research question that tests it. Green: computed from project data; orange: measured on generated audio or hand-simulated; gray: no data collected yet.')]
    c += [P('Data and scores (RQ1, RQ2). Nine official inputs are used for 17 regions: 2025 population and density (Statistics Korea [7]); 2024 domestic tourism trips and four visitor-survey measures (overall satisfaction, recommendation, revisit intention, crowding satisfaction; National Travel Survey [8]); and 2023 noise and vibration complaints and regulated noise-emitting facilities (Ministry of Environment [9]). All values were transcribed by hand with a link to their source; nothing was scraped. Five activity components (density, trips per resident, complaints and facilities per 100,000 residents, crowding pressure = 100 − crowding satisfaction) are log1p-transformed, min–max scaled across the 17 regions and combined:')]
    c += [('eq', 'Activity Proxy = 100 × (0.35 density + 0.30 tourism + 0.15 complaints + 0.10 facilities + 0.10 crowding)')]
    c += [('eq', 'Visitor Pleasantness = 0.40 overall + 0.25 recommendation + 0.20 revisit + 0.15 crowding satisfaction')]
    c += [P('The weights are stated design hypotheses, not fitted coefficients, and the Activity Proxy is not an ISO 12913 Eventfulness coordinate; a field study to compare it with perception (RQ7) is designed separately. A landmark score is the region’s Activity Proxy plus an offset set by the researcher, clipped to [0, 1], and the app labels it “illustrative”.')]
    c += [P(f'Musical specification (RQ3). Tempo is round(42 + 110 × score) BPM, giving {S["spec"]["bpm_min"]}–{S["spec"]["bpm_max"]} BPM across the 75 landmarks; pitch is round(12 × score) semitones above A4 (440 Hz). Mode is decided by three rules in order: minor for solemn places (memorial, cemetery, observatory, cave); major for traditional, natural or administrative places (hanok, temple, palace, park, beach, government); otherwise major if the region’s Visitor Pleasantness is at or above the median of the 17 regions ({S["pleasantness_median"]:.2f}) and minor if below. Genre and mood words are chosen by place category and score band and joined with a scene sentence, a mode sentence, the tempo, instrumentation and a vocal directive into one generation request. Audio is generated with Suno model V4_5 through sunoapi.org. Gemini (gemini-3.5-flash-lite) can suggest genre, instruments and mood from a photo, but tempo, mode, root note and vocals are passed in as fixed values it cannot change. For non-visual use, every region is a keyboard stop with a screen-reader label, focus plays the score as pitch with east–west position as stereo pan, and arrow keys move to the nearest region.')]
    c += [('fig', HERE / 'figures' / 'app_map.png', 15.0, 'Start screen of the web app (current development branch). Region color is the activity score (blue calm, red active); choosing a region opens each landmark’s score, musical specification, photos and generated audio. The panel states that audio needs an MP3 or the user’s own Suno key and that the score weights are hypotheses.')]
    c += [('h2', '3.2 Verification design')]
    c += [P('Each link has an evidence class: computed (from project data and code), measured (generated audio analyzed by software), hand-simulated (a researcher followed a function’s instructions by hand; not live model output), or pending (no data). All statistics are recomputed by the repository’s analysis scripts with seed 20260920 [17].')]
    c += [B([('RQ1 weight sensitivity. ', {'bold': True}), 'Spearman correlation of each component with the score; agreement after dropping one component; and 10,000 weight vectors drawn from a Dirichlet distribution centered on the stated weights (concentration 20) and 10,000 from a flat Dirichlet. The order of the two regions with published soundscape values (Seoul [10] and Daejeon) was compared.'])]
    c += [B([('RQ2 variance partition. ', {'bold': True}), 'η² and ICC(1) of the 75 landmark scores grouped by region; association of a log English-Wikipedia readership index (Sep 2025–Aug 2026) [11] with the score by permutation test.'])]
    c += [B([('RQ4 audio measurement. ', {'bold': True}), 'Ten landmarks at rank quantiles of the 75 scores (Gangnam included as a minor-key case) were generated twice: round 1 with the original text and a single free-text request, round 2 with the revised text and Suno’s custom request shape. Audio was analyzed with librosa 1.0.0 [12]. Key is the major or minor key whose Krumhansl–Kessler profile [13] correlates best with the chroma vector; that correlation is reported as the key-fit score (not a probability). Tempo was assessed both as the single global estimate and as whether the request (±5%) is among the three strongest tempogram peaks; the chance level comes from 20,000 shuffles of the requests among clips. Rates carry Clopper–Pearson intervals [14]; 2×2 contrasts use Fisher’s exact test.'])]
    c += [B([('Variables. ', {'bold': True}), 'Independent: request wording (position and phrasing of the mode sentence), request shape (single text vs custom), genre words. Dependent: detected mode and tempo. Controlled: model version (V4_5), analysis procedure and version. Because the generator is stochastic, a single success was never counted as an improvement.'])]
    c += [B([('Human pulse check. ', {'bold': True}), 'For one Sejong clip, one informal listener who did not know the target tapped the main pulse of anonymous 25-second files. This is an engineering diagnostic with n = 1, not the listener experiment (RQ6).'])]
    c += [('h1', '4. Results')]
    c += [('h2', '4.1 RQ1: a plausible regional order that is sensitive to the weights')]
    c += [P(f'The Activity Proxy ranged from 32.9 to 61.3; Seoul, Busan and Jeju scored highest and Gwangju lowest. Visitor Pleasantness occupied a narrow band ({S["pleasantness_band"][0]:.1f}–{S["pleasantness_band"][1]:.1f}). The effective influence of the components did not follow the stated weights (Table 1): tourism, weighted 0.30, had almost no rank association with the score (ρ = {S["component_vs_activity_rho"]["tourism"]:.2f}), while dropping density reduced agreement with the full ranking to ρ = {S["drop_one_rho"]["density"]:.2f}. Under perturbation near the stated weights the median agreement was ρ = {MCL["rho_median"]:.2f}, but the 5th percentile was {MCL["rho_p5"]:.2f} and only {pct(MCL["share_rho_ge_90"])} of draws kept ρ ≥ 0.9 (Fig. 2). The two regions with published values were in the same order as the model (Seoul {ref["seoul_activity"]:.1f}, 1st; Daejeon {ref["daejeon_activity"]:.1f}, {ref["daejeon_rank"]}th; published Eventfulness 78 and 45), but two points can expose a contradiction, not validate a model.')]
    comp = [('Population density', 'density', 0.35), ('Tourism trips per resident', 'tourism', 0.30), ('Complaints per 100,000', 'complaints', 0.15),
            ('Facilities per 100,000', 'facilities', 0.10), ('Crowding pressure', 'crowding', 0.10)]
    c += [('table', 'Stated weight and actual influence of each Activity Proxy component (17 regions). ρ (component): Spearman correlation of the scaled component with the score; ρ (drop): agreement of the ranking recomputed without that component.',
           ['Component', 'Weight', 'ρ (component)', 'ρ (drop)'],
           [[n, f'{w:.2f}', f2(S['component_vs_activity_rho'][k]), f2(S['drop_one_rho'][k])] for n, k, w in comp], [6, 2.4, 2.6, 2.4], None)]
    c += [('fig', FIG / 'fig3_sensitivity.png', 15.5, 'Sensitivity of the Activity Proxy to its weights. (a) Rank under the stated weights (dot) and 95% range across 10,000 perturbed weight vectors (bar). (b) Distribution of Spearman ρ between perturbed and stated rankings; blue: near the stated weights, orange: arbitrary weights; dashed line ρ = 0.9.')]
    c += [('h2', '4.2 RQ2: landmark sound comes mostly from authored offsets')]
    c += [P(f'Region explained {pct(PV["eta_sq"])} of landmark-score variance (η²), and ICC(1) was indistinguishable from zero; landmark offsets (SD 0.21) varied far more than regional scores (SD 0.08). Place-level sound therefore reflects the researcher’s judgment more than official statistics, which the app discloses. The Wikipedia readership index was weakly related to the landmark score across {POP["n_complete"]} landmarks (ρ = {POP["rho"]:.2f}, permutation p = {POP["p_perm"]:.3f}), not distinguishable from zero at the 5% level; it measures online attention, not footfall or noise, and never changes the music.')]
    c += [('h2', '4.3 RQ3: Visitor Pleasantness decides the mode for less than half of the places')]
    c += [P(f'Category rules decided the mode for 40 of 75 landmarks ({pct(40 / 75)}); the Pleasantness rule decided {n_pleas} ({pct(n_pleas / 75)}) (Table 2), and {S["n_minor"]} landmarks request minor. Because the 17 Pleasantness values lie within 6.7 points and {S["n_regions_within1_of_median"]} regions sit within one point of the median, small survey differences become a categorical major/minor difference; and because the value is regional, every default-rule place in a region (e.g. Hongdae, Gangnam, N Seoul Tower) shares one decision.')]
    c += [('table', 'Which rule decides the requested mode (current code, 75 landmarks). Rules are applied in this order.',
           ['Deciding rule', 'Major', 'Minor', 'Places'],
           [['Solemn (memorial, cemetery, observatory, cave, …)', 0, KR['Solemn override']['minor key'], KR['Solemn override']['minor key']],
            ['Traditional/nature (hanok, temple, palace, park, beach, government, …)', KR['Traditional/nature override']['major key'], 0, KR['Traditional/nature override']['major key']],
            ['Regional Visitor Pleasantness (vs median of 17 regions)', KR['Regional Pleasantness default']['major key'], KR['Regional Pleasantness default']['minor key'], n_pleas],
            ['Total', 75 - S['n_minor'], S['n_minor'], 75]], [8.6, 1.8, 1.8, 2], None)]
    c += [('h2', '4.4 RQ4: generated audio follows the request only in part')]
    c += [P(f'In round 1 the requested mode was detected in {r1["mode_hits"]} of 10 tracks (95% interval {ci(r1["mode_ci"])}): {r1["major_hits"]}/{r1["major_n"]} major and {r1["minor_hits"]}/{r1["minor_n"]} minor requests. Round 2 reached {r2["mode_hits"]}/10 ({ci(r2["mode_ci"])}), but minor requests were again {r2["minor_hits"]}/{r2["minor_n"]} (Table 3, Fig. 3). The round-2 gain includes Sejong changing to a major request after a factual correction, and clips 05, 06 and 08 flipped without any change in request, consistent with random variation, so the gain cannot be attributed to the rewording. The Gangnam miss (A♯ major) had a key-fit score of 0.92, so the detector was not undecided.')]
    c += [('table', 'Requests and measurements for the ten landmarks. Measured BPM is librosa’s single estimate; ✓ requested mode detected, ✗ other mode. Sejong (07) requested minor in round 1 and major in round 2.',
           ['Clip', 'Landmark', 'Score', 'Req. BPM', 'R1 BPM', 'R2 BPM', 'Mode asked', 'R1 key', 'R2 key'],
           clip_rows('en'), [0.9, 4.4, 1.0, 1.3, 1.2, 1.2, 1.9, 1.8, 1.8], ['center', 'left'] + ['center'] * 7)]
    c += [('fig', FIG / 'fig7_audio_fidelity.png', 14.5, 'Generated audio against the specification. (a) Requested vs measured tempo, round 1 (filled) and round 2 (open); solid line exact agreement, dashed and dotted lines double and half tempo; diamonds are the half- or double-tempo reading of the same number (the audio is unchanged). (b) Detected key and key-fit score per clip; blue requested mode, orange other mode.')]
    c += [P(f'Judged by the single estimate, tempo was barely followed: the rank correlation between requested and measured tempo was ρ = {r1["rho"]:.2f} (round 1) and {r2["rho"]:.2f} (round 2), and nine of ten round-1 estimates fell between 114 and 161 BPM. Yet the requested tempo was among the three strongest tempogram peaks in {T1["top3_hits"]}/10 and {T2["top3_hits"]}/10 clips, against about {T1["null_mean"]:.1f} and {T2["null_mean"]:.1f} expected by chance (permutation p < 0.0001 in both rounds). The requested pulse is usually present, but often not the strongest metrical level. The slowest request, 42 BPM, never appeared among the top peaks in five generations.')]
    c += [('h2', '4.5 The pulse a person heard: the Sejong 95 BPM case')]
    c += [P(f'The round-2 Sejong clip requested 95 BPM and the automatic estimate was 95.3 BPM, so it looked like a success. One informal listener who did not know the target tapped its main pulse at 48 BPM (Table 4). A regeneration that strictly required a 95 BPM quarter-note pulse was also tapped at 48 BPM, and the source with an exact 95 BPM kick and rim overlaid at 47 BPM, the added pulse being absorbed as a subdivision of the slow beat. Finally the time axis was compressed {TFV["retime_rate"]:.3f}× with pitch preserved, from the human measurement of 47 BPM to the 95 BPM target, and the conflicting hi-hat was replaced by one hit per quarter note; the new anonymous file was tapped at {HV["blind_tap_bpm"]:.0f} BPM ({HV["absolute_error_percent"]:.1f}% error; criterion ±5% set before the test) [20][21].')]
    c += [('table', 'Perceptual-tempo diagnosis and correction for the Sejong clip. Automatic values are librosa estimates; human values are blind taps by the same single listener. The last row is post-processed audio, not a raw generation.',
           ['Stage', 'Target', 'Automatic BPM', 'Human tap', 'Decision'],
           [['Round-2 Suno source', 95, '95.3', 48, 'Fail'], ['Regenerated with strict 95 BPM request', 95, '95.3', 48, 'Fail'],
            ['Source + 95 BPM kick and rim', 95, '95.3', 47, 'Fail'],
            ['47→95 time-axis correction + hi-hat replacement', 95, '95.3', int(HV['blind_tap_bpm']), f'Pass ({HV["absolute_error_percent"]:.1f}%)']],
           [6.8, 1.4, 2.4, 1.8, 2.2], None)]
    c += [P('This is a sequential engineering diagnostic at one place with one listener (n = 1); it does not estimate an effect size or success rate. It does show that an automatic BPM match does not guarantee the pulse a person perceives, and that where exact tempo carries meaning, deterministic post-processing rather than the generator should be responsible for tempo.')]
    c += [('h2', '4.6 What changes the mode: genre words')]
    c += [P(f'The two places that kept failing to come back minor, Gangnam and the Asan plant, were generated further (Fig. 4). For Gangnam, none of the five generations that kept the original genre words (“lo-fi hip-hop, city-pop”) was minor, regardless of wording, request shape or an explicit root; one of two was minor without genre words, and three of three when the genre was swapped to “dark synth-pop, moody downtempo” [22]. The same swap gave 0/3 for Asan. Pooling all {PF["n"]} minor requests, {PF["k"]} ({pct(PF["k"] / PF["n"])}) came back minor, and no single factor was distinguishable from chance at this sample size (custom {PF["shape"]["custom"]["k"]}/{PF["shape"]["custom"]["n"]} vs single-text {PF["shape"]["non-custom"]["k"]}/{PF["shape"]["non-custom"]["n"]}, Fisher p = {PF["p_shape"]:.3f}). Gangnam’s 3/3 vs 1/7 (p = {PF["p_gangnam"]:.3f}) is one of several uncorrected exploratory comparisons. The requested root note was matched in only one of three Gangnam minor tracks.')]
    c += [('fig', FIG / 'fig9_genre_words.png', 15.5, 'Every generation for the two minor-key places. Triangles: minor detected (as requested); circles: major detected. Outline: gray original genre words, brown no genre words, green swapped genre words. (a) Gangnam (b) Asan plant.')]
    c += [('h2', '4.7 RQ5–RQ8')]
    c += [P('The Gemini style predictor is implemented and its request format and model identifier were checked, but no output from a key-backed run is recorded in the repository. The comparison of rule-based mode with photo-based prediction is therefore a hand simulation (a researcher applied the function’s instructions to the real photos and text): four of five places agreed, and only Hongdae differed. For the listener experiment (RQ6) a preregistered protocol, a blinded rating form and an analysis script (Spearman ρ, permutation test, pairwise ordering accuracy, ICC [15], Lin’s concordance [16]) are ready, but no participant data exist. The field study (RQ7) has a 47-column observation template and a Korean questionnaire, and accessibility (RQ8) has implemented features and technical checks only, with no evaluation by blind users.')]
    c += [('h1', '5. Feedback-driven Improvements')]
    c += [P('Results and feedback were turned directly into fixes (Table 5). The clearest gains came from repairing the project’s own rules and data rather than from rewording the request to a third-party model.')]
    c += [('table', 'Problems found through testing and feedback, and the fixes.',
           ['Problem found', 'Fix', 'Outcome'],
           [['Keyword collision (“complex”) gave the Sejong government complex a semiconductor-plant style', 'New institutional category', 'Style corrected; later generations at 95.3 BPM'],
            ['Missing fact: Sejong is a planned city with many young families (user feedback)', 'Government added to major rule; description updated', 'D♯ major, key-fit 0.94'],
            ['Bright words (“warm, mellow”) next to a minor request', 'Remove bright words when minor', 'Necessary, not sufficient (Gangnam failed)'],
            ['Mode word buried at the end of a long adjective list', 'Mode as an early sentence; root as “around”', 'Root still not controlled'],
            ['Automatic BPM match differed from the human pulse', 'Time-axis correction + hi-hat replacement', 'One listener tapped 96 BPM (1.1%)'],
            ['Key passed through a public relay; AI prompt ignored; unfinished audio returned', 'Direct calls; use the prompt shown; wait for completion', 'Checked with a mocked network']],
           [6.2, 5.0, 4.6], ['left', 'left', 'left'])]
    c += [('h1', '6. Conclusions, Limitations and Future Plans')]
    c += [P('Moodscape makes the chain from official statistics to sound traceable end to end, and its first four links were tested by computation and measurement. The regional order is plausible but weight-sensitive; landmark scores are mostly the researcher’s judgment; the mode rule is coarse and regional; and the generator did not honor minor-key requests (0/5 across the two rounds) or guarantee the pulse a person perceives. In the Sejong case, deterministic time-axis correction brought the perceived pulse to the target. These results matter for interpreting any listener study: if the audio does not carry the requested tempo and mode, a weak listener result cannot separate a failure of perception from a failure of generation.')]
    c += [P([('Limitations. ', {'bold': True}), 'Twenty tracks plus about twenty follow-ups from one provider and model version; follow-up comparisons were not preregistered and changed several things at once; the only human check is one listener tapping one clip, and all other modes and tempos are automatic detections; weights are not fitted and landmark scores are not measured; the inputs for Seoul and Daejeon sit outside the 15-region source file and still need provenance reconciliation; no Gemini output is recorded.'])]
    c += [P([('Future plans. ', {'bold': True}), 'In order of value per effort: (1) several listeners tap every clip blind and a trained musician identifies the mode; (2) generate each request several times before claiming any change works; (3) test the genre-word hypothesis at more places; (4) freeze one clip set and run the listener experiment with 15–24 adults; (5) run a field pilot at 6–10 sites in two time windows; (6) check Gemini with a live key; (7) evaluate the interface with blind and low-vision users when possible; (8) calibrate the hypothesised weights with field data. Where tempo carries meaning, we propose using generated audio as harmonic and timbral material and enforcing tempo with deterministic correction.'])]
    c += [P([('Data availability and use of AI tools. ', {'bold': True}), 'All inputs, analysis scripts and generated audio are public in the project repository [17–22]; generated audio remains subject to the provider’s terms and photographs keep their own licenses. The system uses Gemini and Suno as components. The analysis scripts and parts of this manuscript were prepared with the assistance of Claude (Anthropic) under the researcher’s direction; every number was recomputed from repository data, and the researcher is responsible for the content.'])]
    return c


SUMMARY_KO = ('지도는 장소의 차이를 시각으로만 전달한다. 본 연구는 공식 지역 통계를 음악으로 바꾸는 웹 프로토타입 Moodscape를 만들고, '
              '데이터에서 소리까지의 연결을 하나씩 검증하였다. 17개 시·도의 공식 지표 9종으로 활동 점수와 방문객 쾌적성을 계산하고, '
              '75개 장소의 템포·조성·스타일을 규칙으로 정해 Suno로 음원 20곡을 생성한 뒤 librosa로 측정하였다. '
              f'지역 순위는 가중치 교란에 민감하였고(ρ 중앙값 {MCL["rho_median"]:.2f}), 장소 점수 분산 중 지역이 설명한 비율은 {pct(PV["eta_sq"])}였다. '
              f'요청 조성 일치는 1차 {r1["mode_hits"]}/10, 2차 {r2["mode_hits"]}/10이었고 단조 요청 5건은 모두 장조로 생성되었다. '
              f'요청 템포는 상위 3개 리듬 피크에 {T1["top3_hits"]}/10, {T2["top3_hits"]}/10 포함되었으나, 세종 클립은 자동 측정 95.3 BPM이 '
              f'청취자에게 48 BPM으로 들려 시간축 보정 후 {HV["blind_tap_bpm"]:.0f} BPM을 얻었다. 청취자·현장·접근성 검증은 프로토콜까지 준비되었다.')
ABSTRACT_EN = ('Maps convey differences between places only visually. We built Moodscape, a web prototype that turns official regional '
               'statistics into music, and tested each link from data to sound. Nine official indicators for 17 Korean provinces give an '
               'activity score and a visitor-pleasantness score; rules turn them into tempo, mode and style for 75 places; 20 tracks were '
               f'generated with Suno and measured with librosa. The regional ranking was sensitive to its weights (median ρ = {MCL["rho_median"]:.2f}), '
               f'and region explained only {pct(PV["eta_sq"])} of landmark-score variance. The requested mode was detected in {r1["mode_hits"]}/10 and '
               f'{r2["mode_hits"]}/10 tracks, and all five minor-key requests came back major. The requested tempo was among the three strongest '
               f'rhythmic peaks in {T1["top3_hits"]}/10 and {T2["top3_hits"]}/10 clips (about 1.5 expected by chance), yet one clip measured at 95.3 BPM '
               f'was tapped at 48 BPM by a listener and reached {HV["blind_tap_bpm"]:.0f} BPM only after time-axis correction. Listener, field and '
               'accessibility studies are prepared but not yet run.')
KEYWORDS = 'Generative music, ISO 12913, Sonification, Soundscape, Validation'


# ---------------------------------------------------------------------------------------------- docx assembly
def fill_title_block(doc, lang):
    t = doc.tables[0]
    for row in t.rows:
        for p in list(row.cells[0].paragraphs):
            if p.text.strip().startswith('(서체'):
                remove(p)

    def write(row, lines):
        ps = t.rows[row].cells[0].paragraphs
        for p in ps[1:]:
            remove(p)
        p0 = ps[0]
        for i, (parts, font, size) in enumerate(lines):
            p = p0 if i == 0 else t.rows[row].cells[0].add_paragraph()
            clear(p)
            add_runs(p, parts, font, size)
            fmt(p, 'center', 2 if i == 0 else 0, 2, 1.15)

    title_ko = '공식 통계에서 소리까지: 지역 데이터 음악화 시스템 Moodscape의 연결별 검증'
    title_en = 'From Official Statistics to Sound: Testing Each Link of Moodscape, a Data-to-Music System for South Korean Places'
    if lang == 'ko':
        write(0, [([(title_ko, {'bold': True})], MYEONGJO, 14)])
        write(1, [(['[참가자 이름]', ('1*', {'sup': True})], DOTUM, 10), ([('1', {'sup': True}), '[학교명], [지역], 대한민국'], DOTUM, 10)])
    write(2, [([(title_en, {'bold': True})], MYEONGJO, 14)])
    write(3, [(['[Participant Name]', ('1*', {'sup': True})], DOTUM, 10), ([('1', {'sup': True}), '[School Name], [City], Republic of Korea'], DOTUM, 10)])

    # 요약 row
    cell = t.rows[4].cells[0]
    ps = [p for p in cell.paragraphs if p.text.strip()]
    p = ps[0]; clear(p)
    add_runs(p, [('요 약 ', {'bold': True}), SUMMARY_KO], MYEONGJO, 9); fmt(p, 'justify', 2, 2, 1.15)
    # Abstract + keywords row
    cell = t.rows[5].cells[0]
    ps = [p for p in cell.paragraphs if p.text.strip()]
    clear(ps[0]); add_runs(ps[0], [('Abstract ', {'bold': True}), ABSTRACT_EN], MYEONGJO, 9); fmt(ps[0], 'justify', 2, 2, 1.15)
    clear(ps[1]); add_runs(ps[1], [('Key Words : ', {'bold': True}), KEYWORDS], MYEONGJO, 9); fmt(ps[1], 'left', 4, 2, 1.15)
    if lang == 'en':  # English-only edition: drop the Korean title, author and 요약 rows
        for i in (4, 1, 0):
            t._tbl.remove(t.rows[i]._tr)


def build(lang, template, out_docx):
    doc = Document(str(template))
    if lang == 'en':
        for p in doc.sections[0].header.paragraphs:
            if p.text.strip():
                clear(p); add_runs(p, ['KSEF 2027 International'], MYEONGJO, 10)
    else:
        for p in doc.sections[0].header.paragraphs:
            if p.text.strip():
                clear(p); add_runs(p, [('KSEF National', {'bold': True}), '(국내분야)'], MYEONGJO, 10)
    fill_title_block(doc, lang)
    body = doc.paragraphs
    for p in body[3:]:
        remove(p)
    body[2].text = ''

    blocks = content_ko() if lang == 'ko' else content_en()
    nfig = ntab = 0
    fig_word, tab_word = ('그림', '표') if lang == 'ko' else ('Fig.', 'Table')
    for b in blocks:
        kind = b[0]
        if kind == 'h1':
            p = doc.add_paragraph(); add_runs(p, [(b[1], {'bold': True})], MYEONGJO, 12.5); fmt(p, 'left', 10, 4, 1.15, keep_next=True)
        elif kind == 'h2':
            p = doc.add_paragraph(); add_runs(p, [(b[1], {'bold': True})], MYEONGJO, 11); fmt(p, 'left', 6, 2, 1.15, keep_next=True)
        elif kind in ('p', 'b'):
            parts = b[1][0] if len(b[1]) == 1 and isinstance(b[1][0], list) else b[1]
            p = doc.add_paragraph()
            if kind == 'b':
                add_runs(p, ['• '], MYEONGJO, 10.5)
                p.paragraph_format.left_indent = Cm(0.4); p.paragraph_format.first_line_indent = Cm(-0.4)
            add_runs(p, parts, MYEONGJO, 10.5)
            fmt(p, 'justify', 0, 3, 1.25)
        elif kind == 'eq':
            p = doc.add_paragraph(); add_runs(p, [(b[1], {'italic': lang == 'en'})], MYEONGJO, 10); fmt(p, 'center', 2, 4, 1.15)
        elif kind == 'fig':
            nfig += 1
            p = doc.add_paragraph(); p.add_run().add_picture(str(b[1]), width=Cm(b[2])); fmt(p, 'center', 4, 0, 1.0, keep_next=True)
            cap = doc.add_paragraph(); add_runs(cap, [(f'{fig_word} {nfig}. ', {'bold': True}), b[3]], MYEONGJO, 8.5); fmt(cap, 'justify', 2, 6, 1.15)
        elif kind == 'table':
            ntab += 1
            _, caption, header, rows_, widths, align = b
            cap = doc.add_paragraph(); add_runs(cap, [(f'{tab_word} {ntab}. ', {'bold': True}), caption], MYEONGJO, 8.5); fmt(cap, 'justify', 6, 2, 1.15, keep_next=True)
            academic_table(doc, header, rows_, widths, MYEONGJO, 8, align)
            sp = doc.add_paragraph(); fmt(sp, 'left', 0, 2, 1.0)
    # References
    p = doc.add_paragraph(); add_runs(p, [('참고문헌' if lang == 'ko' else 'References', {'bold': True})], MYEONGJO, 12.5); fmt(p, 'left', 10, 4, 1.15, keep_next=True)
    for i, r in enumerate(REFS, 1):
        text = r[lang] if lang in r else r['ko']
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.6)
        parts = [f'[{i}] ', text]
        if r.get('url'):
            parts += [(r['url'], {'link': r['url'], 'size': 8.5}), ', ' + r['when'][0 if lang == 'ko' else 1] + '.']
        add_runs(p, parts, MYEONGJO, 8.5)
        fmt(p, 'left', 0, 1.5, 1.1)
    doc.save(out_docx)
    return nfig, ntab


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--template', type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument('--no-pdf', action='store_true')
    args = ap.parse_args()
    assert len(SUMMARY_KO) <= 500, f'요약 {len(SUMMARY_KO)}자 > 500'
    assert len(ABSTRACT_EN.split()) <= 200, f'Abstract {len(ABSTRACT_EN.split())} words > 200'
    jobs = [('ko', HERE / 'national' / 'KSEF2027_National_논문_Moodscape.docx'),
            ('en', HERE / 'international' / 'KSEF2027_International_Research_paper_Moodscape.docx')]
    for lang, out in jobs:
        out.parent.mkdir(parents=True, exist_ok=True)
        nf, nt = build(lang, args.template, out)
        print(f'{out.name}: {nf} figures, {nt} tables; 요약 {len(SUMMARY_KO)}자, abstract {len(ABSTRACT_EN.split())} words')
        if not args.no_pdf:
            pdf = out.with_suffix('.pdf')
            export_pdf_with_pages(out, pdf)
            try:
                from pypdf import PdfReader
                print(f'  -> {pdf.name}: {len(PdfReader(str(pdf)).pages)} pages')
            except ImportError:
                print(f'  -> {pdf.name}')


if __name__ == '__main__':
    main()
