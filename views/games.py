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
df=pd.DataFrame(rows); df["일자"]=pd.to_datetime(df["일자"])
df["득점"]=pd.to_numeric(df["득점"],errors="coerce"); df["실점"]=pd.to_numeric(df["실점"],errors="coerce")
done=df[df["결과"].notna()].copy()
TEAM_KO={"Kia Tigers":"KIA 타이거즈","LG Twins":"LG 트윈스","Doosan Bears":"두산 베어스","Samsung Lions":"삼성 라이온즈","Lotte Giants":"롯데 자이언츠","SSG Landers":"SSG 랜더스","Kiwoom Heroes":"키움 히어로즈","NC Dinos":"NC 다이노스","KT Wiz":"KT 위즈"}
df["상대"]=df["상대"].replace(TEAM_KO); done["상대"]=done["상대"].replace(TEAM_KO)
done["월"]=done["일자"].dt.month.astype(str)+"월"

def longest_streak(values, target):
    best=run=0
    for value in values:
        run=run+1 if value==target else 0; best=max(best,run)
    return best

c1,c2,c3,c4=st.columns(4)
c1.metric("수집 완료 경기",len(done)); c2.metric("승–패–무",f"{(done['결과']=='W').sum()}–{(done['결과']=='L').sum()}–{(done['결과']=='D').sum()}")
c3.metric("승률",f"{(done['결과']=='W').sum()/max((done['결과']!='D').sum(),1):.3f}")
c4.metric("최장 연승",f"{longest_streak(done.sort_values('일자')['결과'],'W')}경기")
recent=done.sort_values("일자").tail(10); st.markdown('<div class="section">최근 폼</div>',unsafe_allow_html=True)
st.write("  ".join(f"**{r}**" for r in recent["결과"]) or "완료 경기 없음")
if len(done):
    summary=(done.groupby("장소")["결과"].agg(경기="size",승=lambda s:(s=="W").sum(),패=lambda s:(s=="L").sum(),무=lambda s:(s=="D").sum()).reset_index())
    fig=go.Figure(go.Bar(x=summary["장소"],y=summary["승"],name="승",marker_color=ORANGE)); fig.add_bar(x=summary["장소"],y=summary["패"],name="패",marker_color="#536778")
    fig.update_layout(barmode="group",height=320,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#cbd5dd",yaxis_gridcolor=GRID)
    st.plotly_chart(fig,use_container_width=True)
    left,right=st.columns(2)
    with left:
        st.markdown('<div class="section">월별 성적</div>',unsafe_allow_html=True)
        monthly=done.groupby("월").agg(경기=("경기ID","size"),승=("결과",lambda s:(s=="W").sum()),패=("결과",lambda s:(s=="L").sum()),득점=("득점","sum"),실점=("실점","sum")).reset_index()
        fm=go.Figure(); fm.add_bar(x=monthly["월"],y=monthly["승"],name="승",marker_color=ORANGE); fm.add_bar(x=monthly["월"],y=monthly["패"],name="패",marker_color="#536778")
        fm.update_layout(barmode="group",height=340,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#cbd5dd",yaxis_gridcolor=GRID)
        st.plotly_chart(fm,use_container_width=True)
    with right:
        st.markdown('<div class="section">상대팀별 전적</div>',unsafe_allow_html=True)
        opponent=done.groupby("상대").agg(경기=("경기ID","size"),승=("결과",lambda s:(s=="W").sum()),패=("결과",lambda s:(s=="L").sum()),무=("결과",lambda s:(s=="D").sum()),득점=("득점","sum"),실점=("실점","sum")).reset_index()
        opponent["승률"]=(opponent["승"]/(opponent["승"]+opponent["패"]).replace(0,pd.NA)).round(3)
        st.dataframe(opponent.sort_values(["승","승률"],ascending=False),use_container_width=True,hide_index=True,height=340)
st.markdown('<div class="section">경기별 결과·일정</div>',unsafe_allow_html=True)
st.dataframe(df.sort_values("일자",ascending=False),use_container_width=True,hide_index=True)
source_footer([f"출처: TheSportsDB 공식 API · 날짜 조회 범위 {payload.get('range',{}).get('from','-')}~{payload.get('range',{}).get('to','-')} · 한화 경기 {len(df)}건 중 점수 완료 {len(done)}건.","무료 날짜 API의 반환 건수 제한으로 같은 날 일부 경기가 누락될 수 있으므로 전체 시즌 공식 성적으로 해석하지 않음."])
