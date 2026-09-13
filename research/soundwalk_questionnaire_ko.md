# Moodscape 사운드워크 설문지 (한국어)

Translated from `soundscape_relationship_validation_protocol.md` for in-field use at Korean
sites. This is a translation for data collection, **not** a validated psychometric
instrument — the protocol itself calls for "a validated Korean translation or
translation/back-translation and a pilot before field deployment" before this is used for
anything beyond an initial pilot. Treat this file as the starting draft that back-translation
step should work from, not a finished instrument.

---

## 안내문 (참가자에게 읽어줄 문구)

안녕하세요. 저희는 이 장소의 소리 환경에 대한 짧은 설문을 진행하고 있습니다. 정답이나 오답은
없으며, 지금 이 순간 느끼시는 그대로 응답해 주시면 됩니다. 응답에는 약 2분이 소요됩니다.
이름은 기록하지 않으며, 응답은 연구 목적으로만 사용됩니다.

## 본 설문 — 8개 항목 (5점 척도)

다음 문장에 대해 **지금 이 장소의 주변 소리 환경**을 기준으로 동의하는 정도를 선택해 주세요.

> "저는 현재 이 장소의 주변 소리 환경이 ___하다고 생각한다."

| # | 한국어 | English (reference) | 1 (전혀 아니다) | 2 | 3 (보통이다) | 4 | 5 (매우 그렇다) |
|---|---|---|---|---|---|---|---|
| 1 | 쾌적하다 | pleasant | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | 혼란스럽다 | chaotic | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | 활기차다 | vibrant | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | 단조롭다 | uneventful | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | 차분하다 | calm | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | 거슬린다 | annoying | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | 사건이 많다 | eventful | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | 지루하다 | monotonous | ☐ | ☐ | ☐ | ☐ | ☐ |

Attribute order is fixed to match the protocol's ISO 12913 instrument — do not reorder these
8 rows between sites, per the protocol's "Attribute order should be fixed" instruction.

*Note on item 4/8: "단조롭다" (monotonous) and "지루하다" (repetitive/uneventful) are close in
Korean; the back-translation pass should confirm these map distinctly to "monotonous" and
"uneventful" and don't collapse into synonyms for Korean speakers.*

## 소리 발생원 인지도

다음 소리 종류가 이 장소에서 **얼마나 지배적으로** 들리는지 표시해 주세요. (1 = 전혀 들리지 않음, 5 = 매우 지배적임)

| 소리 종류 | English | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 교통 소음 (자동차, 버스 등) | traffic | ☐ | ☐ | ☐ | ☐ | ☐ |
| 기계 소음 (공사, 환기 장치 등) | other mechanical | ☐ | ☐ | ☐ | ☐ | ☐ |
| 사람 소리 (대화, 발걸음 등) | human | ☐ | ☐ | ☐ | ☐ | ☐ |
| 자연 소리 (새, 바람, 물소리 등) | natural | ☐ | ☐ | ☐ | ☐ | ☐ |

## 전반적 평가 및 배경 정보

- 이 소리 환경이 이 장소에 **적절하다고** 생각하십니까? (1 전혀 아니다 – 5 매우 그렇다): ☐1 ☐2 ☐3 ☐4 ☐5
- 연령대: ☐10대 ☐20대 ☐30대 ☐40대 ☐50대 ☐60대 이상
- 청력에 어려움이 있으십니까?: ☐예 ☐아니오 ☐응답 안 함
- 현재 이 지역의: ☐거주자 ☐방문객
- 이 장소에 대한 친숙도 (1 처음 방문 – 5 매우 익숙함): ☐1 ☐2 ☐3 ☐4 ☐5

*(이름은 기록하지 않습니다 / Names are not collected in the analysis file, per protocol.)*

---

## Field-recorder checklist (not read to participants)

Recorded once per site-time window, alongside the ratings above — matches the columns in
`research/soundwalk_observation_template.csv`:

- LAeq over the rating interval (계기 사용, 기록 필수)
- 분당 보행자 수 / 분당 차량 수
- 위도·경도, 날짜, 시작 시각, 소요 시간
- 기온, 강수 여부, 바람 상태
- 평일/주말, 평상시/축제 여부
- 토지이용 구분 (상업/주거/공원 등)

## Analysis pipeline this feeds

Ratings collected on this form map directly onto `isoCoordinates()` in
`research/iso_pe_calculator.js`:

```js
const { isoCoordinates } = require("./iso_pe_calculator.js");
isoCoordinates({
  pleasant: 4, annoying: 2, calm: 3, chaotic: 3,
  vibrant: 4, monotonous: 2, eventful: 4, uneventful: 2,
});
// → { pleasantness: 0.354, eventfulness: 0.354 }
```

No real responses have been collected against this form yet — see DEVELOPMENT_PLAN2.md
Priority 1.
