"""Tests for weight-sensitivity analysis (ADR-0007)."""

import pytest

import pandas as pd

from ecds_shock_index import ShockIndexCalculator
from ecds_shock_index.sensitivity import weight_sensitivity


@pytest.fixture()
def scored_df():
    """Score the standard 3-measure fixture with default weights."""
    df = pd.DataFrame(
        {
            "measure_id": ["COL", "BCS", "A1C"],
            "completeness_rate": [0.95, 0.72, 0.85],
            "mapping_coverage": [0.93, 0.68, 0.88],
            "variance_ratio": [1.03, 1.45, 1.10],
            "cutpoint_shift": [0.02, 0.09, 0.05],
            "measure_weight": [1, 1, 3],
        }
    )
    calc = ShockIndexCalculator()
    return calc.score_dataframe(df)


class TestWeightSensitivity:
    def test_default_weights_identity(self, scored_df):
        result = weight_sensitivity(scored_df, deltas=(0.0,))
        assert (result["shock_index_before"] == result["shock_index_after"]).all()
        assert not result["tier_flip"].any()

    def test_oat_bcs_flip(self, scored_df):
        result = weight_sensitivity(scored_df, deltas=(0.05,))
        bcs_alpha_up = result[
            (result["measure_id"] == "BCS")
            & (result["weight_name"] == "alpha_ccs")
            & (result["signed_delta"] == 0.05)
        ]
        assert len(bcs_alpha_up) == 1
        row = bcs_alpha_up.iloc[0]
        assert row["shock_index_after"] == pytest.approx(0.4847428396517264, abs=1e-9)
        assert bool(row["tier_flip"]) is True
        assert row["tier_before"] == "high"
        assert row["tier_after"] == "moderate"

    def test_bcs_straddle_oracle(self, scored_df):
        result_low = weight_sensitivity(scored_df, deltas=(0.00767,))
        bcs_low = result_low[
            (result_low["measure_id"] == "BCS")
            & (result_low["weight_name"] == "alpha_ccs")
            & (result_low["signed_delta"] == 0.00767)
        ]
        assert len(bcs_low) == 1
        assert bool(bcs_low.iloc[0]["tier_flip"]) is False

        result_high = weight_sensitivity(scored_df, deltas=(0.00768,))
        bcs_high = result_high[
            (result_high["measure_id"] == "BCS")
            & (result_high["weight_name"] == "alpha_ccs")
            & (result_high["signed_delta"] == 0.00768)
        ]
        assert len(bcs_high) == 1
        assert bool(bcs_high.iloc[0]["tier_flip"]) is True

    def test_validity_domain_r(self, scored_df):
        result = weight_sensitivity(scored_df, deltas=(0.05,))
        bcs_rows = result[result["measure_id"] == "BCS"]
        assert (bcs_rows["validity_domain_r"] == 0.50).all()

    def test_zero_weights_excluded(self, scored_df):
        result = weight_sensitivity(scored_df, deltas=(0.05,), include_zero_weights=False)
        assert "delta_wm" not in result["weight_name"].values
        assert set(result["weight_name"].unique()) == {"alpha_ccs", "beta_eav", "gamma_cpr"}
