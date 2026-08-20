# HANDOFF

## 프로젝트 구조

- `app.py`: Streamlit 진입점과 카테고리별 내비게이션
- `_lib.py`: CSS, 팔레트, 수정시각 기반 파일 로더, 공통 UI, 이닝 변환
- `views/`: 홈, 시즌 기록, 선수 아카이브, 영구결번 전시관, 데이터 범위
- `data/raw/`: 원본 응답. Git 제외
- `data/processed/`: 앱이 읽는 검증 완료 데이터
- `data/mappings/`: 팀·선수 ID 및 alias
- `data/checkpoints/`: 수집 재개 체크포인트. Git 제외
- `assets/`: 라이선스가 기록된 실제 자산과 AI 생성 자산 분리
- `scripts/`: 다음 단계의 수집·정규화 스크립트 위치
- `tests/`: 캐시, 이닝, 데이터 계약, AppTest

## 데이터 수집 스크립트 실행 순서

자동 수집 허용 여부를 먼저 확인하고 다음 순서를 유지한다.

1. `00_probe_sources.py` — robots.txt만 확인, 5~15초. 현재 KBO는 차단 종료
2. `01_parse_kbo_team_seasons.py` — 허가·사용자 제공 HTML 오프라인 정규화, 5~15초
3. `02_fetch_thesportsdb_games.py` — 다음 경기·최근 결과 API 스냅샷, 5~15초
4. `03_fetch_licensed_images.py` — 승인된 이미지 매니페스트, 이미지당 1~5초
5. `04_fetch_thesportsdb_window.py` — 기준일 전후 7일, 10~40초
6. KBO 선수·관중·일정 수집 — 서면 허가 또는 공식 API 확보 후
6. `10_normalize_entities.py` — 팀·선수 정규화, 1~3분
7. `11_build_team_seasons.py` — 팀 processed, 1~5분
8. `12_build_player_seasons.py` — 선수 processed, 1~5분
9. `90_validate_data.py` — 계약·집계 검증, 1~5분

실측 시간은 첫 성공 실행 뒤 이 문서에 기록한다.

## 현재 데이터 스키마

### `retired_numbers.json`

- `player_id`, `number`, `name`, `position`, `years`
- `headline`, `stats`, `milestones`, `source_url`
- 통계 범위는 KBO 정규시즌 통산

### 예정 `team_seasons.parquet`

- `season`, `competition`, `team_id`, `team_name`
- `games`, `wins`, `losses`, `draws`, `rank`
- `runs`, `runs_allowed`, `attendance_total`, `attendance_games`
- `source_url`, `fetched_at`, `as_of_date`, `season_complete`

### 예정 선수 시즌 테이블

- 공통: `season`, `competition`, `player_id`, `player_name`, `team_id`, `position`
- 타자: `pa`, `ab`, `hits`, `home_runs`, `walks`, `hbp`, `sacrifice_flies`
- 투수: `outs_recorded`, `earned_runs`, `hits`, `walks`, `strikeouts`
- AVG/OBP/SLG/ERA/WHIP는 앱 표시 전에 processed 단계에서 재계산

## 자주 발생하는 함정

- `@st.cache_data` 키에 경로만 넣지 않는다. `_lib.py` 공통 로더 사용.
- `40 2/3`이닝을 `40.2`로 변환하지 않는다. 아웃카운트로 저장.
- 이름만으로 선수와 사진을 연결하지 않는다.
- 비율 지표를 선수별 단순 평균하지 않는다.
- 정규시즌과 포스트시즌을 합산하지 않는다.
- 원자료 결측·미제공·수집 실패·실제 0을 구분한다.
- 2026 시즌은 진행 중이며 `as_of_date`가 필수다.
- STATIZ는 허가 또는 공식 API 없이 자동 수집하지 않는다.
- KBO도 현재 robots.txt가 전체 자동 수집을 막으므로 대상 페이지를 요청하지 않는다.

## 현재 완료 상태

- [x] D 드라이브 독립 프로젝트 생성
- [x] 공통 테마와 수정시각 기반 로더
- [x] 고밀도 데이터센터 홈·영구결번·데이터 범위 초기 화면
- [x] 홈 링크 버튼 활성화와 2026 경기 센터 60초 자동 갱신
- [x] 2026-08-13~27 날짜 API 15회 수집, 한화 경기 7건 정규화
- [x] Barcelona 지표의 야구 대응표와 우선순위 작성
- [x] 영구결번 4명 KBO 공식 통산 기록
- [x] 단위 테스트와 AppTest 초안
- [x] KBO 데이터 접근성 프로브: robots.txt 차단 확인, fail-closed 적용
- [x] 허가·사용자 제공 HTML용 오프라인 팀 시즌 파서
- [ ] 팀·선수 processed 데이터
- [ ] 실제 이미지 라이선스 확보
- [x] GitHub public 원격 저장소와 `master` 푸시
- [x] Streamlit Community Cloud 배포 및 화면 확인

## 알려진 한계

- 팀 시즌과 일반 선수 시즌 데이터는 아직 수집하지 않았다.
- TheSportsDB 무료 API는 진짜 이닝별 라이브스코어를 보장하지 않아 일정·최근 결과 위주로 표시한다.
- 선수 사진을 표시하지 않는다.
- 영구결번 지정일은 공식 출처 검증 전이므로 아직 노출하지 않는다.
- 디자인 콘셉트 이미지 속 얼굴·로고·수치는 실제 데이터로 사용하지 않는다.

## 남은 작업

1. KBO 서면 허가·공식 API 또는 재사용 허용 데이터셋 확보
2. 허가된 원본 파일 반입과 출처·라이선스 기록
3. 팀·선수 ID 매핑
4. 2015~2025 데이터 구축
5. 홈 KPI·시즌 기록·선수 아카이브 활성화
6. 라이선스 확인 이미지 추가
7. 경기·상대전적·퓨처스 순차 확장

## 배포 정보

- 로컬 경로: `D:\workspace\hanwha-eagles-dashboard`
- 진입점: `app.py`
- 배포 브랜치: `master`
- GitHub 원격: `https://github.com/robinho0329/hanwha-eagles-dashboard`
- 저장소 공개 범위: public
- Streamlit URL: `https://ovp72menatzlgkichkctpj.streamlit.app`
- 배포 확인일: 2026-08-20
- 확인 범위: 홈 렌더링, 영구결번 전시관 이동 및 KBO 출처 링크 표시
