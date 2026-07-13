"""Weight-sensitivity analysis for the ECDS Shock Index composite.

Provides one-at-a-time (OAT) perturbation on the 3-hazard-weight simplex,
as required by OECD/JRC Handbook step 7 and ADR-0007.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ecds_shock_index import ShockIndexCalculator, classify_risk

if TYPE_CHECKING:
    from collections.abc import Sequence


_WEIGHT_NAMES = ("alpha_ccs", "beta_eav", "gamma_cpr")


def weight_sensitivity(
    scored_df: pd.DataFrame,
    calculator: ShockIndexCalculator | None = None,
    deltas: Sequence[float] = (0.05, 0.10, 0.20),
    include_zero_weights: bool = False,
) -> pd.DataFrame:
    """OAT weight-sensitivity analysis on the hazard-weight simplex.

    For each weight, perturbs by +delta and -delta while renormalizing the
    remaining weights proportionally to stay on the simplex. Returns a tidy
    long DataFrame with one row per (weight, signed_delta, measure).

    Parameters
    ----------
    scored_df
        Output of ``ShockIndexCalculator.score_dataframe`` — must contain
        ``measure_id``, ``ccs``, ``eav``, ``cpr``, and ``shock_index`` columns.
    calculator
        Calculator whose weights to perturb. Defaults to ``ShockIndexCalculator()``.
    deltas
        Absolute perturbation magnitudes to apply in both directions.
    include_zero_weights
        If False (default), skip weights that are zero (e.g. delta_wm under
        ADR-0002). If True, include them as inclusion/exclusion probes.

    Returns
    -------
    pd.DataFrame
        Columns: weight_name, signed_delta, l1_radius, alpha_ccs, beta_eav,
        gamma_cpr, measure_id, shock_index_before, shock_index_after,
        tier_before, tier_after, tier_flip, validity_domain_r.
    """
    if calculator is None:
        calculator = ShockIndexCalculator()

    base_weights = {
        "alpha_ccs": calculator.alpha_ccs,
        "beta_eav": calculator.beta_eav,
        "gamma_cpr": calculator.gamma_cpr,
    }

    score_cols = {"ccs", "eav", "cpr", "shock_index", "measure_id"}
    missing = score_cols - set(scored_df.columns)
    if missing:
        raise ValueError(f"scored_df is missing required columns: {sorted(missing)}")

    rows: list[dict] = []

    for wname in _WEIGHT_NAMES:
        w_base = base_weights[wname]
        if w_base == 0.0 and not include_zero_weights:
            continue

        others = {k: v for k, v in base_weights.items() if k != wname}
        others_sum = sum(others.values())
        min_other = min(others.values()) if others else 0.0
        validity_r = 2.0 * min(w_base, min_other) if others_sum > 0 else 0.0

        for delta in deltas:
            for sign in (+1, -1):
                sd = sign * delta
                w_new = w_base + sd
                if w_new < 0 or w_new > 1.0:
                    continue
                remaining = 1.0 - w_new
                if others_sum == 0:
                    continue
                perturbed = {wname: w_new}
                for oname, oval in others.items():
                    perturbed[oname] = remaining * oval / others_sum

                l1 = sum(abs(perturbed[k] - base_weights[k]) for k in _WEIGHT_NAMES)

                for _, row in scored_df.iterrows():
                    si_before = row["shock_index"]
                    si_after = (
                        perturbed["alpha_ccs"] * row["ccs"]
                        + perturbed["beta_eav"] * row["eav"]
                        + perturbed["gamma_cpr"] * row["cpr"]
                    )
                    si_after = max(0.0, min(1.0, si_after))
                    tier_before = classify_risk(si_before)
                    tier_after = classify_risk(si_after)
                    rows.append({
                        "weight_name": wname,
                        "signed_delta": sd,
                        "l1_radius": round(l1, 12),
                        "alpha_ccs": perturbed["alpha_ccs"],
                        "beta_eav": perturbed["beta_eav"],
                        "gamma_cpr": perturbed["gamma_cpr"],
                        "measure_id": row["measure_id"],
                        "shock_index_before": si_before,
                        "shock_index_after": si_after,
                        "tier_before": tier_before,
                        "tier_after": tier_after,
                        "tier_flip": tier_before != tier_after,
                        "validity_domain_r": validity_r,
                    })

    return pd.DataFrame(rows)


__all__ = ["weight_sensitivity"]
