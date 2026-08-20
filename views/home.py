"""Home — product direction without fabricated live statistics."""

import streamlit as st

from _lib import PROCESSED, hero, load_json, metric_cards, setup_page, source_footer


setup_page()
museum = load_json(PROCESSED / "retired_numbers.json")
players = museum.get("players", [])

hero(
    "HANWHA EAGLES · DATA & HERITAGE",
    "기록은 쌓이고, 역사는 남는다",
    "한화 이글스의 시즌과 선수를 원자료에서 다시 계산하고, 영구결번과 결정적 순간을 데이터 박물관으로 보존합니다.",
)

st.markdown('<div class="section">FOUNDATION RELEASE</div>', unsafe_allow_html=True)
st.markdown(
    metric_cards(
        [
            ("영구결번", f"{len(players)}명", "21 · 23 · 35 · 52"),
            ("팀 역사", "1986–", "빙그레·한화 프랜차이즈"),
            ("상세 기록", "2015–2025", "초기 수집 목표 범위"),
            ("현재 시즌", "2026", "완료 시즌과 분리 표시"),
        ]
    ),
    unsafe_allow_html=True,
)

st.markdown('<div class="section">EAGLES DATA MUSEUM</div>', unsafe_allow_html=True)
cards = []
for player in players:
    first_stats = list(player["stats"].items())[:3]
    stats = " · ".join(f"{key} {value}" for key, value in first_stats)
    cards.append(
        f'<div class="museum-card" data-number="{player["number"]}">'
        f'<div class="museum-no">{player["number"]}</div>'
        f'<div class="museum-name">{player["name"]}</div>'
        f'<div class="museum-role">{player["position"]} · {player["years"]}</div>'
        f'<div class="museum-line"></div><div class="museum-stat">{stats}<br>{player["headline"]}</div></div>'
    )
st.markdown('<div class="museum-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)

st.markdown('<div class="section">BUILD ORDER</div>', unsafe_allow_html=True)
build_cards = "".join(
    f'<div class="timeline-card"><div class="timeline-year">{number}</div>'
    f'<div class="timeline-title">{title}</div><div class="timeline-body">{body}</div></div>'
    for number, title, body in [
        ("01", "공식 원자료 확보", "KBO 접근성과 이용 조건을 점검하고 raw 응답을 시즌 단위로 보존합니다."),
        ("02", "재계산과 검증", "승률·AVG·OBP·SLG·ERA·WHIP를 분자와 분모에서 다시 계산합니다."),
        ("03", "대시보드 확장", "시즌 기록과 선수 아카이브를 검증한 뒤 경기·상대전적·퓨처스를 추가합니다."),
    ]
)
st.markdown(f'<div class="timeline-grid">{build_cards}</div>', unsafe_allow_html=True)

st.info("현재 홈 화면은 구조와 공식 영구결번 기록만 표시합니다. 팀 순위·최근 경기·관중 KPI는 수집 검증 후 활성화됩니다.")
source_footer(
    [
        "출처: KBO 공식 선수 기록 및 KBO 레전드 40 보도자료.",
        "범위: 영구결번 선수의 KBO 정규시즌 통산 기록. 포스트시즌과 해외리그 기록은 포함하지 않음.",
        "이미지: 현재 실제 선수 사진을 사용하지 않음. AI 콘셉트 이미지는 앱 데이터나 선수 초상으로 사용하지 않음.",
    ]
)
