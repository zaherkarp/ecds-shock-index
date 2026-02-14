"""Unit tests for ECDS Shock Index core scoring logic."""

import pytest

from ecds_shock_index import ShockIndexCalculator, ccs_score, cpr_score, eav_score, wm_score


def test_ccs_score_average():
    """CCS should average completeness and mapping coverage."""
    assert ccs_score(0.8, 0.9) == pytest.approx(0.85)


def test_eav_score_baseline_is_midpoint():
    """EAV at baseline should map to 0.5 risk."""
    assert eav_score(1.0, baseline=1.0) == pytest.approx(0.5)


def test_cpr_score_normalization():
    """CPR should scale by max shift and clip to one."""
    assert cpr_score(0.25, max_shift=0.5) == pytest.approx(0.5)
    assert cpr_score(0.8, max_shift=0.5) == pytest.approx(1.0)


def test_wm_score_normalization():
    """WM should normalize measure weight by maximum."""
    assert wm_score(3, max_weight=5) == pytest.approx(0.6)


def test_calculate_weighted_index():
    """Calculator should return weighted score from factors."""
    calc = ShockIndexCalculator(alpha_ccs=0.4, beta_eav=0.2, gamma_cpr=0.2, delta_wm=0.2)
    score = calc.calculate(ccs=0.8, eav=0.5, cpr=0.5, wm=0.5)
    assert score == pytest.approx(0.62)


def test_invalid_parameters_raise_errors():
    """Invalid normalization parameters should raise ValueError."""
    with pytest.raises(ValueError):
        eav_score(variance_ratio=1.1, baseline=0)

    with pytest.raises(ValueError):
        cpr_score(cutpoint_shift=0.2, max_shift=0)

    with pytest.raises(ValueError):
        wm_score(measure_weight=1, max_weight=0)
