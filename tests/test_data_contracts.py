from _lib import PROCESSED, load_json


def test_retired_numbers_contract() -> None:
    data = load_json(PROCESSED / "retired_numbers.json")
    players = data["players"]
    assert {player["number"] for player in players} == {21, 23, 35, 52}
    assert len({player["player_id"] for player in players}) == 4
    for player in players:
        assert player["source_url"].startswith("https://www.koreabaseball.com/")
        assert player["stats"]
        assert player["milestones"]


def test_manifest_has_no_available_missing_path() -> None:
    manifest = load_json(PROCESSED / "data_manifest.json")
    for dataset in manifest["datasets"]:
        if dataset["status"] == "available":
            assert (PROCESSED.parent.parent / dataset["path"]).exists()
