from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_home_renders() -> None:
    app = AppTest.from_file(str(ROOT / "views" / "home.py"))
    app.run(timeout=20)
    assert not app.exception
    assert any("검증된 데이터" in info.value or "현재 홈 화면" in info.value for info in app.info)


def test_museum_renders_and_selects_player() -> None:
    app = AppTest.from_file(str(ROOT / "views" / "museum.py"))
    app.run(timeout=20)
    assert not app.exception
    assert len(app.selectbox) == 1
    app.selectbox[0].select("52 · 김태균").run(timeout=20)
    assert not app.exception
