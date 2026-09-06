# Moodscape Development Log

Date: 30 August 2026

---

# English Version

## 1. Purpose of today's work

Today's goal was to make the Moodscape prototype more reliable, transparent, and defensible. The earlier regional scores depended heavily on AI-assisted or manually reasoned Pleasantness/Eventfulness estimates. Those estimates were useful for early prototyping, but they were not equivalent to direct soundscape measurements.

We therefore rebuilt the regional scoring system around comparable official data for all 17 South Korean first-level regions. The revised prototype makes a clear distinction between measured input data, human-selected model weights, and direct soundscape evidence.

## 2. Data assembled and used

The revised model uses the following province-level sources:

- 2025 population and population density data for all 17 regions.
- 2024 domestic-tourism trip counts from the National Tourism Survey.
- 2023 noise and vibration complaints reported by the Ministry of Environment.
- Registered noise-emitting facilities reported by the Ministry of Environment.
- 2024 overall visitor satisfaction, crowding satisfaction, revisit intention, and recommendation intention from the National Tourism Survey.
- A separate 2024 Jeju visitor-survey summary for supporting regional context.
- Published soundscape research for Seoul and Daejeon, retained as external comparison evidence.

The official environmental and tourism variables are comparable across regions. Social-media comments and general public reviews were not inserted directly into the score because their samples are not consistent or representative across every province.

## 3. Reformed activity formula

The live prototype now calculates a regional Activity Proxy:

```text
Activity Proxy = 100 × (
    0.35 × normalized population density
  + 0.30 × normalized tourism trips per resident
  + 0.15 × normalized noise complaints per 100,000 residents
  + 0.10 × normalized noise-emitting facilities per 100,000 residents
  + 0.10 × normalized crowding pressure
)
```

Crowding pressure is calculated as:

```text
Crowding pressure = 100 − crowding satisfaction
```

Before weighting, each activity variable is log-transformed and normalized across the 17 regions:

```text
Normalized X =
[ln(1 + X) − minimum ln(1 + X)]
÷
[maximum ln(1 + X) − minimum ln(1 + X)]
```

The log transformation reduces the influence of extreme values. This means that a very densely populated region does not automatically receive the highest activity score. Density contributes 35% of the result, while tourism, noise, industrial-source, and perceived-crowding indicators contribute the remaining 65%.

## 4. Separate visitor-pleasantness calculation

Activity and pleasantness are not treated as the same concept. Visitor Pleasantness is calculated separately:

```text
Visitor Pleasantness =
    0.40 × overall satisfaction
  + 0.25 × recommendation intention
  + 0.20 × revisit intention
  + 0.15 × crowding satisfaction
```

This score provides visitor-perception context. It does not currently control the audio and is not presented as an ISO 12913 Pleasantness measurement.

## 5. Interface and implementation changes

The prototype was updated so that:

- All 17 regional baselines are calculated from the same reproducible model.
- The map tooltip identifies the displayed result as “Modelled activity.”
- Each regional panel contains a “Modelled proxy” badge.
- Users can expand “See data and calculation” to inspect the province's raw inputs, weights, activity score, and visitor-pleasantness score.
- Seoul and Daejeon display their direct soundscape research as comparison references only.
- The About page now explains that the inputs are measured but the weights are human-selected hypotheses.
- Earlier AI-assisted P/E estimates no longer drive the map or audio baseline.
- Landmark-level values remain illustrative offsets because comparable landmark-level measurements are not available.

## 6. Academic verification and DOI additions

Permanent DOI links were added for the principal academic references, including:

- Hong and Jeon’s Seoul soundwalk study: https://doi.org/10.1016/j.buildenv.2020.107327
- Kim, Kim, and Hong’s Daejeon study: https://doi.org/10.1016/j.apacoust.2024.110319
- Lee and Kim’s Seoul social-media soundscape study: https://doi.org/10.1371/journal.pone.0343393
- Zhao et al.’s iSonic accessibility study: https://doi.org/10.1145/1352782.1352786
- Russell’s circumplex model of affect: https://doi.org/10.1037/h0077714
- Chatty Maps: https://doi.org/10.1098/rsos.150690

Official government reports and ISO standards do not necessarily have DOIs, so they are linked through their official report or catalogue pages instead.

## 7. Checks completed

The scoring calculation was independently checked for all 17 regions. Every activity and pleasantness output remained within the expected 0–100 range. The CSV source register was also parsed successfully after the DOI additions, and no whitespace or patch-format errors were detected.

The revised Activity Proxy produced a regional range from approximately 32.9 to 61.3 in the current dataset. This narrower result is expected because the model combines multiple variables rather than assigning extreme emotional scores manually.

## 8. Scientific limitations and next step

The revised prototype is more reproducible, but it does not prove that the formula predicts perceived soundscape mood. The official inputs are real measurements; the weights are reasoned starting values rather than coefficients learned from listener data.

