"""Tests for batch scoring and contract-level aggregation."""

import pytest

import pandas as pd

from ecds_shock_index import ShockIndexCalculator, classify_risk


@pytest.fixture()
def sample_df():
    return pd.DataFrame(
        {
            "measure_id": ["COL", "BCS", "A1C"],
            "completeness_rate": [0.88, 0.79, 0.83],
            "mapping_coverage": [0.91, 0.85, 0.89],
            "variance_ratio": [1.12, 1.30, 1.05],
            "cutpoint_shift": [0.08, 0.16, 0.05],
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
