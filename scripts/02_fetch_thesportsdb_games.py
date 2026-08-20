"""Fetch Hanwha game summaries through TheSportsDB's documented API endpoints."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from pathlib import Path
from _fetch import fetch, save_raw

TEAM_ID = "139826"
BASE = "https://www.thesportsdb.com/api/v1/json/123/"
RAW = Path("data/raw/thesportsdb/games")
OUTPUT = Path("data/processed/live_games.json")

def main() -> None:
    bundle = {"provider":"TheSportsDB", "team_id":TEAM_ID,
              "fetched_at":datetime.now(timezone.utc).isoformat(), "items":{}}
    for name, endpoint, field in (("next","eventsnext.php","events"),("last","eventslast.php","results")):
        result = fetch(f"{BASE}{endpoint}?id={TEAM_ID}")
        raw_path = save_raw(result, RAW / name, suffix=".json")
        payload = json.loads(result.body)
        bundle["items"][name] = payload.get(field) or []
        bundle.setdefault("raw", {})[name] = {"path":str(raw_path), "sha256":result.sha256,
                                                "source_url":result.url}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, OUTPUT)
    print(f"wrote {OUTPUT}")

if __name__ == "__main__": main()
