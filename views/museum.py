"""Eagles Data Museum — retired-number legends."""

import plotly.graph_objects as go
import streamlit as st

from _lib import GRID, ORANGE, PLOT, PROCESSED, hero, load_json, metric_cards, setup_page, source_footer


setup_page()
museum = load_json(PROCESSED / "retired_numbers.json")
players = museum.get("players", [])

hero(
    "EAGLES DATA MUSEUM",
    "영구결번 전시관",
    "등번호 뒤에 남은 기록과 시대를 함께 읽습니다. 모든 통산 수치는 KBO 정규시즌 범위로 통일합니다.",
)

names = [f'{player["number"]} · {player["name"]}' for player in players]
selected_label = st.selectbox("전시 선수", names, label_visibility="collapsed")
selected = players[names.index(selected_label)]

st.markdown(f'<div class="section">NO. {selected["number"]} · {selected["name"]}</div>', unsafe_allow_html=True)
left, right = st.columns([1, 2.1], gap="large")
with left:
    st.markdown(
        f"""
        <div class="museum-card" data-number="{selected['number']}" style="min-height:330px">
          <div class="museum-no">{selected['number']}</div>
          <div class="museum-name" style="font-size:1.55rem">{selected['name']}</div>
          <div class="museum-role">{selected['position']} · {selected['years']}</div>
          <div class="museum-line"></div>
          <div class="museum-stat" style="font-size:.9rem">{selected['headline']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    stats = list(selected["stats"].items())
    st.markdown(
        metric_cards([(key, value, "KBO 정규시즌 통산") for key, value in stats[:4]]),
        unsafe_allow_html=True,
    )
    if len(stats) > 4:
        st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
        st.markdown(
            metric_cards([(key, value, "KBO 정규시즌 통산") for key, value in stats[4:]]),
            unsafe_allow_html=True,
        )

st.markdown('<div class="section">CAREER TIMELINE</div>', unsafe_allow_html=True)
timeline = "".join(
    f'<div class="timeline-card"><div class="timeline-year">{year}</div>'
    f'<div class="timeline-title">{title}</div><div class="timeline-body">{body}</div></div>'
    for year, title, body in selected["milestones"]
)
st.markdown(f'<div class="timeline-grid">{timeline}</div>', unsafe_allow_html=True)

st.markdown('<div class="section">NUMBER WALL</div>', unsafe_allow_html=True)
fig = go.Figure(
    go.Bar(
        x=[str(player["number"]) for player in players],
        y=[1, 1, 1, 1],
        text=[player["name"] for player in players],
        textposition="inside",
        marker_color=[ORANGE if player == selected else "#173247" for player in players],
        hovertext=[player["headline"] for player in players],
        hoverinfo="text",
    )
)
fig.update_layout(height=225, showlegend=False, yaxis_visible=False, **PLOT)
fig.update_xaxes(title="영구결번", gridcolor=GRID)
st.plotly_chart(fig, use_container_width=True)

st.link_button("KBO 공식 기록에서 확인", selected["source_url"])
source_footer(
    [
        f"선택 선수 출처: {selected['source_url']}",
        "집계 범위: KBO 정규시즌 통산. 포스트시즌·일본리그·국가대표 기록 제외.",
        "사진 정책: 라이선스가 확인된 사진만 추후 추가하며, 이름 기반 추정 매칭은 사용하지 않음.",
    ]
)
