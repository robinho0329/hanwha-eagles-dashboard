"""Franchise history structured after the Barcelona project's club and eras pages."""
import streamlit as st
from _lib import PROCESSED, hero, load_json, load_parquet, setup_page, source_footer

setup_page(); hero("FRANCHISE HISTORY · SINCE 1986","이글스의 시간","빙그레 창단부터 1999년 정상, 재건과 신구장 시대까지 기록과 인물을 함께 봅니다.")
h=load_parquet(PROCESSED/"hitter_seasons.parquet"); p=load_parquet(PROCESSED/"pitcher_seasons.parquet")
st.markdown('<div class="section">구단 정체성</div>',unsafe_allow_html=True)
st.markdown('''<div class="lede">1986년 충청권을 연고로 <b>빙그레 이글스</b>가 KBO 리그에 참가했다. 1993년 11월 구단명을 <b>한화 이글스</b>로 바꾸었고, 1999년 처음 한국시리즈 정상에 올랐다. 장종훈·송진우·정민철·김태균으로 이어지는 영구결번은 공격과 투수 양쪽에서 구단의 시대를 연결한다.</div>''',unsafe_allow_html=True)

st.markdown('<div class="section">다섯 개의 시대</div>',unsafe_allow_html=True)
eras=[("1986–1993","빙그레의 비상","창단 직후 강팀으로 성장해 네 차례 한국시리즈 무대를 밟은 초기 황금기."),("1994–2008","한화와 첫 우승","구단명 변경 뒤 1999년 한국시리즈 첫 우승. 다이너마이트 타선의 상징이 굳어진 시기."),("2009–2017","긴 재건","세대교체와 성적 부진이 겹친 시간. 동시에 다음 세대와 팬덤이 팀의 역사를 이어 갔다."),("2018–2024","가을의 귀환과 재설계","2018년 포스트시즌 복귀 뒤 다시 장기적인 전력 재편에 들어간 전환기."),("2025–","새 구장, 재도약","대전 한화생명 볼파크 시대 개막과 함께 2025 정규시즌 2위로 올라선 현재 진행형 시대.")]
cards=''.join(f'<div class="timeline-card"><div class="timeline-year">{y}</div><div class="timeline-title">{t}</div><div class="timeline-body">{b}</div></div>' for y,t,b in eras)
st.markdown(f'<div class="timeline-grid">{cards}</div>',unsafe_allow_html=True)

st.markdown('<div class="section">역사 좌표</div>',unsafe_allow_html=True)
milestones=[("1986","빙그레 이글스 KBO 참가"),("1993.11","한화 이글스로 구단명 변경"),("1999","한국시리즈 첫 우승"),("2018","포스트시즌 복귀"),("2025","신구장 시대 · 정규시즌 2위")]
st.markdown('<div class="museum-grid">'+''.join(f'<div class="museum-card"><div class="museum-number">{y}</div><div class="museum-name">{t}</div></div>' for y,t in milestones)+'</div>',unsafe_allow_html=True)

st.markdown('<div class="section">데이터로 남은 최근 11시즌</div>',unsafe_allow_html=True)
c1,c2,c3,c4=st.columns(4); c1.metric("선수 기록 범위","2015–2025"); c2.metric("타자 선수-시즌",f"{len(h):,}"); c3.metric("투수 선수-시즌",f"{len(p):,}"); c4.metric("영구결번","4명")
st.caption("선수-시즌 수는 출전 선수 기록 행의 개수이며 선수 수나 로스터 규모와 같은 뜻이 아닙니다.")

st.markdown('<div class="section">영구결번으로 읽는 역사</div>',unsafe_allow_html=True)
museum=load_json(PROCESSED/"retired_numbers.json")
for player in museum.get("players",[]):
    with st.expander(f"{player['number']} · {player['name']} — {player['headline']}"):
        st.write(f"{player['position']} · {player['years']}"); st.write(" · ".join(f"{k} {v}" for k,v in player["stats"].items()))

source_footer(["창단·구단명 변경: 한화그룹 연혁 및 문화체육관광부 자료.","1999 우승: KBO 온라인박물관 프로야구 30주년·KBO 공식 기사.","2025 순위: KBO 역대 구단성적. 서술은 공식 자료를 바탕으로 요약했으며 세부 시즌 기록 페이지는 데이터 확보 후 확장."])
