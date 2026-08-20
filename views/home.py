"""High-density home dashboard based only on verified KBO records."""

import html

import streamlit as st

from _lib import PROCESSED, load_json, setup_page, source_footer


setup_page()
museum = load_json(PROCESSED / "retired_numbers.json")
players = museum.get("players", [])


def esc(value: object) -> str:
    return html.escape(str(value))


def people_cards(keys: list[str], position: str) -> str:
    rows = []
    for player in (item for item in players if item["position"] == position):
        stat_key = next((key for key in keys if key in player["stats"]), next(iter(player["stats"])))
        rows.append(
            f'<div class="dc-person"><div class="dc-person-no">{player["number"]}</div>'
            f'<div class="dc-person-name">{esc(player["name"])}<small>{esc(player["position"])} · {esc(player["years"])}</small></div>'
            f'<div class="dc-person-stat">{esc(player["stats"][stat_key])}</div></div>'
        )
    return "".join(rows)


st.markdown(
    """
    <div class="dc-topbar">
      <div class="dc-title">EAGLES DATA CENTER <i>↗</i></div>
      <div class="dc-badge">VERIFIED DATA · 2025 ARCHIVE</div>
    </div>
    <div class="dc-grid">
      <section class="dc-panel dc-hero">
        <div class="dc-kicker">2025 SEASON ARCHIVE · RIDE THE STORM</div>
        <h1>2위, 다시 높이 날아오른 이글스</h1>
        <div class="dc-hero-sub">REGULAR SEASON · PLAYOFF DIRECT</div>
        <div class="dc-record">
          <div class="dc-mark">E</div><div class="dc-vline"></div>
          <div><div class="dc-record-main">한화 이글스 · 83승 4무 57패</div>
          <div class="dc-record-sub">144경기 · 승률 .593 · KBO 정규시즌 2위</div></div>
        </div>
        <div class="dc-actions"><div class="dc-btn dc-btn-primary">시즌 아카이브</div>
        <div class="dc-btn">KBO 공식 기록 ↗</div></div>
      </section>

      <section class="dc-panel dc-summary">
        <div class="dc-summary-top">
          <div class="dc-rank"><div class="dc-label">정규시즌 순위</div>
            <div class="dc-rank-num">2<small>위</small></div><div class="dc-muted">리그 전체 10팀</div></div>
          <div><div class="dc-label">팀 성적 <span class="dc-muted">2025 완료 시즌</span></div>
            <div class="dc-big-record">83승 57패 4무</div>
            <div class="dc-label">승률</div><div class="dc-rate">.593
              <div class="dc-progress"><i style="width:59.3%"></i></div></div></div>
        </div>
        <div class="dc-summary-bottom">
          <div class="dc-mini"><span>팀 타율</span><b>.266</b><span>KBO 공식</span></div>
          <div class="dc-mini"><span>팀 ERA</span><b>3.55</b><span>KBO 공식</span></div>
          <div class="dc-mini"><span>홈 매진</span><b>60회</b><span>71경기 기준</span></div>
        </div>
      </section>

      <section class="dc-panel dc-card dc-season">
        <div class="dc-card-title">2025 시즌 캡슐 <span>REGULAR</span></div>
        <table class="dc-table"><thead><tr><th>항목</th><th>기록</th><th>범위</th></tr></thead><tbody>
          <tr class="on"><td>정규시즌</td><td><strong>2위</strong></td><td>144경기</td></tr>
          <tr><td>승·패·무</td><td>83-57-4</td><td>KBO</td></tr>
          <tr><td>승률</td><td>.593</td><td>무승부 제외</td></tr>
          <tr><td>팀 타율</td><td>.266</td><td>정규시즌</td></tr>
          <tr><td>팀 ERA</td><td>3.55</td><td>정규시즌</td></tr>
        </tbody></table>
      </section>

      <section class="dc-panel dc-card dc-legends">
        <div class="dc-card-title">영구결번 · 타자 <span>통산 안타 우선</span></div>
        """
    + people_cards(["안타", "경기"], "내야수")
    + """
      </section>

      <section class="dc-panel dc-card dc-pitch">
        <div class="dc-card-title">영구결번 · 투수 <span>통산 승 우선</span></div>
        """
    + people_cards(["승", "경기"], "투수")
    + """
      </section>

      <section class="dc-panel dc-museum">
        <div class="dc-card-title">EAGLES DATA MUSEUM <span>HALL OF FAME</span></div>
        <div class="dc-kicker">RETIRED NUMBERS</div>
        <div class="dc-museum-no">21·23<br>35·52</div>
        <div class="dc-museum-copy">송진우, 정민철, 장종훈, 김태균. 등번호 뒤에 남은 기록과 시대를 데이터로 보존합니다.</div>
        <div class="dc-link">영구결번 전시관에서 보기 →</div>
      </section>

      <section class="dc-panel dc-card dc-attendance">
        <div class="dc-card-title">2025 홈 관중 <span>71 HOME GAMES</span></div>
        <div class="dc-statbar"><label>총 관중</label><div><i style="width:99.2%"></i></div><b>1,197,840</b></div>
        <div class="dc-statbar"><label>평균 관중</label><div><i style="width:84%"></i></div><b>16,871</b></div>
        <div class="dc-statbar"><label>좌석 점유율</label><div><i style="width:99.2%"></i></div><b>99.2%</b></div>
        <div class="dc-statbar"><label>매진 경기</label><div><i style="width:84.5%"></i></div><b>60 / 71</b></div>
        <div class="dc-muted" style="margin-top:.8rem">구단 한 시즌 최다 관중 기록 · 전년 대비 총 관중 49% 증가</div>
      </section>

      <section class="dc-panel dc-card dc-timeline">
        <div class="dc-card-title">이글스 역사 좌표 <span>FRANCHISE</span></div>
        <div class="dc-event"><b>1986</b><span>빙그레 이글스 KBO 리그 참가</span></div>
        <div class="dc-event"><b>1994</b><span>한화 이글스로 구단명 변경</span></div>
        <div class="dc-event"><b>1999</b><span>구단 첫 한국시리즈 우승</span></div>
        <div class="dc-event"><b>2025</b><span>정규시즌 2위 · 대전 한화생명 볼파크 시대</span></div>
      </section>

      <section class="dc-panel dc-card dc-sources">
        <div class="dc-card-title">데이터 상태 <span>SOURCES</span></div>
        <div class="dc-source-line"><b>KBO 팀 기록</b><span>2025 정규시즌 · 검증 완료</span></div>
        <div class="dc-source-line"><b>KBO 관중 현황</b><span>2025 홈 71경기 · 검증 완료</span></div>
        <div class="dc-source-line"><b>KBO 레전드 40</b><span>영구결번 통산 기록 · 검증 완료</span></div>
        <div class="dc-source-line"><b>선수 시즌 아카이브</b><span>2015–2025 · 수집 준비 중</span></div>
      </section>
    </div>
    """,
    unsafe_allow_html=True,
)

source_footer(
    [
        "2025 팀 기록: KBO 역대 구단성적 — 144경기, 83승 57패 4무, 타율 .266, ERA 3.55, 승률 .593.",
        "2025 관중: KBO 2025 구단별 관중 현황 — 홈 71경기, 1,197,840명, 평균 16,871명, 점유율 99.2%, 매진 60회.",
        "영구결번: KBO 공식 선수 기록 및 KBO 레전드 40. 통산 수치는 정규시즌 범위.",
        "시각 요소: 실제 선수 사진이나 AI 얼굴을 사용하지 않은 데이터 중심 홈 화면.",
    ]
)
