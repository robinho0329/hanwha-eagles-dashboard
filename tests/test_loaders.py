import json
from pathlib import Path

from _lib import directory_key, load_json


def test_json_loader_invalidates_when_file_changes(tmp_path: Path) -> None:
    target = tmp_path / "sample.json"
    target.write_text(json.dumps({"value": 1}), encoding="utf-8")
    assert load_json(target)["value"] == 1

    target.write_text(json.dumps({"value": 200}), encoding="utf-8")
    assert load_json(target)["value"] == 200


def test_directory_key_changes_when_file_changes(tmp_path: Path) -> None:
    target = tmp_path / "one.txt"
    target.write_text("a", encoding="utf-8")
    before = directory_key(tmp_path)
    target.write_text("a much longer value", encoding="utf-8")
    after = directory_key(tmp_path)
    assert before != after
