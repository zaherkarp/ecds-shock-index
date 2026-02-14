"""Command line interface for quick ECDS Shock Index calculations."""

from __future__ import annotations

import argparse

from ecds_shock_index import ShockIndexCalculator


def build_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI execution."""
    parser = argparse.ArgumentParser(description="Compute ECDS Shock Index from normalized factors.")
    parser.add_argument("--ccs", type=float, required=True, help="Clinical completeness score [0, 1]")
    parser.add_argument("--eav", type=float, required=True, help="ECDS adoption variability score [0, 1]")
    parser.add_argument("--cpr", type=float, required=True, help="Cutpoint pressure risk score [0, 1]")
    parser.add_argument("--wm", type=float, required=True, help="Weight multiplier score [0, 1]")
    return parser


def main() -> None:
    """Run the CLI entrypoint."""
    args = build_parser().parse_args()
    calculator = ShockIndexCalculator()
    score = calculator.calculate(ccs=args.ccs, eav=args.eav, cpr=args.cpr, wm=args.wm)
    print(f"ECDS Shock Index: {score:.4f}")


if __name__ == "__main__":
    main()
