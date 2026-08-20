# Hanwha Eagles Data Center

한화 이글스의 시즌·선수 기록을 원자료에서 재계산하고, 영구결번과 구단 역사를 데이터 박물관 형태로 보존하는 Streamlit 멀티페이지 대시보드입니다.

## 현재 기능

- 한화 이글스 오렌지·딥 네이비 기반 공통 디자인 시스템
- `st.navigation` 카테고리 메뉴
- 2025 시즌 요약·순위·공격/수비·관중 KPI를 한 화면에 배치한 데이터센터 홈
- 60초 자동 갱신 2026 경기 센터: 다음 경기와 최근 결과, 제공되는 경우 현재 점수
- 시즌 아카이브·영구결번 전시관·KBO 공식 기록으로 이동하는 실제 링크 버튼
- 영구결번 전시관: 송진우(21), 정민철(23), 장종훈(35), 김태균(52)
- 시즌 기록·선수 아카이브의 데이터 미확보 상태 처리
- 데이터 매니페스트와 알려진 한계 공개
- 파일 수정시각·크기를 캐시 키에 포함하는 JSON/Parquet/이미지 로더

## 데이터 원칙

- 수치는 원자료의 분자·분모에서 재계산합니다.
- 정규시즌, 포스트시즌, 시범경기, 퓨처스를 섞지 않습니다.
- 데이터가 없거나 수집이 실패한 값을 0으로 바꾸지 않습니다.
- 선수는 이름만으로 병합하지 않고 출처의 고유 ID·시즌·팀·포지션을 사용합니다.
- 투구 이닝은 소수로 저장하지 않고 아웃카운트로 정규화합니다.

## 현재 데이터 출처

- KBO 공식 선수 기록
- KBO 40주년 레전드 40 보도자료

현재 포함된 수치는 영구결번 선수의 KBO 정규시즌 통산 기록과 KBO가 공개한 2025 팀 성적·관중 요약입니다. KBO `robots.txt`의 자동 수집 금지를 확인해 페이지 크롤링은 중단했으며, 상세 계획은 `CRAWLING_PLAN.md`에 기록했습니다. STATIZ도 공식 API 또는 서면 허가 없이는 자동 수집하지 않습니다.

2026 경기 센터는 TheSportsDB의 공개 API를 60초 캐시로 조회합니다. 무료 제공 범위에서는 일정과 최근 결과가 중심이며 라이브 점수가 지연 또는 미제공될 수 있습니다. 이 경우 점수를 추측하지 않고 `점수 업데이트 대기`로 표시합니다.

## 실행

```bash
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

## 저장소와 배포

- GitHub: `https://github.com/robinho0329/hanwha-eagles-dashboard`
- 브랜치: `master`
- 저장소 공개 범위: public
- Streamlit Cloud: `https://ovp72menatzlgkichkctpj.streamlit.app`
- 배포 확인: 홈과 영구결번 전시관 렌더링 확인

## 테스트

```bash
python -m pytest -q
python -m compileall app.py _lib.py views tests
```

## 데이터 반입

`scripts/00_probe_sources.py`는 대상 페이지를 요청하기 전에 robots.txt만 검사하며, 현재 KBO는 차단 상태로 종료됩니다. 서면 허가를 받았거나 사용자가 적법하게 제공한 팀 기록 HTML은 `scripts/01_parse_kbo_team_seasons.py`로 네트워크 없이 검증·정규화할 수 있습니다.

`scripts/02_fetch_thesportsdb_games.py`는 문서화된 API에서 다음 경기와 최근 결과를 raw/processed로 저장합니다. `scripts/03_fetch_licensed_images.py`는 매니페스트에 재사용 라이선스·출처·크레딧과 선수 식별정보가 완비된 이미지만 다운로드합니다. 예시는 `data/mappings/image_manifest.example.json`을 참고합니다.

`scripts/04_fetch_thesportsdb_window.py`는 기준일 전후 7일의 KBO 날짜 API를 수집해 한화 경기만 경기 ID로 정규화합니다. 바르셀로나 프로젝트 지표를 야구에 대응시키는 기준은 `BARCELONA_REFERENCE.md`에 기록했습니다.

## 목표 데이터 범위

- 팀 역사: 1986~2025 완료 시즌
- 선수 상세: 2015~2025 완료 시즌
- 2026: 진행 시즌으로 기준일과 함께 별도 표시
- 포스트시즌·시범경기·퓨처스: 검증 후 별도 데이터셋으로 확장

## 주요 한계

- 실제 팀 시즌·선수 시즌 processed 데이터 수집 전입니다.
- 선수 사진은 라이선스와 인물 식별이 확인되기 전까지 표시하지 않습니다.
- 앱의 AI 콘셉트 이미지는 시각적 참고용이며 실제 선수·경기·통계를 나타내지 않습니다.
- 영구결번 타임라인 설명은 각 KBO 출처를 바탕으로 요약한 편집 문장입니다.
