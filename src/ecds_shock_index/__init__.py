"""Core computation module for the ECDS Shock Index.

The module exposes factor-level scoring helpers and a calculator class
that combines factor values using a weighted average.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Risk tier thresholds (inclusive lower bound)
# ---------------------------------------------------------------------------

RISK_TIERS: dict[str, tuple[float, float]] = {
    "low": (0.0, 0.25),
    "moderate": (0.25, 0.50),
    "high": (0.50, 0.75),
    "critical": (0.75, 1.01),
}


def _clip_01(value: float) -> float:
    """Clamp a numeric value to the inclusive range [0, 1]."""
    return max(0.0, min(1.0, value))


# ---------------------------------------------------------------------------
# Factor-level scoring helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Risk classification
# ---------------------------------------------------------------------------


def classify_risk(score: float) -> str:
    """Return a risk tier label for a shock index score.

    Tiers:
        low      [0.00, 0.25)
        moderate [0.25, 0.50)
        high     [0.50, 0.75)
        critical [0.75, 1.00]
    """
    score = _clip_01(score)
    for tier, (lo, hi) in RISK_TIERS.items():
        if lo <= score < hi:
            return tier
    return "critical"


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------


@dataclass
class ShockIndexCalculator:
    """Calculator for combining ECDS Shock Index components.

    The default weighting favors completeness and measure weight while still
    accounting for variance and cutpoint pressure.

    Raises ``ValueError`` during ``__post_init__`` if weights are negative
    or do not sum to 1.0 (within tolerance of 1e-6).
    """

    alpha_ccs: float = 0.35
    beta_eav: float = 0.25
    gamma_cpr: float = 0.20
    delta_wm: float = 0.20

    def __post_init__(self) -> None:
        weights = [self.alpha_ccs, self.beta_eav, self.gamma_cpr, self.delta_wm]
        if any(w < 0 for w in weights):
            raise ValueError("All weights must be non-negative")
        total = sum(weights)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1.0 (got {total})")

    def calculate(self, ccs: float, eav: float, cpr: float, wm: float) -> float:
        """Compute weighted ECDS Shock Index from normalized inputs."""
        weighted = (
            self.alpha_ccs * _clip_01(ccs)
            + self.beta_eav * _clip_01(eav)
            + self.gamma_cpr * _clip_01(cpr)
            + self.delta_wm * _clip_01(wm)
        )
        return _clip_01(weighted)

    # ------------------------------------------------------------------
    # Batch helpers
    # ------------------------------------------------------------------

    def score_dataframe(
        self,
        df: pd.DataFrame,
        max_shift: float = 0.5,
        max_weight: float = 5.0,
    ) -> pd.DataFrame:
        """Compute shock index for each row of a DataFrame.

        The DataFrame must contain the columns:
            completeness_rate, mapping_coverage, variance_ratio,
            cutpoint_shift, measure_weight

        Returns the input DataFrame with new columns appended:
            ccs, eav, cpr, wm, shock_index, risk_tier
        """
        required = {
            "completeness_rate",
            "mapping_coverage",
            "variance_ratio",
            "cutpoint_shift",
            "measure_weight",
        }
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame is missing required columns: {sorted(missing)}")

        result = df.copy()
        result["ccs"] = result.apply(
            lambda r: ccs_score(r["completeness_rate"], r["mapping_coverage"]),
            axis=1,
        )
        result["eav"] = result["variance_ratio"].apply(eav_score)
        result["cpr"] = result["cutpoint_shift"].apply(
            lambda v: cpr_score(v, max_shift=max_shift),
        )
        result["wm"] = result["measure_weight"].apply(
            lambda v: wm_score(v, max_weight=max_weight),
        )
        result["shock_index"] = result.apply(
            lambda r: self.calculate(ccs=r["ccs"], eav=r["eav"], cpr=r["cpr"], wm=r["wm"]),
            axis=1,
        )
        result["risk_tier"] = result["shock_index"].apply(classify_risk)
        return result

    def aggregate_contract(self, scored_df: pd.DataFrame) -> dict[str, Any]:
        """Aggregate scored measures to a contract-level summary.

        ``scored_df`` must be output from ``score_dataframe`` (i.e. it must
        contain ``shock_index`` and ``measure_weight`` columns).

        Returns a dict with:
            weighted_shock_index – measure-weight-weighted average index
            mean_shock_index     – simple average
            max_shock_index      – worst-case measure
            measure_count        – number of measures
            risk_tier            – tier for the weighted index
        """
        required = {"shock_index", "measure_weight"}
        missing = required - set(scored_df.columns)
        if missing:
            raise ValueError(f"DataFrame is missing required columns: {sorted(missing)}")

        total_weight = scored_df["measure_weight"].sum()
        if total_weight == 0:
            weighted = 0.0
        else:
            weighted = (
                scored_df["shock_index"] * scored_df["measure_weight"]
            ).sum() / total_weight

        return {
            "weighted_shock_index": round(weighted, 4),
            "mean_shock_index": round(scored_df["shock_index"].mean(), 4),
            "max_shock_index": round(scored_df["shock_index"].max(), 4),
            "measure_count": len(scored_df),
            "risk_tier": classify_risk(weighted),
        }


__all__ = [
    "RISK_TIERS",
    "ShockIndexCalculator",
    "classify_risk",
    "ccs_score",
    "cpr_score",
    "eav_score",
    "wm_score",
]
