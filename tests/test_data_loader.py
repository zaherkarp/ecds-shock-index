"""Tests for data loading and validation utilities."""

import pytest

import pandas as pd

from ecds_shock_index.data_loader import (
    load_cms_measure_weights,
    load_ncqa_ecds,
    merge_ecds_and_weights,
)

DATA_DIR = "data/raw"


class TestLoadNcqaEcds:
    def test_loads_example_file(self):
        df = load_ncqa_ecds(f"{DATA_DIR}/example_ncqa_ecds.csv")
        assert len(df) == 3
        assert "measure_id" in df.columns

    def test_rejects_bad_columns(self, tmp_path):
        bad = tmp_path / "bad.csv"
        bad.write_text("a,b\n1,2\n")
        with pytest.raises(ValueError, match="missing required columns"):
            load_ncqa_ecds(bad)


class TestLoadCmsMeasureWeights:
    def test_loads_example_file(self):
        df = load_cms_measure_weights(f"{DATA_DIR}/example_cms_measure_weights.csv")
        assert len(df) == 3
        assert "measure_weight" in df.columns

    def test_rejects_bad_columns(self, tmp_path):
        bad = tmp_path / "bad.csv"
        bad.write_text("x,y\n1,2\n")
        with pytest.raises(ValueError, match="missing required columns"):
            load_cms_measure_weights(bad)


class TestMergeEcdsAndWeights:
    def test_merge_on_measure_id(self):
        ecds = pd.DataFrame({"measure_id": ["A", "B"], "val": [1, 2]})
        weights = pd.DataFrame({"measure_id": ["A", "B"], "measure_weight": [3, 5]})
        merged = merge_ecds_and_weights(ecds, weights)
        assert "measure_weight" in merged.columns
        assert len(merged) == 2

    def test_left_join_preserves_unmatched(self):
        ecds = pd.DataFrame({"measure_id": ["A", "B", "C"], "val": [1, 2, 3]})
        weights = pd.DataFrame({"measure_id": ["A"], "measure_weight": [3]})
        merged = merge_ecds_and_weights(ecds, weights)
        assert len(merged) == 3
        assert pd.isna(merged.loc[merged["measure_id"] == "C", "measure_weight"].iloc[0])
