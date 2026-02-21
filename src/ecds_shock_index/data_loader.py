"""Utilities to load and join example NCQA ECDS and CMS Stars definitions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ECDS_REQUIRED_COLUMNS = {
    "measure_id",
    "completeness_rate",
    "mapping_coverage",
    "variance_ratio",
    "cutpoint_shift",
}

CMS_REQUIRED_COLUMNS = {
    "measure_id",
    "measure_weight",
}


def _validate_columns(df: pd.DataFrame, required: set[str], source: str) -> None:
    """Raise ``ValueError`` if *df* is missing any *required* columns."""
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


def load_ncqa_ecds(path: str | Path) -> pd.DataFrame:
    """Load NCQA ECDS results CSV.

    Expected columns:
        measure_id, completeness_rate, mapping_coverage,
        variance_ratio, cutpoint_shift
    """
    df = pd.read_csv(path)
    _validate_columns(df, ECDS_REQUIRED_COLUMNS, "NCQA ECDS file")
    return df


def load_cms_measure_weights(path: str | Path) -> pd.DataFrame:
    """Load CMS Stars measure definitions/weights CSV.

    Expected columns:
        measure_id, measure_weight
    """
    df = pd.read_csv(path)
    _validate_columns(df, CMS_REQUIRED_COLUMNS, "CMS measure weights file")
    return df


def merge_ecds_and_weights(
    ecds_df: pd.DataFrame,
    weights_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge ECDS results with Stars measure weights on measure_id."""
    return ecds_df.merge(weights_df, on="measure_id", how="left")


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[2]
    ecds_path = base / "data" / "raw" / "example_ncqa_ecds.csv"
    cms_path = base / "data" / "raw" / "example_cms_measure_weights.csv"

    ecds = load_ncqa_ecds(ecds_path)
    cms = load_cms_measure_weights(cms_path)
    merged = merge_ecds_and_weights(ecds, cms)

    print("Loaded NCQA rows:", len(ecds))
    print("Loaded CMS rows:", len(cms))
    print("Merged rows:", len(merged))
    print(merged.head())
