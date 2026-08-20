from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import pandas as pd

SCRIPT=Path(__file__).parents[1]/"scripts"/"06_import_player_seasons.py"
spec=spec_from_file_location("player_import",SCRIPT); module=module_from_spec(spec); spec.loader.exec_module(module)

def test_player_import_recalculates_rates(tmp_path):
    h=tmp_path/"h.csv"; p=tmp_path/"p.csv"; out=tmp_path/"out"
    pd.DataFrame([{"season":2025,"competition":"regular","source_player_id":"h1","player_name":"테스트 타자","team_id":"hanwha-eagles","position":"내야수","games":10,"source_url":"user-file","pa":100,"ab":90,"hits":27,"doubles":5,"triples":1,"home_runs":3,"walks":8,"hbp":1,"sacrifice_flies":1,"rbi":20}]).to_csv(h,index=False)
    pd.DataFrame([{"season":2025,"competition":"regular","source_player_id":"p1","player_name":"테스트 투수","team_id":"hanwha-eagles","position":"투수","games":10,"source_url":"user-file","outs_recorded":90,"earned_runs":10,"hits_allowed":25,"walks":5,"strikeouts":30,"saves":0}]).to_csv(p,index=False)
    hitters,pitchers=module.build(h,p,out)
    assert hitters.loc[0,"avg"]==.300 and hitters.loc[0,"ops"]==.838
    assert pitchers.loc[0,"innings"]=="30.0" and pitchers.loc[0,"era"]==3.0
