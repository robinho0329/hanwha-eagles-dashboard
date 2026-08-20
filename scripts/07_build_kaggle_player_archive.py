"""Build 2015-2025 Hanwha player seasons from the CC BY-SA 4.0 Kaggle dataset."""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd

RAW=Path("data/raw/licensed-kaggle"); OUT=Path("data/processed")
SOURCE="https://www.kaggle.com/datasets/netsong/kbo-player-dataset-by-regular-season-1982-2025"

def outs(value: object) -> int:
    text=str(value).strip(); whole, _, fraction=text.partition(" ")
    # Spreadsheet software converted the literal 1/3 to the date-like string 01-Mar in five rows.
    if text == "01-Mar": return 1
    result=int(whole)*3
    if fraction: result += {"1/3":1,"2/3":2}[fraction]
    return result

def half_up(series: pd.Series, digits: int) -> pd.Series:
    factor=10**digits
    return (np.floor(series*factor+0.5+1e-9)/factor).where(series.notna())

def main() -> None:
    b=pd.read_csv(RAW/"batting_1982_2025.csv"); p=pd.read_csv(RAW/"pitching_1982_2025.csv")
    b=b[b["Season"].between(2015,2025)&b["Team"].eq("한화")].copy()
    p=p[p["Season"].between(2015,2025)&p["Team"].eq("한화")].copy()
    h=pd.DataFrame({"season":b.Season,"competition":"regular","source_player_id":b.Id.astype(str),
        "player_name":b.Player,"team_id":"hanwha-eagles","position":b.Position,"games":b.G,
        "source_url":b.URL,"pa":b.PA,"ab":b.AB,"runs":b.R,"hits":b.H,"doubles":b["2B"],
        "triples":b["3B"],"home_runs":b.HR,"walks":b.BB,"hbp":b.HBP,"strikeouts":b.SO,
        "stolen_bases":b.SB,"sacrifice_flies":b.SF,"rbi":b.RBI})
    singles=h.hits-h.doubles-h.triples-h.home_runs
    h["avg"]=(h.hits/h.ab.replace(0,np.nan)).round(3)
    h["obp"]=((h.hits+h.walks+h.hbp)/(h.ab+h.walks+h.hbp+h.sacrifice_flies).replace(0,np.nan)).round(3)
    h["slg"]=((singles+2*h.doubles+3*h.triples+4*h.home_runs)/h.ab.replace(0,np.nan)).round(3)
    h["ops"]=(h.obp+h.slg).round(3)
    ps=pd.DataFrame({"season":p.Season,"competition":"regular","source_player_id":p.Id.astype(str),
        "player_name":p.Player,"team_id":"hanwha-eagles","position":p.Position,"games":p.G,
        "source_url":p.URL,"wins":p.W,"losses":p.L,"saves":p.SV,"holds":p.HLD,
        "outs_recorded":p.IP.map(outs),"earned_runs":p.ER,"hits_allowed":p.H,"home_runs_allowed":p.HR,
        "walks":p.BB,"hbp":p.HBP,"strikeouts":p.SO})
    valid=ps.outs_recorded.replace(0,np.nan); ps["innings"]=ps.outs_recorded.map(lambda x:f"{x//3}.{x%3}")
    ps["era"]=half_up(ps.earned_runs*27/valid,2); ps["whip"]=half_up((ps.hits_allowed+ps.walks)*3/valid,2)
    ps["k9"]=half_up(ps.strikeouts*27/valid,2); ps["bb9"]=half_up(ps.walks*27/valid,2)
    for name,frame in (("hitter_seasons.parquet",h),("pitcher_seasons.parquet",ps)):
        target=OUT/name; temporary=OUT/(name+".tmp"); frame.to_parquet(temporary,index=False); os.replace(temporary,target)
    print(f"wrote {len(h)} hitter seasons and {len(ps)} pitcher seasons; source={SOURCE}; license=CC BY-SA 4.0")

if __name__ == "__main__": main()
