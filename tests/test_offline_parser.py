from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "01_parse_kbo_team_seasons.py"


def load_parser():
    spec = spec_from_file_location("offline_team_parser", SCRIPT)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_offline_parser_normalizes_authorized_html(tmp_path):
    source = tmp_path / "team-history.html"
    source.write_text(
        """<table><thead><tr><th>연도</th><th>순위</th><th>팀명</th><th>경기</th><th>승</th><th>패</th><th>무</th><th>승률</th><th>타율</th><th>방어율</th></tr></thead>
        <tbody><tr><td>2025</td><td>2</td><td>한화</td><td>144</td><td>83</td><td>57</td><td>4</td><td>.593</td><td>.266</td><td>3.55</td></tr></tbody></table>""",
        encoding="utf-8",
    )
    frame = load_parser().parse_html(source)
    assert frame.loc[0, "team_id"] == "hanwha-eagles"
    assert frame.loc[0, "competition"] == "regular"
    assert frame.loc[0, "games"] == 144
    assert frame.loc[0, "win_rate"] == 0.593
