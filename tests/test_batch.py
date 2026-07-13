"""Tests for batch scoring and contract-level aggregation."""

import pytest

import pandas as pd

from ecds_shock_index import ShockIndexCalculator, classify_risk


@pytest.fixture()
def sample_df():
    return pd.DataFrame(
        {
            "measure_id": ["COL", "BCS", "A1C"],
            "completeness_rate": [0.95, 0.72, 0.85],
            "mapping_coverage": [0.93, 0.68, 0.88],
            "variance_ratio": [1.03, 1.45, 1.10],
            "cutpoint_shift": [0.02, 0.09, 0.05],
            "measure_weight": [1, 1, 3],
        }
    )


class TestScoreDataframe:
    def test_returns_expected_columns(self, sample_df):
        calc = ShockIndexCalculator()
        result = calc.score_dataframe(sample_df)
        for col in ("ccs", "eav", "cpr", "wm", "shock_index", "risk_tier"):
            assert col in result.columns

    def test_all_scores_between_zero_and_one(self, sample_df):
        calc = ShockIndexCalculator()
        result = calc.score_dataframe(sample_df)
        for col in ("ccs", "eav", "cpr", "wm", "shock_index"):
            assert (result[col] >= 0).all()
            assert (result[col] <= 1).all()

    def test_risk_tiers_are_valid(self, sample_df):
        calc = ShockIndexCalculator()
        result = calc.score_dataframe(sample_df)
        valid = {"low", "moderate", "high", "critical"}
        assert set(result["risk_tier"].unique()).issubset(valid)

    def test_row_count_preserved(self, sample_df):
        calc = ShockIndexCalculator()
        result = calc.score_dataframe(sample_df)
        assert len(result) == len(sample_df)

    def test_missing_column_raises(self):
        df = pd.DataFrame({"measure_id": ["A"]})
        calc = ShockIndexCalculator()
        with pytest.raises(ValueError, match="missing required columns"):
            calc.score_dataframe(df)

    def test_custom_max_params(self, sample_df):
        calc = ShockIndexCalculator()
        result = calc.score_dataframe(sample_df, max_shift=1.0, max_weight=3.0)
        assert len(result) == 3

    def test_latent_share_threading(self, sample_df):
        calc = ShockIndexCalculator()
        result = calc.score_dataframe(sample_df, latent_share=0.50)
        bcs = result[result["measure_id"] == "BCS"].iloc[0]
        assert bcs["cpr"] == pytest.approx(0.54)
        assert bcs["shock_index"] == pytest.approx(0.4337665313250656)
        assert bcs["risk_tier"] == "moderate"


class TestAggregateContract:
    def test_summary_keys(self, sample_df):
        calc = ShockIndexCalculator()
        scored = calc.score_dataframe(sample_df)
        summary = calc.aggregate_contract(scored)
        assert set(summary.keys()) == {
            "weighted_shock_index",
            "mean_shock_index",
            "max_shock_index",
            "measure_count",
            "risk_tier",
        }

    def test_measure_count(self, sample_df):
        calc = ShockIndexCalculator()
        scored = calc.score_dataframe(sample_df)
        summary = calc.aggregate_contract(scored)
        assert summary["measure_count"] == 3

    def test_weighted_index_is_float(self, sample_df):
        calc = ShockIndexCalculator()
        scored = calc.score_dataframe(sample_df)
        summary = calc.aggregate_contract(scored)
        assert isinstance(summary["weighted_shock_index"], float)

    def test_max_gte_mean(self, sample_df):
        calc = ShockIndexCalculator()
        scored = calc.score_dataframe(sample_df)
        summary = calc.aggregate_contract(scored)
        assert summary["max_shock_index"] >= summary["mean_shock_index"]

    def test_missing_columns_raises(self):
        df = pd.DataFrame({"foo": [1]})
        calc = ShockIndexCalculator()
        with pytest.raises(ValueError, match="missing required columns"):
            calc.aggregate_contract(df)

    def test_zero_total_weight(self):
        df = pd.DataFrame({"shock_index": [0.5, 0.6], "measure_weight": [0, 0]})
        calc = ShockIndexCalculator()
        summary = calc.aggregate_contract(df)
        assert summary["weighted_shock_index"] == 0.0


class TestNaNValidation:
    """Missing values must raise, never launder into scores. See ADR-0004."""

    def test_unmatched_measure_id_raises(self):
        # Left merge leaves NaN measure_weight for XYZ; previously wm_score
        # scored it 1.0 and the aggregate silently described inconsistent
        # row sets (weighted skips NaN, count/mean/max include the row).
        ecds = pd.DataFrame(
            {
                "measure_id": ["COL", "XYZ"],
                "completeness_rate": [0.95, 0.85],
                "mapping_coverage": [0.93, 0.88],
                "variance_ratio": [1.03, 1.10],
                "cutpoint_shift": [0.02, 0.05],
            }
        )
        weights = pd.DataFrame({"measure_id": ["COL"], "measure_weight": [1]})
        merged = ecds.merge(weights, on="measure_id", how="left")
        calc = ShockIndexCalculator()
        with pytest.raises(ValueError, match="XYZ"):
            calc.score_dataframe(merged)

    def test_aggregate_contract_rejects_nan_weight(self):
        df = pd.DataFrame(
            {"shock_index": [0.5, 0.6], "measure_weight": [1.0, float("nan")]}
        )
        calc = ShockIndexCalculator()
        with pytest.raises(ValueError, match="NaN"):
            calc.aggregate_contract(df)

    def test_aggregate_contract_rejects_nan_shock_index(self):
        df = pd.DataFrame(
            {"shock_index": [0.5, float("nan")], "measure_weight": [1.0, 2.0]}
        )
        calc = ShockIndexCalculator()
        with pytest.raises(ValueError, match="NaN"):
            calc.aggregate_contract(df)