The strongest next step remains a controlled soundscape and listener study. A defensible pilot would collect recordings from at least 30 locations across 6–10 provinces, cover two time periods per location, and obtain approximately 10 independent ratings for each site and time. Those observations could be used to test correlations, estimate model coefficients, compare alternative formulas, and measure prediction error.

## 9. Files affected or produced

- `data.js` — official inputs and reproducible composite calculation.
- `ui.js` — model status, calculation breakdown, and limitations in the regional panel.
- `map.js` — modelled-activity tooltip wording.
- `style.css` — model-detail interface styling.
- `about.html` — revised methodology, limitations, sources, and DOI links.
- `research/moodscape_external_sources.csv` — verified academic DOI links and official-source records.
- `research/moodscape_15_regions_official_proxies.csv` — environmental and demographic proxy data.
- `research/moodscape_2024_national_tourism_province_perception.csv` — official visitor-perception table.
- `research/moodscape_2024_jeju_visitor_survey_summary.csv` — Jeju visitor-survey summary.
- `research/soundscape_relationship_validation_protocol.md` — proposed validation method.
- `research/soundwalk_observation_template.csv` — field-observation structure.

---

# 한국어 버전

## 1. 오늘 작업의 목적

오늘의 목표는 Moodscape 프로토타입을 더 신뢰할 수 있고, 투명하며, 설명 가능한 형태로 개선하는 것이었다. 이전 지역 점수는 AI의 도움을 받은 추정치 또는 사람이 판단한 Pleasantness/Eventfulness 추정치에 크게 의존했다. 이러한 추정치는 초기 프로토타입 제작에는 유용했지만, 실제 현장에서 측정된 사운드스케이프 자료와 동일하지 않았다.

따라서 대한민국 17개 광역자치단체에 공통으로 적용할 수 있는 공식 통계를 사용하여 지역 점수 모델을 다시 구성했다. 새 프로토타입은 실제 측정된 입력 자료, 사람이 정한 모델 가중치, 그리고 직접적인 사운드스케이프 연구 근거를 명확히 구분한다.

## 2. 수집하고 사용한 데이터

개선된 모델은 다음과 같은 지역 단위 자료를 사용한다.

- 17개 지역의 2025년 인구와 인구밀도
- 국민여행조사의 2024년 국내 관광 여행 횟수
- 환경부의 2023년 소음·진동 민원 건수
- 환경부에 등록된 소음 배출시설 수
- 2024년 국민여행조사의 전반적 만족도, 혼잡도 만족도, 재방문 의향, 추천 의향
- 제주 지역 맥락을 보완하기 위한 2024년 제주 방문관광객 실태조사 요약
- 서울과 대전의 출판된 사운드스케이프 연구 결과. 이 자료는 외부 비교 근거로만 유지했다.

공식 환경·관광 변수는 모든 지역에서 비교 가능한 형식이다. 소셜미디어 댓글과 일반 사용자 리뷰는 지역마다 표본 수와 대표성이 일관되지 않기 때문에 점수에 직접 포함하지 않았다.

## 3. 개선된 활동성 공식

현재 프로토타입은 다음과 같은 지역 활동성 대리점수(Activity Proxy)를 계산한다.

```text
활동성 대리점수 = 100 × (
    0.35 × 정규화된 인구밀도
  + 0.30 × 정규화된 주민 1인당 관광 여행 횟수
  + 0.15 × 정규화된 인구 10만 명당 소음 민원
  + 0.10 × 정규화된 인구 10만 명당 소음 배출시설
  + 0.10 × 정규화된 혼잡 압력
)
```

혼잡 압력은 다음과 같이 계산한다.

```text
혼잡 압력 = 100 − 혼잡도 만족도
```

가중치를 적용하기 전에 각 활동성 변수에 로그 변환을 적용하고, 17개 지역을 기준으로 0–1 범위로 정규화한다.

```text
정규화된 X =
[ln(1 + X) − ln(1 + X)의 최솟값]
÷
[ln(1 + X)의 최댓값 − ln(1 + X)의 최솟값]
```

로그 변환은 극단적으로 큰 값의 영향력을 줄인다. 따라서 인구밀도가 매우 높다는 이유만으로 해당 지역이 자동으로 가장 활동적인 지역으로 결정되지 않는다. 인구밀도는 전체 결과의 35%만 차지하며, 관광·소음·산업적 소음원·체감 혼잡도 지표가 나머지 65%를 구성한다.

## 4. 별도의 방문객 쾌적성 계산

활동성과 쾌적성은 같은 개념으로 처리하지 않았다. 방문객 쾌적성은 다음과 같이 별도로 계산한다.

```text
방문객 쾌적성 =
    0.40 × 전반적 만족도
  + 0.25 × 추천 의향
  + 0.20 × 재방문 의향
  + 0.15 × 혼잡도 만족도
```

