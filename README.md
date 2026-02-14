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
│   ├── cli.py                # Optional command-line interface
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
pip install -e .
```

### Option 2: conda

```bash
conda env create -f environment.yml
conda activate ecds-shock-index
pip install -e .
```

## Quick Start

```python
from ecds_shock_index import ShockIndexCalculator, ccs_score, eav_score, cpr_score, wm_score

ccs = ccs_score(completeness_rate=0.82, mapping_coverage=0.90)
eav = eav_score(variance_ratio=1.15)
cpr = cpr_score(cutpoint_shift=0.22)
wm = wm_score(measure_weight=3, max_weight=5)

calculator = ShockIndexCalculator()
index = calculator.calculate(ccs=ccs, eav=eav, cpr=cpr, wm=wm)
print(index)
```

## Command Line Example

```bash
python -m src.cli --ccs 0.86 --eav 0.74 --cpr 0.58 --wm 0.60
```

## Development

Run tests locally:

```bash
pytest
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Code of Conduct

Please review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation guidelines.
