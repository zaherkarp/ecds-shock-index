"""Command line interface for ECDS Shock Index calculations.

Supports two modes:
    Single   – supply pre-computed factor scores directly
    Batch    – supply a merged CSV file to score all measures at once
"""

from __future__ import annotations

import argparse
import json
import sys

from ecds_shock_index import ShockIndexCalculator, classify_risk
from ecds_shock_index.data_loader import load_cms_measure_weights, load_ncqa_ecds, merge_ecds_and_weights


def build_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI execution."""
    parser = argparse.ArgumentParser(
        prog="ecds-shock-index",
        description="Compute ECDS Shock Index from normalized factors or a CSV file.",
    )
    sub = parser.add_subparsers(dest="command")

    # -- single mode (default when no subcommand) --
    single = sub.add_parser("single", help="Compute index from four pre-computed factor scores.")
    single.add_argument("--ccs", type=float, required=True, help="Clinical completeness score [0, 1]")
    single.add_argument("--eav", type=float, required=True, help="ECDS adoption variability score [0, 1]")
    single.add_argument("--cpr", type=float, required=True, help="Cutpoint pressure risk score [0, 1]")
    single.add_argument("--wm", type=float, required=True, help="Weight multiplier score [0, 1]")
    single.add_argument("--json", action="store_true", dest="as_json", help="Output result as JSON")

    # -- batch mode --
    batch = sub.add_parser("batch", help="Score all measures from CSV files.")
    batch.add_argument("--ecds", required=True, help="Path to NCQA ECDS results CSV")
    batch.add_argument("--weights", required=True, help="Path to CMS measure weights CSV")
    batch.add_argument("--max-shift", type=float, default=0.5, help="Max cutpoint shift for CPR normalization (default: 0.5)")
    batch.add_argument("--max-weight", type=float, default=5.0, help="Max measure weight for WM normalization (default: 5.0)")
    batch.add_argument("--output", "-o", help="Write scored CSV to this path (default: print to stdout)")
    batch.add_argument("--json", action="store_true", dest="as_json", help="Output contract-level summary as JSON")

    # -- legacy: support the old flat --ccs/--eav/--cpr/--wm style --
    parser.add_argument("--ccs", type=float, help=argparse.SUPPRESS)
    parser.add_argument("--eav", type=float, help=argparse.SUPPRESS)
    parser.add_argument("--cpr", type=float, help=argparse.SUPPRESS)
    parser.add_argument("--wm", type=float, help=argparse.SUPPRESS)

    return parser


def _run_single(ccs: float, eav: float, cpr: float, wm: float, as_json: bool = False) -> None:
    calc = ShockIndexCalculator()
    score = calc.calculate(ccs=ccs, eav=eav, cpr=cpr, wm=wm)
    tier = classify_risk(score)
    if as_json:
        print(json.dumps({"shock_index": round(score, 4), "risk_tier": tier}))
    else:
        print(f"ECDS Shock Index: {score:.4f}  ({tier} risk)")


def _run_batch(args: argparse.Namespace) -> None:
    ecds_df = load_ncqa_ecds(args.ecds)
    weights_df = load_cms_measure_weights(args.weights)
    merged = merge_ecds_and_weights(ecds_df, weights_df)

    calc = ShockIndexCalculator()
    scored = calc.score_dataframe(merged, max_shift=args.max_shift, max_weight=args.max_weight)
    summary = calc.aggregate_contract(scored)

    if args.output:
        scored.to_csv(args.output, index=False)
        print(f"Scored CSV written to {args.output}")
    else:
        print(scored.to_string(index=False))

    print()
    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        print("Contract Summary")
        print(f"  Weighted Shock Index: {summary['weighted_shock_index']:.4f}")
        print(f"  Mean Shock Index:     {summary['mean_shock_index']:.4f}")
        print(f"  Max Shock Index:      {summary['max_shock_index']:.4f}")
        print(f"  Measure Count:        {summary['measure_count']}")
        print(f"  Risk Tier:            {summary['risk_tier']}")


def main() -> None:
    """Run the CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "batch":
        _run_batch(args)
    elif args.command == "single":
        _run_single(args.ccs, args.eav, args.cpr, args.wm, getattr(args, "as_json", False))
    elif args.ccs is not None and args.eav is not None and args.cpr is not None and args.wm is not None:
        # Legacy flat-argument mode
        _run_single(args.ccs, args.eav, args.cpr, args.wm)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
