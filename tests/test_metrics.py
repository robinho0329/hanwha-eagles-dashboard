import pytest

from _lib import format_innings, innings_to_outs, normalize_name


@pytest.mark.parametrize(
    ("innings", "outs"),
    [("3003", 9009), ("2394 2/3", 7184), ("40 1/3", 121), (7, 21)],
)
def test_innings_to_outs(innings, outs) -> None:
    assert innings_to_outs(innings) == outs
    assert innings_to_outs(format_innings(outs)) == outs


def test_invalid_innings_fraction() -> None:
    with pytest.raises(ValueError):
        innings_to_outs("10.2")


def test_normalize_name_is_conservative() -> None:
    assert normalize_name("  김태균  ") == "김태균"
    assert normalize_name("Ryu   Hyun-jin") == "Ryu Hyun-jin"
