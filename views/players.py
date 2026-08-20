"""Identity-safe player archive activated by validated season parquet files."""
import streamlit as st
from _lib import PROCESSED, hero, load_parquet, setup_page, source_footer

setup_page()
hero("PLAYER ARCHIVE", "선수 아카이브", "시즌·포지션·최소 표본을 걸고 타격과 투구 기록을 비교합니다.")
hitters, pitchers = load_parquet(PROCESSED/"hitter_seasons.parquet"), load_parquet(PROCESSED/"pitcher_seasons.parquet")
if hitters.empty and pitchers.empty:
    st.warning("검증된 선수 시즌 파일을 기다리고 있습니다.")
    st.markdown('<div class="section">DATA INTAKE READY</div>',unsafe_allow_html=True)
    st.write("`data/templates/` 형식의 CSV를 검증기에 넣으면 AVG·OBP·SLG·OPS와 ERA·WHIP·K/9·BB/9를 원자료에서 다시 계산합니다.")
    st.code("python scripts/06_import_player_seasons.py hitters.csv pitchers.csv")
else:
    seasons=sorted(set(hitters.get("season",[]))|set(pitchers.get("season",[])),reverse=True)
    c1,c2=st.columns([1,2]); season=c1.selectbox("시즌",seasons); query=c2.text_input("선수 검색")
    tabs=st.tabs(["타자","투수"])
    with tabs[0]:
        data=hitters[hitters["season"].eq(season)].copy()
        if query: data=data[data["player_name"].str.contains(query,case=False,na=False)]
        max_pa=int(max(data["pa"].max(),1)) if not data.empty else 1
        minimum=st.slider("최소 타석",0,max_pa,min(50,max_pa))
        data=data[data["pa"].ge(minimum)] if not data.empty else data
        cols=[c for c in ["player_name","position","games","pa","avg","obp","slg","ops","home_runs","rbi"] if c in data]
        st.dataframe(data[cols].sort_values("ops",ascending=False) if not data.empty else data,use_container_width=True,hide_index=True)
    with tabs[1]:
        data=pitchers[pitchers["season"].eq(season)].copy()
        if query: data=data[data["player_name"].str.contains(query,case=False,na=False)]
        max_ip=int(max(data["outs_recorded"].max()//3,1)) if not data.empty else 1
        minimum=st.slider("최소 이닝",0,max_ip,min(10,max_ip),key="min_ip")
        data=data[data["outs_recorded"].ge(minimum*3)] if not data.empty else data
        cols=[c for c in ["player_name","position","games","innings","era","whip","k9","bb9","strikeouts","saves"] if c in data]
        st.dataframe(data[cols].sort_values("era") if not data.empty else data,use_container_width=True,hide_index=True)
source_footer(["입력 범위: 2015–2025 완료 정규시즌, 2026 진행 시즌 별도.","비율 지표는 검증된 분자·분모에서 재계산하며 이름만으로 선수를 병합하지 않음."])
