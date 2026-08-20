"""Hanwha Eagles Data Center entrypoint."""

import streamlit as st


st.set_page_config(
    page_title="Hanwha Eagles · Data Center",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

navigation = st.navigation(
    {
        "EAGLES": [
            st.Page("views/home.py", title="홈", icon="🏠", default=True),
            st.Page("views/seasons.py", title="시즌 기록", icon="📊"),
            st.Page("views/players.py", title="선수 아카이브", icon="👤"),
        ],
        "DATA MUSEUM": [
            st.Page("views/museum.py", title="영구결번 전시관", icon="🏛️"),
        ],
        "ABOUT": [
            st.Page("views/data_scope.py", title="데이터 범위", icon="🗂️"),
        ],
    }
)
navigation.run()
