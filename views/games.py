"""Historical game analysis plus the separate 2026 live API window."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from _lib import GRID, ORANGE, PROCESSED, hero, load_json, load_parquet, setup_page, source_footer

setup_page(); hero("GAME ANALYSIS", "경기 분석", "2015–2025 정규시즌 1,584경기와 2026 라이브 창을 섞지 않고 분석합니다.")
history = load_parquet(PROCESSED / "hanwha_games_2015_2025.parquet")
live_payload = load_json(PROCESSED / "hanwha_game_window.json")

def longest(values, target="W"):
    best=run=0
    for value in values:
        run=run+1 if value==target else 0; best=max(best,run)
    return best

def analysis(frame: pd.DataFrame, key: str) -> None:
    frame=frame.sort_values("date").copy(); frame["month"]=pd.to_datetime(frame.date).dt.month
    wins=int(frame.result.eq("W").sum()); losses=int(frame.result.eq("L").sum()); draws=int(frame.result.eq("D").sum())
    c1,c2,c3,c4=st.columns(4); c1.metric("완료 경기",len(frame)); c2.metric("승–패–무",f"{wins}–{losses}–{draws}"); c3.metric("승률",f"{wins/max(wins+losses,1):.3f}"); c4.metric("최장 연승",f"{longest(frame.result)}경기")
    st.markdown('<div class="section">최근 10경기</div>',unsafe_allow_html=True); st.write("  ".join(f"**{x}**" for x in frame.tail(10).result))
    venue=frame.assign(장소=frame.is_home.map({True:"홈",False:"원정"})).groupby("장소").agg(승=("result",lambda s:(s=="W").sum()),패=("result",lambda s:(s=="L").sum()),무=("result",lambda s:(s=="D").sum())).reset_index()
    fig=go.Figure(); fig.add_bar(x=venue.장소,y=venue.승,name="승",marker_color=ORANGE); fig.add_bar(x=venue.장소,y=venue.패,name="패",marker_color="#536778")
    fig.update_layout(barmode="group",height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#cbd5dd",yaxis_gridcolor=GRID); st.plotly_chart(fig,width="stretch",key=f"venue-{key}")
    left,right=st.columns(2)
    with left:
        st.markdown('<div class="section">월별 성적</div>',unsafe_allow_html=True)
        monthly=frame.groupby("month").agg(승=("result",lambda s:(s=="W").sum()),패=("result",lambda s:(s=="L").sum())).reset_index()
        chart=go.Figure(); chart.add_bar(x=monthly.month,y=monthly.승,name="승",marker_color=ORANGE); chart.add_bar(x=monthly.month,y=monthly.패,name="패",marker_color="#536778")
        chart.update_layout(barmode="group",height=340,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#cbd5dd",yaxis_gridcolor=GRID); st.plotly_chart(chart,width="stretch",key=f"month-{key}")
    with right:
        st.markdown('<div class="section">상대팀별 전적</div>',unsafe_allow_html=True)
        opp=frame.groupby("opponent").agg(경기=("game_id","size"),승=("result",lambda s:(s=="W").sum()),패=("result",lambda s:(s=="L").sum()),무=("result",lambda s:(s=="D").sum()),득점=("runs_for","sum"),실점=("runs_against","sum")).reset_index().rename(columns={"opponent":"상대"}); opp["승률"]=(opp.승/(opp.승+opp.패).replace(0,pd.NA)).round(3)
        st.dataframe(opp.sort_values(["승","승률"],ascending=False),width="stretch",hide_index=True,height=340)
    st.markdown('<div class="section">경기별 결과</div>',unsafe_allow_html=True)
    detail=frame.rename(columns={"date":"일자","opponent":"상대","runs_for":"득점","runs_against":"실점","result":"결과","stadium":"구장"}).copy(); detail["장소"]=detail.is_home.map({True:"홈",False:"원정"})
    st.dataframe(detail[["일자","장소","상대","득점","실점","결과","구장"]].sort_values("일자",ascending=False),width="stretch",hide_index=True)

archive_tab, live_tab = st.tabs(["2015–2025 경기 아카이브", "2026 LIVE WINDOW"])
with archive_tab:
    if history.empty: st.warning("역사 경기 데이터가 없습니다.")
    else:
        season=st.selectbox("시즌",sorted(history.season.unique(),reverse=True),key="history-season"); analysis(history[history.season.eq(season)],f"history-{season}")
        source_footer(["KBO 공식 월별 일정 서비스 · 정규시즌만 수록.","2015–2025 매 시즌 144경기, 합계 1,584경기. 시즌별 승패무가 KBO 역대 구단성적과 일치함."])
with live_tab:
    raw=live_payload.get("games",[]); rows=[]
    for g in raw:
        home=g.get("idHomeTeam")=="139826"; hs=g.get("intHomeScore"); aws=g.get("intAwayScore"); ours=hs if home else aws; theirs=aws if home else hs
        if ours is None or theirs is None: continue
        rows.append({"game_id":g.get("idEvent"),"date":g.get("dateEventLocal") or g.get("dateEvent"),"is_home":home,"opponent":g.get("strAwayTeam") if home else g.get("strHomeTeam"),"runs_for":int(ours),"runs_against":int(theirs),"result":"W" if int(ours)>int(theirs) else "L" if int(ours)<int(theirs) else "D","stadium":g.get("strVenue") or ""})
    if rows: analysis(pd.DataFrame(rows),"live")
    else: st.info("현재 완료 경기 데이터가 없습니다.")
    source_footer([f"TheSportsDB 날짜 API · {live_payload.get('range',{}).get('from','-')}~{live_payload.get('range',{}).get('to','-')}.","무료 API 반환 제한이 있어 2026 공식 전체 시즌 성적으로 사용하지 않음."])
