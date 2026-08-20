"""Collect the free Hanwha roster slice and any player stats exposed by TheSportsDB."""
from __future__ import annotations
import json, os, time
from datetime import datetime, timezone
from pathlib import Path
from _fetch import fetch, save_raw

BASE, TEAM_ID = "https://www.thesportsdb.com/api/v1/json/123/", "139826"
RAW = Path("data/raw/thesportsdb/players")
OUTPUT = Path("data/processed/current_players_thesportsdb.json")

def main() -> None:
    roster_result = fetch(f"{BASE}lookup_all_players.php?id={TEAM_ID}")
    roster_path = save_raw(roster_result, RAW / "roster", suffix=".json")
    roster = json.loads(roster_result.body).get("player") or []
    players, stats_raw = [], []
    for player in roster:
        player_id = str(player["idPlayer"])
        stat_result = fetch(f"{BASE}lookupplayerstats.php?id={player_id}")
        stat_path = save_raw(stat_result, RAW / "stats" / player_id, suffix=".json")
        provider_stats = json.loads(stat_result.body).get("playerstats") or []
        stats = [row for row in provider_stats if str(row.get("idLeague")) == "4830"]
        cc = (player.get("strCreativeCommons") or "").strip()
        image_eligible = bool(cc and cc.lower() not in {"no", "none", "n/a"})
        players.append({
            "source_player_id":player_id, "source_team_id":str(player.get("idTeam") or ""),
            "player_name":player.get("strPlayer"), "nationality":player.get("strNationality"),
            "birth_date":player.get("dateBorn"), "position":player.get("strPosition"),
            "status":player.get("strStatus"), "height":player.get("strHeight"),
            "weight":player.get("strWeight"), "creative_commons":cc or None,
            "image_eligible":image_eligible,
            "image_candidate_url":player.get("strThumb") if image_eligible else None,
            "kbo_stats":stats, "provider_stats_seen":len(provider_stats),
        })
        stats_raw.append({"player_id":player_id, "path":str(stat_path), "sha256":stat_result.sha256,
                          "source_url":stat_result.url})
        time.sleep(.2)
    bundle = {"provider":"TheSportsDB", "scope":"free API roster slice; not a complete KBO roster",
              "team_id":TEAM_ID, "fetched_at":datetime.now(timezone.utc).isoformat(),
              "players":players, "raw":{"roster":{"path":str(roster_path),"sha256":roster_result.sha256,
              "source_url":roster_result.url}, "stats":stats_raw}}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, OUTPUT)
    print(f"wrote {len(players)} players; {sum(bool(p['kbo_stats']) for p in players)} have KBO stats; "
          f"{sum(p['image_eligible'] for p in players)} have image-license candidates")

if __name__ == "__main__": main()
