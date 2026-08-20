# KBO 데이터 수집 계획

## 원칙

- KBO 공식 공개 기록을 우선한다.
- STATIZ는 공식 API 또는 서면 허가 없이는 자동 수집하지 않는다.
- 한 요청으로 여러 시즌을 얻을 수 있는 페이지를 우선해 요청 수를 최소화한다.
- 원본 HTML, 수집 시각, URL, 상태코드, 해시를 함께 보존한다.
- 실패 시 기존 정상 processed 파일을 덮어쓰지 않는다.
- 정규시즌·포스트시즌·시범경기·퓨처스를 데이터셋 수준에서 분리한다.

## 단계

1. `00_probe_sources.py`
   - 대상 페이지보다 먼저 robots.txt만 요청해 자동 수집 허용 여부를 점검한다.
   - 금지된 경우 대상 URL을 요청하지 않고 실패 종료한다.
   - 예상 시간: 5~15초
2. `01_parse_kbo_team_seasons.py`
   - 서면 허가를 받았거나 사용자가 적법하게 제공한 HTML만 오프라인에서 처리한다.
   - 네트워크 요청 없이 시즌별 표를 `team_seasons.parquet`으로 정규화한다.
   - 예상 시간: 5~15초
3. `02_fetch_kbo_player_seasons.py` — 예정
   - 시즌·타자/투수 페이지를 낮은 빈도로 수집한다.
   - 선수 ID, 시즌, 팀, 포지션을 보존한다.
   - 예상 시간: 10~30분
4. `03_fetch_kbo_attendance.py` — 예정
   - 경기별 관중을 시즌·구장·홈팀 단위로 저장한다.
   - 예상 시간: 3~10분
5. `04_fetch_kbo_schedule_results.py` — 예정
   - 일정과 결과를 경기 ID 중심으로 정규화한다.
   - 예상 시간: 3~10분
6. `10_normalize_entities.py` 이후 processed 빌드·검증 — 예정

## 재시도와 체크포인트

- 연결 실패와 5xx만 최대 3회 재시도한다.
- 재시도 간격은 2초, 4초, 8초로 증가시킨다.
- 4xx는 즉시 실패 처리한다.
- 각 성공 응답에 SHA-256을 기록한다.
- processed 출력은 임시 파일에 쓴 뒤 원자적으로 교체한다.
- 시즌 단위 수집기는 성공한 시즌 체크포인트를 남긴다.

## 초기 데이터 계약

`team_seasons.parquet`

- `season`, `competition`, `rank`
- `team_id`, `team_name`
- `games`, `wins`, `losses`, `draws`
- `batting_average`, `era`, `win_rate`
- `season_complete`, `as_of_date`
- `source_url`, `fetched_at`, `raw_sha256`

## 중단 조건

- robots.txt 또는 이용약관에서 자동 수집 금지가 확인될 때
- 필수 열이 사라지거나 표 구조가 예상과 다를 때
- 팀별 승패 합계와 경기 수의 계약 검증이 실패할 때
- 동일 URL에서 반복적인 403·429가 발생할 때

## 2026-08-20 사전 점검 결과

- KBO `robots.txt`가 일반 자동 수집기에 `Disallow: /`를 반환해 KBO 페이지 크롤링은 중단했다.
- 사전 점검 중 생성된 결과물은 앱 데이터에서 제외하고 `work/quarantine/`으로 격리했다.
- 향후 허용 경로는 KBO의 서면 허가 또는 공식 API, 재사용이 명시된 라이선스 데이터셋,
  사용자가 적법하게 확보해 제공한 파일의 오프라인 처리로 제한한다.
- STATIZ 역시 공식 API 또는 서면 허가 없이는 자동 수집하지 않는다.
