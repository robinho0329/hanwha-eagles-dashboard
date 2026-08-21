"""Fetch KBO regular-season schedules/results by month for 2015-2025.

The public schedule web-service is requested at a deliberately low rate. Every
monthly response is checkpointed before normalization so interrupted runs can
resume without requesting completed months again.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.koreabaseball.com/ws/Schedule.asmx/GetScheduleList"
SOURCE_PAGE = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
TEAM_HISTORY_PAGE = "https://www.koreabaseball.com/Record/History/Team/Record.aspx"
CROWD_HISTORY_PAGE = "https://www.koreabaseball.com/Record/Crowd/History.aspx"
RAW = Path("data/raw/kbo/schedule_v2")
OUT = Path("data/processed")
HEADERS = {
    "User-Agent": "HanwhaEaglesDataArchive/1.0 (non-commercial research dashboard)",
    "Referer": SOURCE_PAGE,
}

# KBO official historical tables. These are deliberately small, reviewable
# reference values used to enrich and cross-check the calculated game totals.
OFFICIAL_TEAM_RATES = {
    2015: (.271, 5.11), 2016: (.289, 5.76), 2017: (.287, 5.28),
    2018: (.275, 4.93), 2019: (.256, 4.80), 2020: (.245, 5.28),
    2021: (.237, 4.65), 2022: (.245, 4.83), 2023: (.241, 4.38),
    2024: (.270, 4.98), 2025: (.266, 3.55),
}
OFFICIAL_WLD = {
    2015: (68, 76, 0), 2016: (66, 75, 3), 2017: (61, 81, 2),
    2018: (77, 67, 0), 2019: (58, 86, 0), 2020: (46, 95, 3),
    2021: (49, 83, 12), 2022: (46, 96, 2), 2023: (58, 80, 6),
    2024: (66, 76, 2), 2025: (83, 57, 4),
}
OFFICIAL_ATTENDANCE = {
    2015: (657_385, 9_130), 2016: (660_472, 9_173),
    2017: (593_251, 8_240), 2018: (734_110, 10_196),
    2019: (555_225, 7_711), 2020: (19_962, 277),
    2021: (103_960, 1_444), 2022: (358_190, 4_975),
    2023: (566_785, 7_764), 2024: (804_204, 11_327),
    2025: (1_231_840, 16_875),
}


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def fetch_month(session: requests.Session, season: int, month: int, delay: float) -> Path:
    path = RAW / str(season) / f"{month:02d}.json"
    if path.exists() and path.stat().st_size > 100:
        return path
    payload = {
        "leId": "1",
        # KBO's schedule UI requests 0,9,6 together. Historical rescheduled
        # regular-season rows can otherwise be omitted in several seasons.
        "srIdList": "0,9,6",
        "seasonId": str(season),
        "gameMonth": f"{month:02d}",
        "teamId": "",
    }
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            response = session.post(URL, data=payload, timeout=30)
            response.raise_for_status()
            body = response.json()
            atomic_json(path, {
                "source_url": URL,
                "source_page": SOURCE_PAGE,
                "payload": payload,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "response": body,
            })
            time.sleep(delay)
            return path
        except (requests.RequestException, ValueError) as error:
            last_error = error
            time.sleep(min(60, 2 ** attempt * 5))
    raise RuntimeError(f"failed {season}-{month:02d}") from last_error


def clean_html(value: object) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return " ".join(html.unescape(text).split())


def parse_month(path: Path) -> list[dict[str, object]]:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    season = int(bundle["payload"]["seasonId"])
    current_date = ""
    games: list[dict[str, object]] = []
    for row_object in bundle["response"].get("rows", []):
        cells = row_object.get("row", [])
        for cell in cells:
            if (cell.get("Class") or "") == "day":
                match = re.search(r"(\d{2}\.\d{2})", clean_html(cell.get("Text")))
                if match:
                    current_date = match.group(1)
        values = {(cell.get("Class") or ""): cell.get("Text") or "" for cell in cells}
        play = values.get("play", "")
        if not play or not current_date:
            continue
        teams, scores = [], []
        for attrs, body in re.findall(r"<span([^>]*)>(.*?)</span>", play, flags=re.I | re.S):
            class_match = re.search(r'class=["\']([^"\']*)', attrs, flags=re.I)
            classes = (class_match.group(1).split() if class_match else [])
            text = clean_html(body)
            if not text or text == "vs":
                continue
            if any(flag in classes for flag in ("win", "lose", "draw", "same")):
                if re.fullmatch(r"\d+", text):
                    scores.append(int(text))
            elif not classes:
                teams.append(text)
        relay = " ".join(str(cell.get("Text") or "") for cell in cells if "relay" in (cell.get("Class") or "").lower() or "etc" in (cell.get("Class") or "").lower())
        game_match = re.search(r"gameId=([A-Za-z0-9]+)", relay)
        if len(teams) < 2 or len(scores) < 2:
            continue
        date = datetime.strptime(f"{season}.{current_date}", "%Y.%m.%d").date().isoformat()
        stadium = next((clean_html(cell.get("Text")) for cell in cells if (cell.get("Class") or "") == "field"), "")
        games.append({
            "game_id": game_match.group(1) if game_match else f"{date}-{teams[0]}-{teams[-1]}",
            "season": season,
            "competition": "regular",
            "date": date,
            "away_team": teams[0],
            "home_team": teams[-1],
            "away_score": scores[0],
            "home_score": scores[1],
            "stadium": stadium,
            "source_url": URL,
        })
    return games


def build(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    games = pd.DataFrame(item for path in paths for item in parse_month(path))
    games = games.drop_duplicates("game_id").sort_values(["date", "game_id"]).reset_index(drop=True)
    hanwha = games[(games.home_team == "한화") | (games.away_team == "한화")].copy()
    hanwha["is_home"] = hanwha.home_team.eq("한화")
    hanwha["opponent"] = hanwha.away_team.where(hanwha.is_home, hanwha.home_team)
    hanwha["runs_for"] = hanwha.home_score.where(hanwha.is_home, hanwha.away_score)
    hanwha["runs_against"] = hanwha.away_score.where(hanwha.is_home, hanwha.home_score)
    hanwha["result"] = "D"
    hanwha.loc[hanwha.runs_for > hanwha.runs_against, "result"] = "W"
    hanwha.loc[hanwha.runs_for < hanwha.runs_against, "result"] = "L"

    league_rows = []
    for season, season_games in games.groupby("season"):
        for team in sorted(set(season_games.home_team) | set(season_games.away_team)):
            frame = season_games[(season_games.home_team == team) | (season_games.away_team == team)].copy()
            is_home = frame.home_team.eq(team)
            scored = frame.home_score.where(is_home, frame.away_score)
            allowed = frame.away_score.where(is_home, frame.home_score)
            wins = int(scored.gt(allowed).sum())
            losses = int(scored.lt(allowed).sum())
            draws = int(scored.eq(allowed).sum())
            league_rows.append({"season": season, "team": team, "games": len(frame),
                                "wins": wins, "losses": losses, "draws": draws,
                                "win_rate": wins / (wins + losses) if wins + losses else None})
    league = pd.DataFrame(league_rows)
    league["rank"] = league.groupby("season")["win_rate"].rank(method="min", ascending=False).astype(int)

    summaries = []
    for season, frame in hanwha.groupby("season"):
        wins = int(frame.result.eq("W").sum())
        losses = int(frame.result.eq("L").sum())
        draws = int(frame.result.eq("D").sum())
        rank = int(league[(league.season == season) & (league.team == "한화")].iloc[0]["rank"])
        batting_average, era = OFFICIAL_TEAM_RATES[int(season)]
        attendance_total, attendance_average = OFFICIAL_ATTENDANCE[int(season)]
        summaries.append({
            "season": season, "competition": "regular", "team_id": "hanwha-eagles",
            "team_name": "한화 이글스", "rank": rank, "games": len(frame), "wins": wins,
            "losses": losses, "draws": draws,
            "win_rate": round(wins / (wins + losses), 3) if wins + losses else None,
            "runs_for": int(frame.runs_for.sum()), "runs_against": int(frame.runs_against.sum()),
            "batting_average": batting_average, "era": era,
            "attendance_total": attendance_total, "attendance_average": attendance_average,
            "source_url": TEAM_HISTORY_PAGE,
        })
    seasons = pd.DataFrame(summaries).sort_values("season")
    observed = {int(row.season): (int(row.wins), int(row.losses), int(row.draws)) for row in seasons.itertuples()}
    if observed != OFFICIAL_WLD:
        raise ValueError(f"game totals do not match KBO official records: {observed}")
    if not seasons.games.eq(144).all():
        raise ValueError(f"incomplete seasons: {seasons.loc[seasons.games.ne(144), ['season', 'games']].to_dict('records')}")
    complete = seasons.set_index("season").games.eq(144)
    manifest = {
        "source": "KBO public schedule web-service and official historical tables",
        "source_urls": [URL, TEAM_HISTORY_PAGE, CROWD_HISTORY_PAGE],
        "scope": "KBO regular season, Hanwha Eagles, 2015-2025",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "league_games": len(games), "hanwha_games": len(hanwha),
        "season_game_counts": {str(int(k)): int(v) for k, v in seasons.set_index("season").games.items()},
        "complete_144_game_seasons": [int(x) for x in complete[complete].index],
        "raw_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    }
    return hanwha, seasons, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end", type=int, default=2025)
    parser.add_argument("--delay", type=float, default=1.2)
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update(HEADERS)
    paths = []
    for season in range(args.start, args.end + 1):
        for month in range(3, 12):
            paths.append(fetch_month(session, season, month, args.delay))
        print(f"checkpointed {season}", flush=True)
    games, seasons, manifest = build(paths)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, frame in (("hanwha_games_2015_2025.parquet", games), ("team_seasons_2015_2025.parquet", seasons)):
        temporary = OUT / f"{name}.tmp"
        frame.to_parquet(temporary, index=False)
        os.replace(temporary, OUT / name)
    atomic_json(OUT / "kbo_game_history_source.json", manifest)
    print(f"wrote {len(games)} Hanwha games and {len(seasons)} season summaries", flush=True)


if __name__ == "__main__":
    main()
