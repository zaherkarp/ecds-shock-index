#!/usr/bin/env python3
"""Weight-sensitivity analysis for the ECDS Shock Index.

Runs OAT perturbation and uniform-Dirichlet(1,1,1) sampling on the
3-hazard-weight simplex per ADR-0007. Uses stdlib random (seed 7,
N=200000) for reproducibility without added dependencies.

Usage:
    python scripts/weight_sensitivity_analysis.py \
        --ecds data/raw/example_ncqa_ecds.csv \
        --weights data/raw/example_cms_measure_weights.csv
"""

from __future__ import annotations

import argparse
import math
import random

import pandas as pd

from ecds_shock_index import ShockIndexCalculator, classify_risk
from ecds_shock_index.data_loader import load_cms_measure_weights, load_ncqa_ecds, merge_ecds_and_weights
from ecds_shock_index.sensitivity import weight_sensitivity


def dirichlet_sample_3(rng: random.Random, n: int) -> list[tuple[float, float, float]]:
    """Draw n samples from Dirichlet(1,1,1) on the 3-simplex via exponentials."""
    samples = []
    for _ in range(n):
        e1 = -math.log(1.0 - rng.random())
        e2 = -math.log(1.0 - rng.random())
        e3 = -math.log(1.0 - rng.random())
        total = e1 + e2 + e3
        samples.append((e1 / total, e2 / total, e3 / total))
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description="Weight-sensitivity analysis")
    parser.add_argument("--ecds", required=True, help="Path to NCQA ECDS CSV")
    parser.add_argument("--weights", required=True, help="Path to CMS weights CSV")
    parser.add_argument("--seed", type=int, default=7, help="RNG seed (default: 7)")
    parser.add_argument("--n-dirichlet", type=int, default=200000, help="Dirichlet samples (default: 200000)")
    args = parser.parse_args()

    ecds_df = load_ncqa_ecds(args.ecds)
    weights_df = load_cms_measure_weights(args.weights)
    merged = merge_ecds_and_weights(ecds_df, weights_df)

    calc = ShockIndexCalculator()
    scored = calc.score_dataframe(merged)

    print("=" * 72)
    print("OAT SENSITIVITY (deltas = 0.05, 0.10, 0.20)")
    print("=" * 72)
    oat_df = weight_sensitivity(scored, calc)
    flips = oat_df[oat_df["tier_flip"]]
    print(f"\nTotal perturbations: {len(oat_df)}")
    print(f"Tier flips: {len(flips)}")
    if len(flips):
        print("\nFlip details:")
        print(flips[["weight_name", "signed_delta", "l1_radius", "measure_id",
                      "shock_index_before", "shock_index_after",
                      "tier_before", "tier_after"]].to_string(index=False))

    print(f"\n{'=' * 72}")
    print(f"DIRICHLET(1,1,1) MONTE CARLO (N={args.n_dirichlet}, seed={args.seed})")
    print("=" * 72)

    rng = random.Random(args.seed)
    samples = dirichlet_sample_3(rng, args.n_dirichlet)

    measure_ids = scored["measure_id"].tolist()
    ccs_vals = scored["ccs"].tolist()
    eav_vals = scored["eav"].tolist()
    cpr_vals = scored["cpr"].tolist()
    si_base = scored["shock_index"].tolist()
    tier_base = [classify_risk(s) for s in si_base]

    flip_counts = {mid: 0 for mid in measure_ids}
    for alpha, beta, gamma in samples:
        for i, mid in enumerate(measure_ids):
            si = alpha * ccs_vals[i] + beta * eav_vals[i] + gamma * cpr_vals[i]
            si = max(0.0, min(1.0, si))
            if classify_risk(si) != tier_base[i]:
                flip_counts[mid] += 1

    print("\nTier-flip frequency per measure:")
    for mid in measure_ids:
        freq = flip_counts[mid] / args.n_dirichlet
        print(f"  {mid}: {flip_counts[mid]:>6d} / {args.n_dirichlet} = {freq:.4%}")

    l1_radius_0_10 = 0.10
    in_ball = 0
    in_ball_flips = {mid: 0 for mid in measure_ids}
    base_alpha, base_beta, base_gamma = 0.4375, 0.3125, 0.25
    for alpha, beta, gamma in samples:
        l1 = abs(alpha - base_alpha) + abs(beta - base_beta) + abs(gamma - base_gamma)
        if l1 <= l1_radius_0_10:
            in_ball += 1
            for i, mid in enumerate(measure_ids):
                si = alpha * ccs_vals[i] + beta * eav_vals[i] + gamma * cpr_vals[i]
                si = max(0.0, min(1.0, si))
                if classify_risk(si) != tier_base[i]:
                    in_ball_flips[mid] += 1

    print(f"\nIn L1 ball (radius {l1_radius_0_10}): {in_ball} / {args.n_dirichlet}")
    if in_ball:
        print("  Flips within ball:")
        for mid in measure_ids:
            print(f"    {mid}: {in_ball_flips[mid]}")


if __name__ == "__main__":
    main()
