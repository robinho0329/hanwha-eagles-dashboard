"""Collect a bounded KBO date window from documented TheSportsDB API endpoints."""
from __future__ import annotations
import argparse, hashlib, json, os, time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from _fetch import fetch, save_raw

BASE = "https://www.thesportsdb.com/api/v1/json/123/eventsday.php"
TEAM_ID, LEAGUE_ID = "139826", "4830"
RAW = Path("data/raw/thesportsdb/daily")
OUTPUT = Path("data/processed/hanwha_game_window.json")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=date.fromisoformat, default=date.today())
    parser.add_argument("--days-before", type=int, default=7)
    parser.add_argument("--days-after", type=int, default=7)
    parser.add_argument("--delay", type=float, default=2.1, help="Seconds between API calls")
    args = parser.parse_args()
    if args.days_before + args.days_after + 1 > 200:
        raise ValueError("A single run is capped at 200 API requests")
    games, raw = {}, []
    offsets=range(-args.days_before,args.days_after+1)
    for request_no,offset in enumerate(offsets,1):
        day = args.center + timedelta(days=offset)
        day_dir=RAW/day.isoformat(); cached=sorted(day_dir.glob("*.json"))
        if cached:
            raw_path=cached[-1]; body=raw_path.read_bytes(); source_url=f"{BASE}?d={day.isoformat()}&l={LEAGUE_ID}"
            sha256=hashlib.sha256(body).hexdigest(); payload=json.loads(body)
        else:
            try:
                result=fetch(f"{BASE}?d={day.isoformat()}&l={LEAGUE_ID}")
            except Exception:
                print(f"rate/error pause at {day}; retrying in 60s",flush=True); time.sleep(60)
                result=fetch(f"{BASE}?d={day.isoformat()}&l={LEAGUE_ID}")
            raw_path=save_raw(result,day_dir,suffix=".json"); payload=json.loads(result.body)
            source_url=result.url; sha256=result.sha256
        for event in payload.get("events") or []:
            if TEAM_ID in {str(event.get("idHomeTeam")), str(event.get("idAwayTeam"))}:
                games[str(event["idEvent"])] = event
        raw.append({"date":day.isoformat(), "path":str(raw_path), "sha256":sha256,"source_url":source_url})
        if request_no % 10 == 0: print(f"progress {request_no}/{len(offsets)} days; Hanwha games {len(games)}",flush=True)
        if request_no < len(offsets) and not cached: time.sleep(max(args.delay,0))
    ordered = sorted(games.values(), key=lambda item:(item.get("dateEvent") or "", item.get("strTime") or ""))
    bundle = {"provider":"TheSportsDB", "team_id":TEAM_ID, "league_id":LEAGUE_ID,
              "range":{"from":(args.center-timedelta(days=args.days_before)).isoformat(),
                       "to":(args.center+timedelta(days=args.days_after)).isoformat()},
              "fetched_at":datetime.now(timezone.utc).isoformat(), "games":ordered, "raw":raw}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, OUTPUT)
    print(f"wrote {len(ordered)} Hanwha games from {len(raw)} daily API responses to {OUTPUT}")

if __name__ == "__main__": main()
