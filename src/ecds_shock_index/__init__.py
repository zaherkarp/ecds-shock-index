"""Core computation module for the ECDS Shock Index.

The module exposes factor-level scoring helpers and a calculator class
that combines factor values using a weighted average.
"""

from __future__ import annotations

from dataclasses import dataclass


def _clip_01(value: float) -> float:
    """Clamp a numeric value to the inclusive range [0, 1]."""
    return max(0.0, min(1.0, value))


def ccs_score(completeness_rate: float, mapping_coverage: float) -> float:
    """Compute the Clinical Completeness Score (CCS).

    CCS is the average of data completeness and coding/mapping coverage.
    """
    return _clip_01((completeness_rate + mapping_coverage) / 2.0)


def eav_score(variance_ratio: float, baseline: float = 1.0) -> float:
    """Compute the ECDS Adoption Variability (EAV) score.

    A variance ratio equal to baseline maps to 0.5. Values above baseline
    increase risk toward 1.0, and values below baseline reduce it toward 0.0.
    """
    if baseline <= 0:
        raise ValueError("baseline must be greater than zero")
    normalized = 0.5 + ((variance_ratio / baseline) - 1.0) / 2.0
    return _clip_01(normalized)


def cpr_score(cutpoint_shift: float, max_shift: float = 0.5) -> float:
    """Compute the Cutpoint Pressure Risk (CPR) score.

    cutpoint_shift is expressed as an absolute shift where max_shift
    corresponds to maximum score (1.0).
    """
    if max_shift <= 0:
        raise ValueError("max_shift must be greater than zero")
    return _clip_01(abs(cutpoint_shift) / max_shift)


def wm_score(measure_weight: float, max_weight: float = 5.0) -> float:
    """Compute the Weight Multiplier (WM) score from Stars measure weight."""
    if max_weight <= 0:
        raise ValueError("max_weight must be greater than zero")
    return _clip_01(measure_weight / max_weight)


@dataclass
class ShockIndexCalculator:
    """Calculator for combining ECDS Shock Index components.

    The default weighting favors completeness and measure weight while still
    accounting for variance and cutpoint pressure.
    """

    alpha_ccs: float = 0.35
    beta_eav: float = 0.25
    gamma_cpr: float = 0.20
    delta_wm: float = 0.20

    def calculate(self, ccs: float, eav: float, cpr: float, wm: float) -> float:
        """Compute weighted ECDS Shock Index from normalized inputs."""
        weighted = (
            self.alpha_ccs * _clip_01(ccs)
            + self.beta_eav * _clip_01(eav)
            + self.gamma_cpr * _clip_01(cpr)
            + self.delta_wm * _clip_01(wm)
        )
        return _clip_01(weighted)


__all__ = [
    "ShockIndexCalculator",
    "ccs_score",
    "eav_score",
    "cpr_score",
    "wm_score",
]
