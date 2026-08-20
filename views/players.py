"""Player archive placeholder until identity-safe data is available."""

import streamlit as st

from _lib import PROCESSED, hero, load_parquet, setup_page, source_footer


setup_page()
hero("PLAYER ARCHIVE", "선수 아카이브", "선수 ID·시즌·팀·포지션을 함께 사용해 동명이인과 외국인 선수 오매칭을 방지합니다.")
hitters = load_parquet(PROCESSED / "hitter_seasons.parquet")
pitchers = load_parquet(PROCESSED / "pitcher_seasons.parquet")
if hitters.empty and pitchers.empty:
    st.warning("검증된 선수 시즌 processed 데이터가 아직 없습니다.")
    st.markdown('<div class="section">IDENTITY RULES</div>', unsafe_allow_html=True)
    st.write("고유 선수 ID → 시즌 → 팀 → 포지션 순으로 매칭하며, fuzzy matching은 자동 확정에 사용하지 않습니다.")
else:
    tab1, tab2 = st.tabs(["타자", "투수"])
    with tab1:
        st.dataframe(hitters, use_container_width=True, hide_index=True)
    with tab2:
        st.dataframe(pitchers, use_container_width=True, hide_index=True)
source_footer(["예정 출처: KBO 공식 선수 기록.", "초기 범위: 2015–2025 정규시즌. 2026은 진행 중 상태로 분리."])
