"""Normalize a lawfully supplied KBO team-history HTML file without network access."""
from __future__ import annotations
import argparse, hashlib, os
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import pandas as pd

SOURCE_URL = "https://www.koreabaseball.com/Record/History/Team/Record.aspx"
TEAM_IDS = {"빙그레":"hanwha-eagles","한화":"hanwha-eagles","LG":"lg-twins","두산":"doosan-bears","OB":"doosan-bears","KIA":"kia-tigers","해태":"kia-tigers","삼성":"samsung-lions","롯데":"lotte-giants","SSG":"ssg-landers","SK":"ssg-landers","키움":"kiwoom-heroes","넥센":"kiwoom-heroes","NC":"nc-dinos","KT":"kt-wiz"}
RENAME = {"연도":"season","순위":"rank","팀명":"team_name","경기":"games","승":"wins","패":"losses","무":"draws","승률":"win_rate","타율":"batting_average","방어율":"era"}

def parse_html(path: Path) -> pd.DataFrame:
    payload = path.read_bytes()
    frames = []
    for table in pd.read_html(StringIO(payload.decode("utf-8", errors="replace")), flavor="lxml"):
        table.columns = [str(column).strip() for column in table.columns]
        normalized = table.rename(columns=RENAME)
        if {"season","rank","team_name","games","wins","losses","draws"}.issubset(normalized.columns):
            frames.append(normalized)
    if not frames:
        raise ValueError("No recognized regular-season team table was found")
    result = pd.concat(frames, ignore_index=True)
    result["season"] = pd.to_numeric(result["season"], errors="coerce")
    result = result[result["season"].notna()].copy()
    result["season"] = result["season"].astype(int)
    result["competition"], result["team_id"] = "regular", result["team_name"].map(TEAM_IDS)
    result["season_complete"] = True
    result["as_of_date"] = result["season"].astype(str) + "-12-31"
    result["source_url"], result["fetched_at"] = SOURCE_URL, datetime.now(timezone.utc).isoformat()
    result["raw_sha256"] = hashlib.sha256(payload).hexdigest()
    if result["team_id"].isna().any():
        raise ValueError(f"Unmapped teams: {sorted(result.loc[result['team_id'].isna(), 'team_name'].unique())}")
    for column in ["rank","games","wins","losses","draws","win_rate","batting_average","era"]:
        if column in result: result[column] = pd.to_numeric(result[column], errors="coerce")
    if result.duplicated(["season","team_id"]).any(): raise ValueError("Duplicate season/team rows")
    if not (result["games"] == result["wins"] + result["losses"] + result["draws"]).all():
        raise ValueError("Games do not equal wins + losses + draws")
    calculated = result["wins"] / (result["wins"] + result["losses"])
    if "win_rate" in result and not (result["win_rate"] - calculated).abs().le(0.001).all():
        raise ValueError("Win-rate validation failed")
    ordered = ["season","competition","rank","team_id","team_name","games","wins","losses","draws","batting_average","era","win_rate","season_complete","as_of_date","source_url","fetched_at","raw_sha256"]
    return result[[column for column in ordered if column in result.columns]]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Authorized or user-supplied HTML file")
    parser.add_argument("--output", type=Path, default=Path("data/processed/team_seasons.parquet"))
    args = parser.parse_args()
    frame = parse_html(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    frame.to_parquet(temporary, index=False)
    os.replace(temporary, args.output)
    print(f"wrote {len(frame)} rows to {args.output}")

if __name__ == "__main__": main()
