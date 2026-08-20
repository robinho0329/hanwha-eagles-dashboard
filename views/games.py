"""Game analysis from the currently licensed API window."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from _lib import GRID, ORANGE, PROCESSED, hero, load_json, setup_page, source_footer

setup_page(); hero("GAME ANALYSIS", "경기 분석", "최근 폼·홈/원정·상대전적을 동일 경기 ID에서 계산합니다.")
payload=load_json(PROCESSED/"hanwha_game_window.json"); raw=payload.get("games",[])
if not raw: st.warning("검증된 경기 창 데이터가 없습니다."); st.stop()
rows=[]
for g in raw:
    home=g.get("idHomeTeam")=="139826"; hs=g.get("intHomeScore"); aws=g.get("intAwayScore")
    ours=hs if home else aws; theirs=aws if home else hs
    result=None if ours is None or theirs is None else ("W" if int(ours)>int(theirs) else "L" if int(ours)<int(theirs) else "D")
    rows.append({"경기ID":g.get("idEvent"),"일자":g.get("dateEventLocal") or g.get("dateEvent"),"장소":"홈" if home else "원정",
                 "상대":g.get("strAwayTeam") if home else g.get("strHomeTeam"),"득점":ours,"실점":theirs,"결과":result,"상태":g.get("strStatus")})
df=pd.DataFrame(rows); df["일자"]=pd.to_datetime(df["일자"]); done=df[df["결과"].notna()].copy()
c1,c2,c3,c4=st.columns(4)
c1.metric("수집 경기",len(df)); c2.metric("완료 경기",len(done)); c3.metric("승–패–무",f"{(done['결과']=='W').sum()}–{(done['결과']=='L').sum()}–{(done['결과']=='D').sum()}")
c4.metric("득실차",f"{(pd.to_numeric(done['득점']).sum()-pd.to_numeric(done['실점']).sum()):+g}" if len(done) else "-")
recent=done.sort_values("일자").tail(10); st.markdown('<div class="section">최근 폼</div>',unsafe_allow_html=True)
st.write("  ".join(f"**{r}**" for r in recent["결과"]) or "완료 경기 없음")
if len(done):
    summary=(done.groupby("장소")["결과"].agg(경기="size",승=lambda s:(s=="W").sum(),패=lambda s:(s=="L").sum(),무=lambda s:(s=="D").sum()).reset_index())
    fig=go.Figure(go.Bar(x=summary["장소"],y=summary["승"],name="승",marker_color=ORANGE)); fig.add_bar(x=summary["장소"],y=summary["패"],name="패",marker_color="#536778")
    fig.update_layout(barmode="group",height=320,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#cbd5dd",yaxis_gridcolor=GRID)
    st.plotly_chart(fig,use_container_width=True)
st.markdown('<div class="section">상대전적·일정</div>',unsafe_allow_html=True)
st.dataframe(df.sort_values("일자",ascending=False),use_container_width=True,hide_index=True)
source_footer([f"출처: TheSportsDB 공식 API · 수집 범위 {payload.get('range',{}).get('from','-')}~{payload.get('range',{}).get('to','-')}.","현재는 제한된 날짜 창이며 전체 시즌 지표로 해석하지 않음."])
