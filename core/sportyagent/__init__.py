"""SportyAgent: make SportyBet's published costs visible.

This package does not forecast winners. Phase 0 ships the repo skeleton,
the published accumulator multiplier table, and a local page.
"""

__version__ = "0.1.0"

from sportyagent.sim.accumulator import payout_multiplier

__all__ = ["__version__", "payout_multiplier"]
