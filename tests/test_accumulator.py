"""Published AnyWin payout multipliers, verified 2026-11-19/20."""

import pytest

from sportyagent import payout_multiplier
from sportyagent.sim.accumulator import ANYWIN_ODDS_KEYS, MAX_LEGS, MIN_LEGS


def test_two_and_three_legs_pay_ninety_five_percent_of_advertised_odds():
    assert payout_multiplier(2) == 0.95
    assert payout_multiplier(3) == 0.95


def test_fifty_leg_slip_pays_fifteen_percent_of_advertised_odds():
    assert payout_multiplier(50) == 0.15
    assert payout_multiplier(47) == 0.15


def test_table_covers_every_leg_count_from_two_to_fifty():
    assert set(ANYWIN_ODDS_KEYS) == set(range(MIN_LEGS, MAX_LEGS + 1))
    assert ANYWIN_ODDS_KEYS[2] == 0.95
    assert ANYWIN_ODDS_KEYS[50] == 0.15
    # The published curve is non-increasing as legs grow.
    previous = ANYWIN_ODDS_KEYS[MIN_LEGS]
    for legs in range(MIN_LEGS, MAX_LEGS + 1):
        value = ANYWIN_ODDS_KEYS[legs]
        assert 0 < value <= 1
        assert value <= previous
        previous = value


def test_out_of_range_and_bad_types_are_rejected():
    with pytest.raises(ValueError):
        payout_multiplier(1)
    with pytest.raises(ValueError):
        payout_multiplier(51)
    with pytest.raises(TypeError):
        payout_multiplier(2.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        payout_multiplier(True)  # type: ignore[arg-type]
