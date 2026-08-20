"""Identity-safe player archive activated by validated season parquet files."""
import streamlit as st
from _lib import PROCESSED, hero, load_parquet, setup_page, source_footer

setup_page()
hero("PLAYER ARCHIVE", "선수 아카이브", "시즌·포지션·최소 표본을 걸고 타격과 투구 기록을 비교합니다.")
hitters, pitchers = load_parquet(PROCESSED/"hitter_seasons.parquet"), load_parquet(PROCESSED/"pitcher_seasons.parquet")
LABELS={"player_name":"선수","position":"포지션","games":"경기","pa":"타석","ab":"타수","hits":"안타","runs":"득점","avg":"타율","obp":"출루율","slg":"장타율","ops":"OPS","home_runs":"홈런","rbi":"타점","stolen_bases":"도루","wins":"승","losses":"패","holds":"홀드","innings":"이닝","era":"ERA","whip":"WHIP","k9":"K/9","bb9":"BB/9","strikeouts":"탈삼진","saves":"세이브"}
if hitters.empty and pitchers.empty:
    st.warning("검증된 선수 시즌 파일을 기다리고 있습니다.")
    st.markdown('<div class="section">DATA INTAKE READY</div>',unsafe_allow_html=True)
    st.write("`data/templates/` 형식의 CSV를 검증기에 넣으면 AVG·OBP·SLG·OPS와 ERA·WHIP·K/9·BB/9를 원자료에서 다시 계산합니다.")
    st.code("python scripts/06_import_player_seasons.py hitters.csv pitchers.csv")
else:
    st.caption(f"검증 완료 · 타자 시즌 {len(hitters):,}행 · 투수 시즌 {len(pitchers):,}행 · 2015–2025 정규시즌")
    st.info("2026 선수 기록은 현재 라이선스 데이터셋에 포함되지 않습니다. 진행 시즌 값을 추정하거나 0으로 채우지 않았습니다.")
    seasons=sorted(set(hitters.get("season",[]))|set(pitchers.get("season",[])),reverse=True)
    c1,c2=st.columns([1,2]); season=c1.selectbox("시즌",seasons); query=c2.text_input("선수 검색")
    tabs=st.tabs(["타자","투수"])
    with tabs[0]:
        data=hitters[hitters["season"].eq(season)].copy()
        if query: data=data[data["player_name"].str.contains(query,case=False,na=False)]
        max_pa=int(max(data["pa"].max(),1)) if not data.empty else 1
        minimum=st.slider("최소 타석",0,max_pa,min(50,max_pa))
        data=data[data["pa"].ge(minimum)] if not data.empty else data
        if not data.empty:
            k1,k2,k3,k4=st.columns(4)
            avg=data.loc[data["avg"].idxmax()]; hr=data.loc[data["home_runs"].idxmax()]
            rbi=data.loc[data["rbi"].idxmax()]; ops=data.loc[data["ops"].idxmax()]
            k1.metric("타율 리더",f"{avg['avg']:.3f}",avg["player_name"]); k2.metric("홈런 리더",f"{int(hr['home_runs'])}개",hr["player_name"])
            k3.metric("타점 리더",f"{int(rbi['rbi'])}점",rbi["player_name"]); k4.metric("OPS 리더",f"{ops['ops']:.3f}",ops["player_name"])
        cols=[c for c in ["player_name","position","games","pa","ab","hits","runs","avg","obp","slg","ops","home_runs","rbi","stolen_bases"] if c in data]
        shown=data[cols].sort_values("ops",ascending=False).rename(columns=LABELS) if not data.empty else data
        st.dataframe(shown,use_container_width=True,hide_index=True)
    with tabs[1]:
        data=pitchers[pitchers["season"].eq(season)].copy()
        if query: data=data[data["player_name"].str.contains(query,case=False,na=False)]
        max_ip=int(max(data["outs_recorded"].max()//3,1)) if not data.empty else 1
        minimum=st.slider("최소 이닝",0,max_ip,min(10,max_ip),key="min_ip")
        data=data[data["outs_recorded"].ge(minimum*3)] if not data.empty else data
        if not data.empty:
            k1,k2,k3,k4=st.columns(4)
            era=data.loc[data["era"].idxmin()]; wins=data.loc[data["wins"].idxmax()]
            strikeouts=data.loc[data["strikeouts"].idxmax()]; saves=data.loc[data["saves"].idxmax()]
            k1.metric("ERA 리더",f"{era['era']:.2f}",era["player_name"]); k2.metric("다승 리더",f"{int(wins['wins'])}승",wins["player_name"])
            k3.metric("탈삼진 리더",f"{int(strikeouts['strikeouts'])}개",strikeouts["player_name"]); k4.metric("세이브 리더",f"{int(saves['saves'])}개",saves["player_name"])
        cols=[c for c in ["player_name","position","games","wins","losses","saves","holds","innings","era","whip","k9","bb9","strikeouts"] if c in data]
        shown=data[cols].sort_values("era").rename(columns=LABELS) if not data.empty else data
        st.dataframe(shown,use_container_width=True,hide_index=True)
source_footer(["데이터: netsong, KBO Player Dataset (1982–2025), Kaggle · CC BY-SA 4.0. 원 저자가 밝힌 upstream은 STATIZ.","표시 범위: 한화 2015–2025 정규시즌. 2026 선수 기록은 이 데이터셋에 없어 미표시.","비율 지표는 분자·분모에서 재계산하며 선수 ID·시즌·팀으로 구분. 2022–2025 보완 필요 가능성이 원 데이터 설명에 명시됨."])
