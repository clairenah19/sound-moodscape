#!/usr/bin/env python3
"""Build the KSEF 2027 National (Korean) and International (English) presentation decks.

International guidelines: PowerPoint format, submitted as PDF, 7-minute talk. National guidelines: free format,
PDF, Korean or English. Both decks are written as .pptx with python-pptx and exported to PDF with Keynote.
Numbers are read from research/paper/stats.json, the same source as the papers.

Run from the repository root:  python3 ksef2027/build_decks.py [--no-pdf]
"""
import argparse
import json
import subprocess
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
RES = HERE.parent / 'research'
FIG = RES / 'paper' / 'figures'
S = json.loads((RES / 'paper' / 'stats.json').read_text())
HV = json.loads((RES / 'listener_clips' / 'clip07_sejong_retimed_hihat_fixed.json').read_text())['human_validation']
TAG = 'ksef2027-submission'
REPO = 'https://github.com/clairenah19/sound-moodscape'
DEMO = 'https://clairenah19.github.io/sound-moodscape/'
AUDIO = f'{REPO}/tree/{TAG}/research/listener_clips'

NAVY, INK, MUTED, LINE = RGBColor(0x15, 0x24, 0x4A), RGBColor(0x1B, 0x1B, 0x1B), RGBColor(0x5A, 0x5A, 0x5A), RGBColor(0xD9, 0xD9, 0xD9)
BLUE, ORANGE, GREEN, CARD = RGBColor(0x2A, 0x78, 0xD6), RGBColor(0xE0, 0x62, 0x2F), RGBColor(0x1B, 0x9E, 0x6E), RGBColor(0xF3, 0xF5, 0xF9)
FONT = 'Apple SD Gothic Neo'
W, H = Inches(13.333), Inches(7.5)

r1, r2 = S['round1'], S['round2']
T1, T2 = S['tempo_diag']['round1'], S['tempo_diag']['round2']
MCL, PV, PF, KR = S['mc_local'], S['place_variance'], S['prompt_features'], S['key_rules']
n_pleas = sum(KR['Regional Pleasantness default'].values())


def tb(slide, x, y, w, h, paras, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.1):
    """paras: list of str or list of (text, opts) runs; opts: bold, color, size, link."""
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing = align, spacing
        p.space_after = Pt(size * 0.45)
        runs = [(para, {})] if isinstance(para, str) else para
        for text, opt in runs:
            r = p.add_run()
            r.text = text
            r.font.name = FONT
            r.font.size = Pt(opt.get('size', size))
            r.font.bold = opt.get('bold', bold)
            r.font.color.rgb = opt.get('color', color)
            if opt.get('link'):
                r.hyperlink.address = opt['link']
                r.font.color.rgb = BLUE
                r.font.underline = True
    return box


def rect(slide, x, y, w, h, fill=CARD, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1.5)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.08
    s.shadow.inherit = False
    return s


def picture(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(path), x, y, w, h)


class Deck:
    def __init__(self, footer):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = W, H
        self.footer = footer
        self.n = 0

    def slide(self, title, kicker=None):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.n += 1
        if kicker:
            tb(s, Inches(0.6), Inches(0.32), Inches(9), Inches(0.4), [kicker], 13, BLUE, True)
        # Rough width estimate (Hangul ~1 em, Latin ~0.55 em) so long titles drop to 24 pt instead of wrapping.
        est = sum(1.0 if ord(ch) > 0x1100 else 0.55 for ch in title)
        tb(s, Inches(0.6), Inches(0.62), Inches(12.1), Inches(0.9), [title], 28 if est <= 35 else 24, NAVY, True)
        line = s.shapes.add_connector(1, Inches(0.6), Inches(1.45), Inches(12.73), Inches(1.45))
        line.line.color.rgb = LINE; line.line.width = Pt(1)
        tb(s, Inches(0.6), Inches(7.02), Inches(9), Inches(0.35), [self.footer], 10, MUTED)
        tb(s, Inches(11.9), Inches(7.02), Inches(0.83), Inches(0.35), [str(self.n)], 10, MUTED, align=PP_ALIGN.RIGHT)
        return s

    def stat(self, s, x, y, w, h, value, label, color=NAVY):
        rect(s, x, y, w, h)
        tb(s, x + Inches(0.15), y + Inches(0.12), w - Inches(0.3), Inches(0.75), [value], 30, color, True)
        tb(s, x + Inches(0.15), y + Inches(0.9), w - Inches(0.3), h - Inches(1.0), [label], 13, MUTED)


