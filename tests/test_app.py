from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_home_renders() -> None:
    app = AppTest.from_file(str(ROOT / "views" / "home.py"))
    app.run(timeout=20)
    assert not app.exception
    rendered = "\n".join(item.value for item in app.markdown)
    assert "EAGLES DATA CENTER" in rendered
    assert "83승 57패 4무" in rendered
    assert "2026 GAME LIVE CENTER" in rendered
    assert "시즌 아카이브" in rendered


def test_museum_renders_and_selects_player() -> None:
    app = AppTest.from_file(str(ROOT / "views" / "museum.py"))
    app.run(timeout=20)
    assert not app.exception
    assert len(app.selectbox) == 1
    app.selectbox[0].select("52 · 김태균").run(timeout=20)
    assert not app.exception


def test_games_and_history_render() -> None:
    games = AppTest.from_file(str(ROOT / "views" / "games.py")).run(timeout=20)
    assert not games.exception
    assert any("월별 성적" in item.value for item in games.markdown)
    history = AppTest.from_file(str(ROOT / "views" / "history.py")).run(timeout=20)
    assert not history.exception
    assert any("다섯 개의 시대" in item.value for item in history.markdown)
