from _lib import PROCESSED, load_json, load_parquet


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


def test_2015_2025_game_archive_is_complete() -> None:
    games = load_parquet(PROCESSED / "hanwha_games_2015_2025.parquet")
    seasons = load_parquet(PROCESSED / "team_seasons_2015_2025.parquet")
    assert len(games) == 1_584
    assert games["game_id"].is_unique
    assert games.groupby("season").size().eq(144).all()
    assert len(seasons) == 11
    assert seasons["games"].eq(144).all()
    assert seasons.loc[seasons.season.eq(2025), ["wins", "losses", "draws", "rank"]].iloc[0].tolist() == [83, 57, 4, 2]
