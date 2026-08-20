"""Validate user-supplied player-season CSV files and build archive parquet files."""
from __future__ import annotations
import argparse, os
from pathlib import Path
import numpy as np
import pandas as pd

COMMON = ["season","competition","source_player_id","player_name","team_id","position","games","source_url"]
HITTER = COMMON + ["pa","ab","hits","doubles","triples","home_runs","walks","hbp","sacrifice_flies","rbi"]
PITCHER = COMMON + ["outs_recorded","earned_runs","hits_allowed","walks","strikeouts","saves"]

def read_and_validate(path: Path, required: list[str], kind: str) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"source_player_id":"string","team_id":"string"})
    missing = set(required) - set(frame.columns)
    if missing: raise ValueError(f"{kind}: missing columns {sorted(missing)}")
    frame = frame[required].copy()
    numeric = [c for c in required if c not in {"competition","source_player_id","player_name","team_id","position","source_url"}]
    for column in numeric: frame[column] = pd.to_numeric(frame[column], errors="raise")
    if not frame["season"].between(2015, 2026).all(): raise ValueError(f"{kind}: season must be 2015..2026")
    if not frame["competition"].eq("regular").all(): raise ValueError(f"{kind}: only regular season is accepted")
    if not frame["team_id"].eq("hanwha-eagles").all(): raise ValueError(f"{kind}: non-Hanwha row found")
    if frame.duplicated(["season","competition","source_player_id","team_id"]).any(): raise ValueError(f"{kind}: duplicate player-season")
    if (frame[numeric] < 0).any().any(): raise ValueError(f"{kind}: negative counting stat")
    return frame

def build(hitters_csv: Path, pitchers_csv: Path, output: Path) -> tuple[pd.DataFrame,pd.DataFrame]:
    h = read_and_validate(hitters_csv, HITTER, "hitters")
    p = read_and_validate(pitchers_csv, PITCHER, "pitchers")
    if (h["hits"] > h["ab"]).any() or (h[["doubles","triples","home_runs"]].sum(axis=1) > h["hits"]).any():
        raise ValueError("hitters: component hits exceed totals")
    singles = h["hits"] - h["doubles"] - h["triples"] - h["home_runs"]
    h["avg"] = (h["hits"] / h["ab"].replace(0,np.nan)).round(3)
    h["obp"] = ((h["hits"]+h["walks"]+h["hbp"]) / (h["ab"]+h["walks"]+h["hbp"]+h["sacrifice_flies"]).replace(0,np.nan)).round(3)
    h["slg"] = ((singles+2*h["doubles"]+3*h["triples"]+4*h["home_runs"]) / h["ab"].replace(0,np.nan)).round(3)
    h["ops"] = (h["obp"]+h["slg"]).round(3)
    valid_outs = p["outs_recorded"].replace(0,np.nan)
    p["innings"] = p["outs_recorded"].map(lambda value:f"{int(value)//3}.{int(value)%3}")
    p["era"] = (p["earned_runs"]*27/valid_outs).round(2)
    p["whip"] = ((p["hits_allowed"]+p["walks"])*3/valid_outs).round(2)
    p["k9"] = (p["strikeouts"]*27/valid_outs).round(2)
    p["bb9"] = (p["walks"]*27/valid_outs).round(2)
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in (("hitter_seasons.parquet",h),("pitcher_seasons.parquet",p)):
        target, temporary = output/name, output/(name+".tmp")
        frame.to_parquet(temporary,index=False); os.replace(temporary,target)
    return h,p

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("hitters",type=Path); parser.add_argument("pitchers",type=Path)
    parser.add_argument("--output",type=Path,default=Path("data/processed")); args=parser.parse_args()
    h,p=build(args.hitters,args.pitchers,args.output); print(f"wrote {len(h)} hitter and {len(p)} pitcher seasons")

if __name__ == "__main__": main()
