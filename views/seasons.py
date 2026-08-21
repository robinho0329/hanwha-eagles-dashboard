"""Verified Hanwha regular-season archive for 2015-2025."""
import plotly.graph_objects as go
import streamlit as st

from _lib import GRID, ORANGE, PROCESSED, hero, load_parquet, setup_page, source_footer

setup_page()
hero("TEAM RECORDS", "시즌 기록", "11개 정규시즌을 같은 기준으로 비교합니다. 경기 결과는 경기 ID에서 집계하고 팀 타율·ERA·관중은 KBO 공식 역사표와 대조했습니다.")
data = load_parquet(PROCESSED / "team_seasons_2015_2025.parquet")
if data.empty:
    st.warning("검증된 시즌 기록이 없습니다.")
    st.stop()

best = data.loc[data.win_rate.idxmax()]
latest = data.sort_values("season").iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("수록 시즌", f"{len(data)}개", "2015–2025 정규시즌")
c2.metric("최고 승률", f"{best.win_rate:.3f}", f"{int(best.season)} · {int(best['rank'])}위")
c3.metric("2025 성적", f"{int(latest.wins)}–{int(latest.losses)}–{int(latest.draws)}", "정규시즌 2위")
c4.metric("2025 관중", f"{int(latest.attendance_total):,}명", f"평균 {int(latest.attendance_average):,}명")

st.markdown('<div class="section">순위와 승률 추이</div>', unsafe_allow_html=True)
fig = go.Figure()
fig.add_scatter(x=data.season, y=data.win_rate, mode="lines+markers", name="승률", line=dict(color=ORANGE, width=3))
fig.add_bar(x=data.season, y=data.rank, name="순위", marker_color="#29465b", opacity=.55, yaxis="y2")
fig.update_layout(height=390, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5dd", yaxis=dict(title="승률", gridcolor=GRID, range=[0.25, .65]), yaxis2=dict(title="순위", overlaying="y", side="right", autorange="reversed", range=[10.8, .2]), legend=dict(orientation="h"))
st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)
with left:
    st.markdown('<div class="section">득점과 실점</div>', unsafe_allow_html=True)
    runs = go.Figure(); runs.add_bar(x=data.season, y=data.runs_for, name="득점", marker_color=ORANGE); runs.add_bar(x=data.season, y=data.runs_against, name="실점", marker_color="#536778")
    runs.update_layout(barmode="group", height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5dd", yaxis_gridcolor=GRID)
    st.plotly_chart(runs, width="stretch")
with right:
    st.markdown('<div class="section">팀 타율과 ERA</div>', unsafe_allow_html=True)
    rates = go.Figure(); rates.add_scatter(x=data.season, y=data.batting_average, name="팀 타율", line=dict(color=ORANGE, width=3)); rates.add_scatter(x=data.season, y=data.era, name="팀 ERA", yaxis="y2", line=dict(color="#e9eef2", width=2))
    rates.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5dd", yaxis=dict(title="타율", gridcolor=GRID), yaxis2=dict(title="ERA", overlaying="y", side="right"), legend=dict(orientation="h"))
    st.plotly_chart(rates, width="stretch")

st.markdown('<div class="section">시즌 상세</div>', unsafe_allow_html=True)
table = data.rename(columns={"season":"시즌","rank":"순위","games":"경기","wins":"승","losses":"패","draws":"무","win_rate":"승률","runs_for":"득점","runs_against":"실점","batting_average":"팀 타율","era":"ERA","attendance_total":"총관중","attendance_average":"평균 관중"})
st.dataframe(table[["시즌","순위","경기","승","패","무","승률","득점","실점","팀 타율","ERA","총관중","평균 관중"]].sort_values("시즌", ascending=False), width="stretch", hide_index=True)
source_footer(["경기·승패무·득실점: KBO 공식 월별 일정 서비스의 2015–2025 정규시즌 1,584경기에서 직접 집계.", "팀 타율·ERA: KBO 역대 구단성적. 관중: KBO 역대 관중 현황.", "2020–2022 관중은 코로나19 입장 제한의 영향을 받으므로 일반 시즌과 직접 비교할 때 주의."])