이 점수는 방문객 인식에 대한 추가 맥락을 제공한다. 현재 오디오를 제어하지 않으며, ISO 12913 방식으로 직접 측정된 Pleasantness 점수라고 표현하지 않는다.

## 5. 인터페이스 및 구현 변경 사항

프로토타입을 다음과 같이 변경했다.

- 17개 지역의 기본 점수를 동일한 재현 가능한 모델로 계산한다.
- 지도 툴팁에 표시되는 결과를 “Modelled activity”로 명시한다.
- 각 지역 패널에 “Modelled proxy” 배지를 표시한다.
- 사용자가 “See data and calculation”을 펼쳐 원자료, 가중치, 활동성 점수, 방문객 쾌적성 점수를 확인할 수 있다.
- 서울과 대전의 직접 사운드스케이프 연구는 비교 자료로만 표시한다.
- About 페이지에서 입력 자료는 측정값이지만 가중치는 사람이 정한 가설임을 설명한다.
- 이전의 AI 보조 P/E 추정치는 더 이상 지도와 오디오의 지역 기본값을 결정하지 않는다.
- 명소 단위 점수는 동일한 수준의 측정 자료가 없기 때문에 예시적인 지역 내 보정값으로 남겨 두었다.

## 6. 학술 자료 검증 및 DOI 추가

주요 학술 자료에 다음과 같은 영구 DOI 링크를 추가했다.

- Hong과 Jeon의 서울 사운드워크 연구: https://doi.org/10.1016/j.buildenv.2020.107327
- Kim, Kim, Hong의 대전 연구: https://doi.org/10.1016/j.apacoust.2024.110319
- Lee와 Kim의 서울 소셜미디어 사운드스케이프 연구: https://doi.org/10.1371/journal.pone.0343393
- Zhao 등의 iSonic 접근성 연구: https://doi.org/10.1145/1352782.1352786
- Russell의 정서 원형 모델: https://doi.org/10.1037/h0077714
- Chatty Maps 연구: https://doi.org/10.1098/rsos.150690

정부 보고서와 ISO 표준에는 DOI가 없는 경우가 많으므로, 해당 자료에는 공식 보고서 또는 공식 카탈로그 링크를 사용했다.

## 7. 완료한 검증

17개 전 지역에 대해 점수 계산을 독립적으로 확인했다. 모든 활동성 점수와 쾌적성 점수는 예상 범위인 0–100 안에 있었다. DOI를 추가한 뒤 CSV 출처 목록도 정상적으로 읽혔으며, 패치 형식이나 공백 오류가 없는지 확인했다.

현재 자료에서 개선된 활동성 대리점수는 약 32.9에서 61.3 사이로 나타났다. 이 범위가 이전보다 좁은 것은 감정 점수를 수동으로 극단적으로 배정하는 대신 여러 변수를 함께 사용했기 때문이다.

## 8. 과학적 한계와 다음 단계

개선된 프로토타입은 이전보다 재현 가능하지만, 이 공식이 사람들이 느끼는 사운드스케이프 분위기를 정확히 예측한다는 사실을 증명하지는 않는다. 공식 입력 자료는 실제 측정값이지만, 가중치는 청취자 자료로 학습된 계수가 아니라 논리적으로 설정한 초기값이다.

가장 중요한 다음 단계는 통제된 사운드스케이프 녹음 및 청취자 평가 실험이다. 방어력 있는 파일럿 연구를 위해서는 6–10개 시·도에 걸쳐 최소 30개 장소를 선정하고, 장소마다 두 시간대에 녹음하며, 각 장소·시간 조건마다 약 10명의 독립적인 평가를 수집하는 것이 좋다. 이 관측 자료를 이용하면 상관관계를 검정하고, 모델 계수를 추정하고, 여러 공식을 비교하며, 예측 오차를 계산할 수 있다.

## 9. 변경 또는 생성된 파일

- `data.js` — 공식 입력 자료와 재현 가능한 복합점수 계산
- `ui.js` — 모델 상태, 계산 상세 정보, 한계 표시
- `map.js` — 지도 툴팁의 활동성 표현
- `style.css` — 모델 상세 인터페이스 스타일
- `about.html` — 방법론, 한계, 출처, DOI 링크 수정
- `research/moodscape_external_sources.csv` — 검증된 DOI와 공식 출처 기록
- `research/moodscape_15_regions_official_proxies.csv` — 환경 및 인구 관련 대리변수 자료
- `research/moodscape_2024_national_tourism_province_perception.csv` — 공식 방문객 인식 자료
- `research/moodscape_2024_jeju_visitor_survey_summary.csv` — 제주 방문객 조사 요약
- `research/soundscape_relationship_validation_protocol.md` — 검증 방법 제안
- `research/soundwalk_observation_template.csv` — 현장 관측용 데이터 구조
