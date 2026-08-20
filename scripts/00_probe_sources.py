"""Check collection permission before requesting any KBO content page."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.robotparser import RobotFileParser
from _fetch import USER_AGENT, fetch

ROBOTS_URL = "https://www.koreabaseball.com/robots.txt"
TARGET_URL = "https://www.koreabaseball.com/Record/History/Team/Record.aspx"
REPORT_PATH = Path("data/checkpoints/source_probe.json")

def main() -> None:
    response = fetch(ROBOTS_URL)
    parser = RobotFileParser()
    parser.set_url(ROBOTS_URL)
    parser.parse(response.body.decode("utf-8", errors="replace").splitlines())
    allowed = parser.can_fetch(USER_AGENT, TARGET_URL)
    report = {"robots_url": ROBOTS_URL, "target_url": TARGET_URL, "user_agent": USER_AGENT,
              "allowed": allowed, "decision": "continue" if allowed else "blocked",
              "note": "No target page was requested by this probe."}
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not allowed:
        raise SystemExit("KBO crawling blocked by robots.txt; no target page was requested")

if __name__ == "__main__":
    main()
