"""Published SportyBet accumulator payout multipliers.

Source: GET /api/ng/factsCenter/betType/config (AnyWin oddsKeys).
Verified against the live API on 2026-11-19/20. These are selection
factors applied to the payout as the number of legs grows; they are not
odds, and they are not forecasts.
"""

from __future__ import annotations

# legs -> multiplier, copied from the AnyWin oddsKeys object.
# 2-3 legs: 0.95; 47+ legs: 0.15. A 50-leg slip is paid at 0.15 of
# the advertised odds.
ANYWIN_ODDS_KEYS: dict[int, float] = {
    2: 0.95,
    3: 0.95,
    4: 0.90,
    5: 0.90,
    6: 0.85,
    7: 0.85,
    8: 0.80,
    9: 0.80,
    10: 0.80,
    11: 0.75,
    12: 0.75,
    13: 0.75,
    14: 0.75,
    15: 0.65,
    16: 0.65,
    17: 0.65,
    18: 0.60,
    19: 0.55,
    20: 0.55,
    21: 0.55,
    22: 0.55,
    23: 0.50,
    24: 0.45,
    25: 0.45,
    26: 0.45,
    27: 0.45,
    28: 0.45,
    29: 0.40,
    30: 0.40,
    31: 0.35,
    32: 0.30,
    33: 0.25,
    34: 0.25,
    35: 0.25,
    36: 0.25,
    37: 0.25,
    38: 0.25,
    39: 0.20,
    40: 0.20,
    41: 0.20,
    42: 0.20,
    43: 0.17,
    44: 0.17,
    45: 0.17,
    46: 0.17,
    47: 0.15,
    48: 0.15,
    49: 0.15,
    50: 0.15,
}

MIN_LEGS = 2
MAX_LEGS = 50


def payout_multiplier(legs: int) -> float:
    """Return the published payout factor for an n-leg AnyWin slip.

    Raises ValueError if ``legs`` is outside the published 2-50 range.
    """
    if not isinstance(legs, int) or isinstance(legs, bool):
        raise TypeError("legs must be an int")
    if legs < MIN_LEGS or legs > MAX_LEGS:
        raise ValueError(
            f"legs must be between {MIN_LEGS} and {MAX_LEGS} inclusive, got {legs}"
        )
    return ANYWIN_ODDS_KEYS[legs]
