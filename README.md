# ECDS Shock Index

The **ECDS Shock Index** repository provides a reproducible analytics framework for modeling how shifts in Electronic Clinical Data Systems (ECDS) measure performance can impact Medicare Advantage Star Ratings.

## Project Motivation

As organizations transition quality measurement pipelines toward ECDS and digital quality methods, historical assumptions about measure distributions can break. The ECDS Shock Index is designed to:

- quantify distribution volatility risk across Stars measures,
- compare operational readiness and data completeness,
- support scenario simulation for future cutpoint movement.

## Repository Structure

```text
.
├── blog/                     # Long-form analysis and methodology posts
├── data/
│   ├── raw/                  # Source extracts and lookup tables
│   └── processed/            # Cleaned and analysis-ready tables
├── notebooks/                # Exploratory notebooks and simulations
├── src/
│   ├── cli.py                # Command-line interface (single & batch)
│   └── ecds_shock_index/     # Core package
├── tests/                    # Unit tests
├── requirements.txt
└── pyproject.toml
```

## Installation

### Option 1: pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Option 2: conda

```bash
conda env create -f environment.yml
conda activate ecds-shock-index
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from ecds_shock_index import ShockIndexCalculator, ccs_score, eav_score, cpr_score, wm_score, classify_risk

# 1. Compute individual factor scores from raw inputs
ccs = ccs_score(completeness_rate=0.82, mapping_coverage=0.90)   # -> 0.86
eav = eav_score(variance_ratio=1.15)                              # -> 0.575
cpr = cpr_score(cutpoint_shift=0.22)                              # -> 0.44
wm  = wm_score(measure_weight=3, max_weight=5)                    # -> 0.60

# 2. Calculate the composite shock index
calculator = ShockIndexCalculator()   # uses default weights
index = calculator.calculate(ccs=ccs, eav=eav, cpr=cpr, wm=wm)
print(f"Shock Index: {index:.4f}")    # 0.6325

# 3. Classify into a risk tier
print(classify_risk(index))           # "high"
```

### Batch Scoring (DataFrame)

Score an entire set of measures at once, then aggregate to a contract-level summary:

```python
import pandas as pd
from ecds_shock_index import ShockIndexCalculator
from ecds_shock_index.data_loader import load_ncqa_ecds, load_cms_measure_weights, merge_ecds_and_weights

# Load and merge data
ecds = load_ncqa_ecds("data/raw/example_ncqa_ecds.csv")
weights = load_cms_measure_weights("data/raw/example_cms_measure_weights.csv")
merged = merge_ecds_and_weights(ecds, weights)

# Score every measure
calc = ShockIndexCalculator()
scored = calc.score_dataframe(merged)
print(scored[["measure_id", "shock_index", "risk_tier"]])

# Contract-level summary
summary = calc.aggregate_contract(scored)
print(summary)
# {'weighted_shock_index': 0.4261, 'mean_shock_index': 0.4389,
#  'max_shock_index': 0.4952, 'measure_count': 3, 'risk_tier': 'moderate'}
```

## Command Line Interface

The CLI supports two modes: **single** (pre-computed scores) and **batch** (CSV files).

### Single Mode

Compute the index from four pre-computed factor scores:

```bash
# Basic usage
python -m src.cli single --ccs 0.86 --eav 0.74 --cpr 0.58 --wm 0.60
# Output: ECDS Shock Index: 0.7220  (high risk)

# JSON output
python -m src.cli single --ccs 0.86 --eav 0.74 --cpr 0.58 --wm 0.60 --json
# Output: {"shock_index": 0.722, "risk_tier": "high"}

# Legacy flat-argument style (backwards compatible)
python -m src.cli --ccs 0.86 --eav 0.74 --cpr 0.58 --wm 0.60
```

### Batch Mode

Score all measures from CSV files and get a contract-level summary:

```bash
# Print scored table and contract summary to stdout
python -m src.cli batch \
  --ecds data/raw/example_ncqa_ecds.csv \
  --weights data/raw/example_cms_measure_weights.csv

# Write scored CSV to a file
python -m src.cli batch \
  --ecds data/raw/example_ncqa_ecds.csv \
  --weights data/raw/example_cms_measure_weights.csv \
  --output data/processed/scored.csv

# JSON contract summary
python -m src.cli batch \
  --ecds data/raw/example_ncqa_ecds.csv \
  --weights data/raw/example_cms_measure_weights.csv \
  --json

# Custom normalization parameters
python -m src.cli batch \
  --ecds data/raw/example_ncqa_ecds.csv \
  --weights data/raw/example_cms_measure_weights.csv \
  --max-shift 1.0 \
  --max-weight 3.0
```

## Risk Tiers

Shock index scores are classified into four tiers:

| Tier       | Range          | Interpretation                                        |
| ---------- | -------------- | ----------------------------------------------------- |
| Low        | [0.00, 0.25)   | Minimal distribution risk; ECDS transition on track   |
| Moderate   | [0.25, 0.50)   | Some volatility; monitor cutpoint movement            |
| High       | [0.50, 0.75)   | Significant risk; prioritize remediation              |
| Critical   | [0.75, 1.00]   | Severe exposure; immediate action recommended         |

## Component Reference

| Component | Full Name                      | What It Measures                                     | Default Weight |
| --------- | ------------------------------ | ---------------------------------------------------- | -------------- |
| CCS       | Clinical Completeness Score    | Average of data completeness and mapping coverage    | 0.35           |
| EAV       | ECDS Adoption Variability      | Distribution volatility relative to baseline         | 0.25           |
| CPR       | Cutpoint Pressure Risk         | Expected cutpoint movement pressure                  | 0.20           |
| WM        | Weight Multiplier              | Stars measure weight amplification effect            | 0.20           |

## Data File Formats

### NCQA ECDS CSV (`--ecds`)

| Column             | Type  | Description                                  |
| ------------------ | ----- | -------------------------------------------- |
| `measure_id`       | str   | Unique measure identifier (e.g., COL, BCS)   |
| `completeness_rate`| float | Data completeness rate [0, 1]                |
| `mapping_coverage` | float | Coding/mapping coverage rate [0, 1]          |
| `variance_ratio`   | float | Variance ratio vs. baseline (1.0 = no change)|
| `cutpoint_shift`   | float | Absolute cutpoint shift magnitude            |

### CMS Measure Weights CSV (`--weights`)

| Column           | Type  | Description                            |
| ---------------- | ----- | -------------------------------------- |
| `measure_id`     | str   | Unique measure identifier              |
| `measure_name`   | str   | Human-readable measure name (optional) |
| `measure_weight` | int   | CMS Stars measure weight (1–5)         |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with verbose output
pytest -v
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Code of Conduct

Please review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation guidelines.
