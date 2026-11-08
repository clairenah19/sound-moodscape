# 참가 등록 폼 입력용 초록 / Registration-form abstracts

두 초록 모두 등록 폼에 직접 입력하는 텍스트이다(사진·도표·그래프 첨부 불가). 수치는 논문과 같은 출처(research/paper/stats.json)이다.

## KSEF National(국내분야) — 연구초록 (국문, 800자 내외)

지도는 장소의 차이를 색과 글자로만 전달하므로 화면을 볼 수 없는 사람에게는 어느 지역이 붐비고 한적한지가 전달되지 않는다. 또한 사운드스케이프 연구는 장소의 분위기가 사람이 지각한 것이며 계산한 숫자 하나로 대신할 수 없음을 보여준다. 본 연구는 공식 지역 통계를 음악으로 바꾸는 웹 프로토타입 Moodscape를 개발하고, 데이터에서 소리까지 이어지는 사슬의 각 연결을 독립된 연구 질문으로 검증하였다. 17개 시·도의 공식 지표 9종(인구밀도, 관광, 방문객 설문, 소음 민원 등)으로 활동 점수와 방문객 쾌적성을 계산하고, 75개 장소의 템포·조성·스타일을 규칙으로 정한 뒤 Suno로 10곡씩 두 차례(총 20곡) 생성하여 librosa로 템포와 조성을 측정하였다. 가중치를 10,000번 교란한 결과 지역 순위 일치의 중앙값은 0.87이었으나 0.9 이상을 유지한 비율은 42%에 그쳤고, 장소 점수 분산 중 지역이 설명한 비율은 12.2%였다. 요청한 조성은 1차 5/10, 2차 7/10에서 검출되었으며 단조 요청 5건은 모두 장조로 생성되었다. 요청 템포는 상위 3개 리듬 피크에 7/10, 9/10 포함되어 우연 기대값(약 1.5)보다 많았지만, 세종 클립은 자동 측정 95.3 BPM이 청취자에게 48 BPM으로 들렸고 시간축 보정과 하이햇 교체 후 96 BPM으로 들렸다. 장르 단어를 바꾸자 강남은 단조 0/5에서 3/3이 되었으나 아산에서는 일반화되지 않았다. 결론적으로 사슬은 끝까지 추적 가능하지만 가중치, 장소 점수, 생성 모델의 조성·박 재현이 약한 연결이다. 향후 여러 청취자의 블라인드 평가, 성인 15–24명 청취자 실험, 현장 사운드워크로 지각과의 관계를 검증할 계획이다.

## KSEF 2027 International — Abstract (English, about 250 words)

**Motivation and objectives.** Maps show differences between places only visually, so people who cannot see the screen miss them. Soundscape research also shows that atmosphere is perceived, not a single computed number. This project built Moodscape, a web prototype that turns official regional statistics into music for South Korean places, and tested each link from data to sound separately.

**Methodology and results.** Nine official indicators for 17 provinces produce an activity score and a visitor-pleasantness score. Rules turn them into tempo, mode and style for 75 places, and 20 tracks generated with Suno in two rounds were measured with librosa. Under 10,000 perturbed weight sets the regional ranking kept a median agreement of 0.87, but only 42% stayed above 0.9, and region explained only 12.2% of landmark-score variance. The requested mode was detected in 5/10 and 7/10 tracks, and all five minor-key requests came back major. The requested tempo was among the three strongest rhythmic peaks in 7/10 and 9/10 clips, against about 1.5 expected by chance. Yet a clip measured at 95.3 BPM was tapped at 48 BPM by a listener, and was heard at 96 BPM only after time-axis correction. Changing genre words turned Gangnam from 0/5 to 3/3 minor but did not transfer to a second place.

**Conclusions and future plans.** The chain is traceable end to end, but the weights, the authored landmark scores and the generator’s control of mode and pulse are its weak links. Next steps are blind tapping by several listeners, a listener experiment with 15–24 adults, and a field soundwalk.