def build(lang, out):
    ko = lang == 'ko'
    T = (lambda k, e: k) if ko else (lambda k, e: e)
    d = Deck(T('Moodscape · KSEF 2027 National(국내분야)', 'Moodscape · KSEF 2027 International'))

    # 1 Title
    s = d.prs.slides.add_slide(d.prs.slide_layouts[6]); d.n += 1
    rect(s, 0, 0, W, H, NAVY, shape=MSO_SHAPE.RECTANGLE)
    tb(s, Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.5), ['Moodscape'], 20, RGBColor(0x9E, 0xC5, 0xF4), True)
    tb(s, Inches(0.8), Inches(1.95), Inches(11.7), Inches(2.0),
       [T('공식 통계에서 소리까지:', 'From Official Statistics to Sound:'),
        T('지역 데이터 음악화 시스템의 연결별 검증', 'Testing Each Link of a Data-to-Music System for South Korean Places')],
       38 if ko else 34, RGBColor(0xFF, 0xFF, 0xFF), True, spacing=1.0)
    tb(s, Inches(0.8), Inches(4.6), Inches(11.7), Inches(1.6),
       [T('[참가자 이름] · [학교명] · 대한민국', '[Participant Name] · [School Name] · Republic of Korea'),
        T('KSEF 2027 National(국내분야) · 분과 [분과코드]', 'KSEF 2027 International · Category [Code]')], 18, RGBColor(0xDD, 0xE6, 0xF5))

    # 2 Problem
    s = d.slide(T('지도는 눈으로만 읽힌다, 그리고 숫자 하나는 장소가 아니다', 'Maps are read only with the eyes, and one number is not a place'), T('1 · 문제 인식', '1 · Motivation'))
    cards = [(T('시각에만 의존하는 지도', 'Maps depend on vision'),
              T('어느 지역이 붐비고 한적한지는 색과 글자로만 전달된다. 화면을 볼 수 없는 사람에게는 전달되지 않는다.',
                'Which regions are busy or quiet is shown only by color and labels, and does not reach people who cannot see the screen.')),
             (T('소리는 다른 감각의 통로', 'Sound is another channel'),
              T('지리 데이터를 소리로 바꾸어 시각장애인의 탐색을 돕는 선행 사례가 있다 [Zhao 2008].',
                'Sonified maps have helped users with visual impairment explore geographic data [Zhao 2008].')),
             (T('그러나 “분위기”는 지각된 것', 'But atmosphere is perceived'),
              T('사운드스케이프는 사람이 지각한 음향 환경이다(ISO 12913). 음압 하나보다 음원과 심리음향이 지각을 더 잘 설명한다 [Oberman 2025].',
                'A soundscape is the acoustic environment as perceived (ISO 12913); perceived sources predict perception better than sound level alone [Oberman 2025].'))]
    for i, (h, b) in enumerate(cards):
        x = Inches(0.6 + i * 4.1)
        rect(s, x, Inches(1.9), Inches(3.85), Inches(3.6))
        tb(s, x + Inches(0.25), Inches(2.1), Inches(3.4), Inches(0.9), [h], 20, NAVY, True)
        tb(s, x + Inches(0.25), Inches(3.05), Inches(3.4), Inches(2.4), [b], 17, INK)
    tb(s, Inches(0.6), Inches(5.85), Inches(12.1), Inches(1.0),
       [[(T('질문: ', 'Question: '), {'bold': True, 'color': BLUE}),
         (T('공식 통계를 음악으로 바꿀 수 있는가? 그리고 그 사슬의 각 연결은 실제로 작동하는가?',
            'Can official statistics be turned into music, and does each link of that chain actually work?'), {})]], 20, INK)

    # 3 Objectives / chain
    s = d.slide(T('목표: 만들고, 연결마다 따로 검증한다', 'Goal: build it, then test every link on its own'), T('2 · 연구 목적과 연구 질문', '2 · Objectives and research questions'))
    picture(s, FIG / 'fig1_chain.png', Inches(0.6), Inches(1.65), w=Inches(7.6))
    tb(s, Inches(8.5), Inches(1.7), Inches(4.25), Inches(5.2),
       [[(T('목적', 'Objectives'), {'bold': True, 'color': NAVY})],
        T('① 재현 가능한 데이터 → 음악 웹 앱 개발', '① Build a reproducible data-to-music web app'),
        T('② 각 연결을 독립된 연구 질문으로 검증', '② Test each link as its own research question'),
        T('③ 결과로 개선 방향 제시', '③ Derive improvements from the results'),
        [(T('증거 등급', 'Evidence classes'), {'bold': True, 'color': NAVY})],
        [('■ ', {'color': GREEN}), (T('계산: RQ1–RQ3', 'Computed: RQ1–RQ3'), {})],
        [('■ ', {'color': ORANGE}), (T('측정·모의: RQ4–RQ5', 'Measured / simulated: RQ4–RQ5'), {})],
        [('■ ', {'color': MUTED}), (T('미수집: RQ6–RQ8 (청취자·현장·접근성)', 'Pending: RQ6–RQ8 (listeners, field, access)'), {})]], 16)

    # 4 System
    s = d.slide(T('아이디어 → 시스템: 활발함은 템포로, 만족은 조성으로', 'Idea → system: activity becomes tempo, satisfaction becomes mode'), T('3 · 시스템 개발', '3 · System design'))
    picture(s, HERE / 'figures' / 'app_map.png', Inches(0.6), Inches(1.7), w=Inches(6.4))
    tb(s, Inches(7.3), Inches(1.7), Inches(5.45), Inches(5.2),
       [[(T('입력: 17개 시·도 공식 지표 9종', 'Input: 9 official indicators, 17 provinces'), {'bold': True, 'color': NAVY})],
        T('인구밀도(통계청), 관광 횟수·방문객 설문(2024 국민여행조사), 소음 민원·배출시설(환경부). 모두 출처 링크와 함께 수기 입력.',
          'Density (Statistics Korea), tourism and visitor survey (2024 National Travel Survey), noise complaints and facilities (Ministry of Environment), transcribed with source links.'),
        [(T('활동 프록시', 'Activity Proxy'), {'bold': True, 'color': NAVY})],
        T('100 × (0.35 밀도 + 0.30 관광 + 0.15 민원 + 0.10 시설 + 0.10 혼잡)', '100 × (0.35 density + 0.30 tourism + 0.15 complaints + 0.10 facilities + 0.10 crowding)'),
        [(T('음악 사양', 'Musical specification'), {'bold': True, 'color': NAVY})],
        T('템포 = 42 + 110 × 점수 BPM · 음높이 = A4 + 12 × 점수 반음 · 조성 = 규칙 3개 → Suno V4_5로 생성',
          'Tempo = 42 + 110 × score BPM · pitch = A4 + 12 × score semitones · mode = 3 rules → generated with Suno V4_5'),
        [(T('접근성', 'Accessibility'), {'bold': True, 'color': NAVY})],
        T('키보드 이동, 화면낭독기 라벨, 점수 → 음높이, 동서 위치 → 스테레오', 'Keyboard navigation, screen-reader labels, score → pitch, east–west → stereo')], 14)

    # 5 Method
    s = d.slide(T('실험 설계: 같은 장소를 두 번 생성하고 소프트웨어와 사람으로 측정', 'Design: generate the same places twice, measure by software and by ear'), T('4 · 검증 방법', '4 · Verification design'))
    cols = [(T('변인', 'Variables'), [T('독립: 요청 문구, 요청 형식(단일 텍스트 / custom), 장르 단어', 'Independent: wording, request shape (single text / custom), genre words'),
                                       T('종속: 검출 조성, 검출 템포', 'Dependent: detected mode and tempo'),
                                       T('통제: 모델 V4_5, 분석 절차, 시드 20260920', 'Controlled: model V4_5, analysis procedure, seed 20260920')]),
            (T('측정', 'Measurement'), [T('10개 장소(점수 분위수) × 2차례 생성', '10 places (score quantiles) × 2 rounds'),
                                         T('조성: Krumhansl–Kessler 조성 프로파일 상관', 'Key: Krumhansl–Kessler profile correlation'),
                                         T('템포: 단일 추정 + 템포그램 상위 3 피크, 순열 20,000회', 'Tempo: single estimate + top-3 tempogram peaks, 20,000 permutations')]),
            (T('통계', 'Statistics'), [T('가중치 민감도: 디리클레 10,000회', 'Weight sensitivity: 10,000 Dirichlet draws'),
                                        T('Clopper–Pearson 구간, Fisher 정확검정', 'Clopper–Pearson intervals, Fisher exact test'),
                                        T('한 번의 성공은 개선으로 보지 않음(확률적 생성)', 'A single success is never counted as a fix (stochastic)')])]
    for i, (h, items) in enumerate(cols):
        x = Inches(0.6 + i * 4.1)
        rect(s, x, Inches(1.85), Inches(3.85), Inches(4.4))
        tb(s, x + Inches(0.25), Inches(2.0), Inches(3.4), Inches(0.6), [h], 20, NAVY, True)
        tb(s, x + Inches(0.25), Inches(2.7), Inches(3.4), Inches(3.5), ['• ' + t for t in items], 15)
    tb(s, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.6),
       [T('사람의 확인: 세종 클립 1개를 1인이 블라인드 탭(공학적 진단, n = 1, 청취자 실험 아님)',
          'Human check: one listener blind-tapped one Sejong clip (engineering diagnostic, n = 1, not the listener study)')], 14, MUTED)

    # 6 RQ1
    s = d.slide(T('RQ1 · 지역 순위는 그럴듯하지만 가중치에 민감하다', 'RQ1 · The regional order is plausible but weight-sensitive'), T('5 · 결과', '5 · Results'))
    picture(s, FIG / 'fig3_sensitivity.png', Inches(0.6), Inches(1.75), w=Inches(8.3))
    d.stat(s, Inches(9.2), Inches(1.75), Inches(3.55), Inches(1.55), f'ρ = {MCL["rho_median"]:.2f}', T('가중치 교란 시 순위 일치 중앙값', 'median rank agreement under perturbed weights'))
    d.stat(s, Inches(9.2), Inches(3.45), Inches(3.55), Inches(1.55), f'{100 * MCL["share_rho_ge_90"]:.0f}%', T('ρ ≥ 0.9를 유지한 비율', 'of draws kept ρ ≥ 0.9'), ORANGE)
    d.stat(s, Inches(9.2), Inches(5.15), Inches(3.55), Inches(1.55), f'ρ = {S["component_vs_activity_rho"]["tourism"]:.2f}', T('가중치 0.30인 관광 성분의 실제 영향', 'actual influence of tourism (weight 0.30)'), ORANGE)

    # 7 RQ2-3
    s = d.slide(T('RQ2·RQ3 · 장소의 소리는 주로 연구자의 판단, 조성은 지역 단위로 거칠다', 'RQ2–RQ3 · Landmark sound is mostly authored; mode is set by region'), T('5 · 결과', '5 · Results'))
    d.stat(s, Inches(0.6), Inches(1.85), Inches(3.9), Inches(1.9), f'{100 * PV["eta_sq"]:.1f}%', T('장소 점수 분산 중 지역이 설명한 비율(η²)', 'of landmark-score variance explained by region (η²)'), ORANGE)
    d.stat(s, Inches(0.6), Inches(3.95), Inches(3.9), Inches(1.9), f'{n_pleas}/75', T('방문객 쾌적성이 조성을 정한 장소', 'places whose mode is set by Visitor Pleasantness'))
    picture(s, FIG / 'fig6_key_rules.png', Inches(4.9), Inches(1.65), h=Inches(4.3))
    tb(s, Inches(0.6), Inches(6.05), Inches(12.1), Inches(0.9),
       [T(f'쾌적성 17개 값이 6.7점 범위에 몰려 있고 {S["n_regions_within1_of_median"]}개 지역이 중앙값에서 1점 이내 → 작은 설문 차이가 장조/단조로 바뀐다.',
          f'The 17 Pleasantness values span 6.7 points and {S["n_regions_within1_of_median"]} regions sit within one point of the median, so small survey differences become major vs minor.')], 15)

    # 8 RQ4 accuracy
    s = d.slide(T('RQ4 · 생성 음원은 요청을 부분적으로만 따른다', 'RQ4 · Generated audio follows the request only in part'), T('5 · 결과', '5 · Results'))
    picture(s, RES / 'accuracy_both_rounds_slide.png', Inches(0.5), Inches(1.6), w=Inches(9.5))
    d.stat(s, Inches(10.25), Inches(1.75), Inches(2.5), Inches(1.6), f'{r1["mode_hits"]}→{r2["mode_hits"]}/10', T('요청 조성 일치(1차→2차)', 'mode matched (round 1→2)'))
    d.stat(s, Inches(10.25), Inches(3.5), Inches(2.5), Inches(1.6), '0/5', T('단조 요청 성공(두 차례)', 'minor requests honored'), ORANGE)
    d.stat(s, Inches(10.25), Inches(5.25), Inches(2.5), Inches(1.6), f'{T1["top3_hits"]}·{T2["top3_hits"]}/10', T('요청 템포가 상위 3 피크에 포함(우연 ≈1.5)', 'request among top-3 peaks (chance ≈1.5)'), GREEN)
    tb(s, Inches(0.6), Inches(6.2), Inches(9.4), Inches(0.8),
       [T('2차 향상에는 세종 요청 변경(단조→장조)과, 요청이 같은데 결과가 뒤바뀐 클립 05·06·08이 섞여 있다 → 문구 수정의 효과로 볼 수 없다.',
          'The round-2 gain mixes Sejong’s changed request (minor → major) with clips 05, 06 and 08 flipping under the same request, so it cannot be credited to rewording.')], 13, MUTED)

    # 9 Sejong
    s = d.slide(T('자동으로 맞은 95 BPM이 사람에게는 48 BPM으로 들렸다', 'An automatic 95 BPM match was heard at 48 BPM'), T('5 · 결과: 세종 사례', '5 · Results: the Sejong case'))
    stages = [(T('2차 Suno 원본', 'Round-2 Suno source'), '95.3', '48', ORANGE), (T('엄격한 95 BPM 재생성', 'Strict 95 BPM regeneration'), '95.3', '48', ORANGE),
              (T('+ 95 BPM 킥·림 덧입힘', '+ 95 BPM kick and rim'), '95.3', '47', ORANGE),
              (T('시간축 2.02× 보정 + 하이햇 교체', '2.02× time-axis fix + hi-hat'), '95.3', f'{HV["blind_tap_bpm"]:.0f}', GREEN)]
    tb(s, Inches(0.6), Inches(1.7), Inches(12.1), Inches(0.5), [[(T('목표 95 BPM   |   자동 측정   →   사람 블라인드 탭', 'Target 95 BPM   |   automatic   →   human blind tap'), {'bold': True, 'color': MUTED})]], 14)
    for i, (label, auto, human, col) in enumerate(stages):
        x = Inches(0.6 + i * 3.08)
        rect(s, x, Inches(2.3), Inches(2.9), Inches(2.6), line=col)
        tb(s, x + Inches(0.18), Inches(2.45), Inches(2.6), Inches(0.9), [label], 15, NAVY, True)
        tb(s, x + Inches(0.18), Inches(3.35), Inches(2.6), Inches(0.5), [T(f'자동 {auto}', f'auto {auto}')], 14, MUTED)
        tb(s, x + Inches(0.18), Inches(3.8), Inches(2.6), Inches(1.0), [f'{human} BPM'], 32, col, True)
    tb(s, Inches(0.6), Inches(5.15), Inches(12.1), Inches(1.8),
       [T('덧입힌 박은 기존의 느린 박의 세분으로 흡수되었다. 사람의 측정값(47)에서 시간축 전체를 보정해야 박이 목표로 들렸다(오차 1.1%, 사전 기준 ±5%).',
          'The added pulse was absorbed as a subdivision of the slow beat. Only correcting the whole time axis from the human measurement (47) moved the heard pulse to the target (1.1% error; criterion ±5% set in advance).'),
        [(T('한계: ', 'Limit: '), {'bold': True}), (T('1개 장소 · 1인 · 순차 진단 — 성공률 추정이 아님. ', 'one place, one listener, sequential diagnostic, not a success rate. '), {}),
         (T('음원 듣기', 'Listen to the audio'), {'link': AUDIO})]], 15)

    # 10 genre words
    s = d.slide(T('무엇이 조성을 바꾸나? 조성 단어보다 장르 단어', 'What changes the mode? Genre words more than mode words'), T('5 · 결과', '5 · Results'))
    picture(s, FIG / 'fig9_genre_words.png', Inches(0.6), Inches(1.7), w=Inches(8.6))
    d.stat(s, Inches(9.5), Inches(1.75), Inches(3.25), Inches(1.6), '0/5 → 3/3', T('강남: 원래 장르어 → “dark synth-pop”', 'Gangnam: original genre → “dark synth-pop”'), GREEN)
    d.stat(s, Inches(9.5), Inches(3.5), Inches(3.25), Inches(1.6), '0/3', T('아산: 같은 방법, 일반화 실패', 'Asan: same method, did not transfer'), ORANGE)
    d.stat(s, Inches(9.5), Inches(5.25), Inches(3.25), Inches(1.6), f'{PF["k"]}/{PF["n"]}', T('단조 요청 전체 성공(어떤 요인도 우연과 구별 안 됨)', 'all minor requests (no factor beats chance)'))

    # 11 Feedback loop
    s = d.slide(T('피드백 → 수정: 가장 큰 개선은 우리 자신의 규칙을 고친 데서 나왔다', 'Feedback → fixes: the biggest gains came from fixing our own rules'), T('6 · 개선 과정', '6 · Improvements'))
    rows = [(T('“complex” 키워드 충돌 → 세종 행정기관이 공장 스타일', '“complex” keyword collision → Sejong styled as a factory'), T('행정기관 범주 신설', 'New institutional category'), T('이후 생성 95.3 BPM', 'later generations at 95.3 BPM')),
            (T('세종 = 젊은 가족이 많은 계획도시(사용자 피드백)', 'Sejong is a planned city of young families (user feedback)'), T('장조 규칙에 추가', 'Added to the major rule'), T('D♯ 장조, 적합도 0.94', 'D♯ major, key-fit 0.94')),
            (T('단조 요청 옆 “warm, mellow”', '“warm, mellow” next to a minor request'), T('단조일 때 밝은 단어 제거', 'Remove bright words when minor'), T('필요하지만 충분하지 않음', 'necessary, not sufficient')),
            (T('자동 BPM ≠ 사람의 박', 'Automatic BPM ≠ human pulse'), T('시간축 보정 + 하이햇 교체', 'Time-axis fix + hi-hat'), T('1인 탭 96 BPM', 'one listener: 96 BPM')),
            (T('API 키가 공개 중계 서버 경유', 'API key routed through a public relay'), T('직접 호출로 변경', 'Direct calls'), T('모의 네트워크로 확인', 'checked with a mocked network'))]
    for i, (a, b, c) in enumerate(rows):
        y = Inches(1.8 + i * 1.0)
        rect(s, Inches(0.6), y, Inches(5.6), Inches(0.82))
        tb(s, Inches(0.75), y, Inches(5.35), Inches(0.82), [a], 14, INK, anchor=MSO_ANCHOR.MIDDLE)
        tb(s, Inches(6.35), y, Inches(0.4), Inches(0.82), ['→'], 20, BLUE, True, anchor=MSO_ANCHOR.MIDDLE)
        rect(s, Inches(6.8), y, Inches(3.2), Inches(0.82), line=BLUE, fill=RGBColor(0xFF, 0xFF, 0xFF))
        tb(s, Inches(6.95), y, Inches(3.0), Inches(0.82), [b], 14, NAVY, True, anchor=MSO_ANCHOR.MIDDLE)
        tb(s, Inches(10.2), y, Inches(2.55), Inches(0.82), [c], 13, MUTED, anchor=MSO_ANCHOR.MIDDLE)

    # 12 Limits and next steps
    s = d.slide(T('한계와 발전 방향', 'Limitations and next steps'), T('7 · 논의', '7 · Discussion'))
    tb(s, Inches(0.6), Inches(1.75), Inches(5.8), Inches(5.1),
       [[(T('한계', 'Limitations'), {'bold': True, 'color': ORANGE, 'size': 20})],
        T('• 한 제공자·한 모델의 음원 20곡 + 후속 약 20곡', '• 20 tracks + ~20 follow-ups, one provider and model'),
        T('• 후속 비교는 사전 등록되지 않음', '• Follow-up comparisons were not preregistered'),
        T('• 사람의 확인은 1인·1클립뿐', '• Only one listener checked one clip'),
        T('• 가중치는 가설, 장소 점수는 측정값 아님', '• Weights are hypotheses; landmark scores are not measured'),
        T('• 청취자·현장·접근성(RQ6–8) 데이터 없음', '• No listener, field or accessibility data yet (RQ6–8)'),
        T('• Gemini 실제 출력 미기록(수작업 모의)', '• No recorded Gemini output (hand-simulated)')], 15)
    tb(s, Inches(6.8), Inches(1.75), Inches(5.95), Inches(5.1),
       [[(T('발전 방향', 'Next steps'), {'bold': True, 'color': GREEN, 'size': 20})],
        T('1. 여러 청취자가 모든 클립을 블라인드 탭, 조성은 음악 전공자 확인', '1. Several listeners tap every clip blind; a musician checks mode'),
        T('2. 같은 요청을 여러 번 생성한 뒤에만 개선 주장', '2. Repeat each request before claiming a fix'),
        T('3. 장르 단어 가설을 더 많은 장소에서 시험', '3. Test the genre-word hypothesis at more places'),
        T('4. 성인 15–24명 청취자 실험(프로토콜 준비 완료)', '4. Listener study, 15–24 adults (protocol ready)'),
        T('5. 6–10개 지점 현장 사운드워크', '5. Field soundwalk at 6–10 sites'),
        T('6. 템포는 생성 대신 결정론적 보정으로', '6. Enforce tempo by deterministic correction')], 15)

    # 13 Conclusion
    s = d.slide(T('결론', 'Conclusion'), T('8 · 결론', '8 · Conclusion'))
    tb(s, Inches(0.6), Inches(1.8), Inches(12.1), Inches(3.6),
       [T('• 공식 통계 → 점수 → 사양 → 음원의 사슬을 끝까지 추적 가능하게 만들고, 앞의 네 연결을 계산·측정으로 검증했다.',
          '• The chain from official statistics to score, specification and audio is traceable end to end, and its first four links were tested.'),
        T('• 지역 순위는 그럴듯하지만 가중치에 민감하고, 장소 점수는 주로 연구자의 판단이며, 조성 규칙은 지역 단위로 거칠다.',
          '• The regional order is plausible but weight-sensitive, landmark scores are mostly authored, and the mode rule is coarse.'),
        T('• 생성 모델은 단조(0/5)와 사람이 느끼는 박을 보장하지 않는다. 템포는 결정론적 보정으로 맞출 수 있었다(1인, 1클립).',
          '• The generator guaranteed neither minor mode (0/5) nor the perceived pulse; deterministic correction fixed tempo (one listener, one clip).'),
        T('• 청취자가 의도한 순서를 듣는지는 준비된 다음 실험의 질문이다.', '• Whether listeners hear the intended order is the next, prepared experiment.')], 18, spacing=1.15)
    rect(s, Inches(0.6), Inches(5.45), Inches(12.1), Inches(1.4))
    tb(s, Inches(0.85), Inches(5.55), Inches(11.7), Inches(1.25),
       [[(T('자료 · ', 'Materials · '), {'bold': True, 'color': NAVY}), (T('코드·데이터', 'Code & data'), {'link': f'{REPO}/tree/{TAG}'}), ('   ·   ', {}),
         (T('웹 데모', 'Web demo'), {'link': DEMO}), ('   ·   ', {}), (T('생성 음원', 'Generated audio'), {'link': AUDIO})],
        [(f'{REPO}/tree/{TAG}', {'size': 12, 'color': MUTED})]], 16)
    d.prs.save(out)
    return d.n


def export_keynote(pptx, pdf):
    """Keynote silently fails to open a .pptx whose name contains Korean, so export via an ASCII-named copy."""
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(dir=HERE))
    src, out = tmp / 'deck.pptx', tmp / 'deck.pdf'
    shutil.copy(pptx, src)
    script = f'''with timeout of 300 seconds
tell application "Keynote"
set d to open (POSIX file "{src}")
delay 4
export d to (POSIX file "{out}") as PDF with properties {{PDF image quality:Best}}
close d saving no
end tell
end timeout'''
    subprocess.run(['osascript', '-e', script], check=True)
    shutil.move(out, pdf)
    shutil.rmtree(tmp)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--no-pdf', action='store_true')
    args = ap.parse_args()
    for lang, out in (('ko', HERE / 'national' / 'KSEF2027_National_발표자료_Moodscape.pptx'),
                      ('en', HERE / 'international' / 'KSEF2027_International_Presentation_Moodscape.pptx')):
        n = build(lang, out)
        print(f'{out.name}: {n} slides')
        if not args.no_pdf:
            export_keynote(out, out.with_suffix('.pdf'))
            print(f'  -> {out.with_suffix(".pdf").name}')


if __name__ == '__main__':
    main()
