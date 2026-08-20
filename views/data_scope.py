"""Data manifest and limitations."""

import pandas as pd
import streamlit as st

from _lib import PROCESSED, hero, load_json, setup_page, source_footer


setup_page()
hero("DATA COVERAGE", "데이터 범위", "있는 데이터와 없는 데이터를 구분하고, 출처·경기 구분·기준일·결측 원인을 공개합니다.")
manifest = load_json(PROCESSED / "data_manifest.json")
rows = manifest.get("datasets", [])

st.markdown('<div class="section">DATASETS</div>', unsafe_allow_html=True)
if rows:
    frame = pd.DataFrame(rows).rename(
        columns={"name": "데이터셋", "status": "상태", "competition": "경기 구분", "source": "출처", "note": "비고"}
    )
    st.dataframe(frame[["데이터셋", "상태", "경기 구분", "출처", "비고"]], use_container_width=True, hide_index=True)

st.markdown('<div class="section">KNOWN LIMITS</div>', unsafe_allow_html=True)
cards = "".join(
    f'<div class="timeline-card"><div class="timeline-year">LIMIT</div>'
    f'<div class="timeline-title">{title}</div><div class="timeline-body">{body}</div></div>'
    for title, body in [
        ("진행 시즌", "2026 기록은 기준일 이후 변할 수 있어 완료 시즌과 별도 표시합니다."),
        ("고급 지표", "STATIZ 자동 수집은 이용약관상 허가 또는 공식 API 없이는 수행하지 않습니다."),
        ("선수 사진", "라이선스와 인물 식별이 모두 확인되지 않으면 표시하지 않습니다."),
        ("대회 구분", "정규시즌·포스트시즌·시범경기·퓨처스는 하나의 집계로 섞지 않습니다."),
        ("결측", "원자료 결측, 시즌 미제공, 적용 불가, 수집 실패를 0과 분리합니다."),
        ("비율 지표", "AVG·OBP·SLG·ERA·WHIP는 단순 평균하지 않고 원자료 분자·분모에서 계산합니다."),
    ]
)
st.markdown(f'<div class="timeline-grid">{cards}</div>', unsafe_allow_html=True)
source_footer([f"매니페스트 생성일: {manifest.get('generated_at', '알 수 없음')}", "이 페이지는 processed 데이터 상태와 함께 갱신됩니다."])
