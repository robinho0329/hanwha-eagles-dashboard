"""Season records placeholder until verified processed data exists."""

import streamlit as st

from _lib import PROCESSED, hero, load_parquet, setup_page, source_footer


setup_page()
hero("TEAM RECORDS", "시즌 기록", "정규시즌과 포스트시즌을 분리하고, 승률과 비율 지표를 원자료의 분자·분모에서 다시 계산합니다.")
data = load_parquet(PROCESSED / "team_seasons.parquet")
if data.empty:
    st.warning("검증된 팀 시즌 processed 데이터가 아직 없습니다.")
    st.markdown('<div class="section">PLANNED COVERAGE</div>', unsafe_allow_html=True)
    st.write("팀 역사 1986–2025 · 상세 분석 2015–2025 · 2026 진행 시즌 별도 표시")
else:
    st.dataframe(data, use_container_width=True, hide_index=True)
source_footer(["예정 출처: KBO 공식 팀 순위·팀 기록.", "현재 상태: 데이터 접근성 프로브 전이므로 수치를 표시하지 않음."])
