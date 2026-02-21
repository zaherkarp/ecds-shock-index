"""Unit tests for ECDS Shock Index core scoring logic."""

import pytest

from ecds_shock_index import (
    ShockIndexCalculator,
    classify_risk,
    ccs_score,
    cpr_score,
    eav_score,
    wm_score,
)


# ---------------------------------------------------------------------------
# Factor-level scoring
# ---------------------------------------------------------------------------


class TestCcsScore:
    def test_average(self):
        assert ccs_score(0.8, 0.9) == pytest.approx(0.85)

    def test_perfect(self):
        assert ccs_score(1.0, 1.0) == pytest.approx(1.0)

    def test_zero(self):
        assert ccs_score(0.0, 0.0) == pytest.approx(0.0)

    def test_clips_above_one(self):
        assert ccs_score(1.2, 1.0) == pytest.approx(1.0)

    def test_clips_below_zero(self):
        assert ccs_score(-0.5, 0.0) == pytest.approx(0.0)


class TestEavScore:
    def test_baseline_is_midpoint(self):
        assert eav_score(1.0, baseline=1.0) == pytest.approx(0.5)

    def test_above_baseline(self):
        assert eav_score(1.5, baseline=1.0) == pytest.approx(0.75)

    def test_below_baseline(self):
        assert eav_score(0.5, baseline=1.0) == pytest.approx(0.25)

    def test_clips_high_ratio(self):
        assert eav_score(3.0, baseline=1.0) == pytest.approx(1.0)

    def test_invalid_baseline(self):
        with pytest.raises(ValueError, match="baseline"):
            eav_score(1.0, baseline=0)
        with pytest.raises(ValueError, match="baseline"):
            eav_score(1.0, baseline=-1)


class TestCprScore:
    def test_normalization(self):
        assert cpr_score(0.25, max_shift=0.5) == pytest.approx(0.5)

    def test_clips_to_one(self):
        assert cpr_score(0.8, max_shift=0.5) == pytest.approx(1.0)

    def test_negative_shift_uses_absolute(self):
        assert cpr_score(-0.25, max_shift=0.5) == pytest.approx(0.5)

    def test_zero_shift(self):
        assert cpr_score(0.0) == pytest.approx(0.0)

    def test_invalid_max_shift(self):
        with pytest.raises(ValueError, match="max_shift"):
            cpr_score(0.2, max_shift=0)


class TestWmScore:
    def test_normalization(self):
        assert wm_score(3, max_weight=5) == pytest.approx(0.6)

    def test_max_weight(self):
        assert wm_score(5, max_weight=5) == pytest.approx(1.0)

    def test_zero_weight(self):
        assert wm_score(0, max_weight=5) == pytest.approx(0.0)

    def test_invalid_max_weight(self):
        with pytest.raises(ValueError, match="max_weight"):
            wm_score(1, max_weight=0)


# ---------------------------------------------------------------------------
# Risk classification
# ---------------------------------------------------------------------------


class TestClassifyRisk:
    def test_low(self):
        assert classify_risk(0.0) == "low"
        assert classify_risk(0.24) == "low"

    def test_moderate(self):
        assert classify_risk(0.25) == "moderate"
        assert classify_risk(0.49) == "moderate"

    def test_high(self):
        assert classify_risk(0.50) == "high"
        assert classify_risk(0.74) == "high"

    def test_critical(self):
        assert classify_risk(0.75) == "critical"
        assert classify_risk(1.0) == "critical"

    def test_clips_out_of_range(self):
        assert classify_risk(-0.5) == "low"
        assert classify_risk(1.5) == "critical"


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------


class TestShockIndexCalculator:
    def test_default_weights_sum_to_one(self):
        calc = ShockIndexCalculator()
        total = calc.alpha_ccs + calc.beta_eav + calc.gamma_cpr + calc.delta_wm
        assert total == pytest.approx(1.0)

    def test_calculate_weighted_index(self):
        calc = ShockIndexCalculator(alpha_ccs=0.4, beta_eav=0.2, gamma_cpr=0.2, delta_wm=0.2)
        score = calc.calculate(ccs=0.8, eav=0.5, cpr=0.5, wm=0.5)
        assert score == pytest.approx(0.62)

    def test_all_zeros(self):
        calc = ShockIndexCalculator()
        assert calc.calculate(0, 0, 0, 0) == pytest.approx(0.0)

    def test_all_ones(self):
        calc = ShockIndexCalculator()
        assert calc.calculate(1, 1, 1, 1) == pytest.approx(1.0)

    def test_invalid_weights_not_summing_to_one(self):
        with pytest.raises(ValueError, match="sum to 1.0"):
            ShockIndexCalculator(alpha_ccs=0.5, beta_eav=0.5, gamma_cpr=0.5, delta_wm=0.5)

    def test_negative_weight_rejected(self):
        with pytest.raises(ValueError, match="non-negative"):
            ShockIndexCalculator(alpha_ccs=-0.1, beta_eav=0.5, gamma_cpr=0.3, delta_wm=0.3)

    def test_invalid_parameters_raise_errors(self):
        with pytest.raises(ValueError):
            eav_score(variance_ratio=1.1, baseline=0)
        with pytest.raises(ValueError):
            cpr_score(cutpoint_shift=0.2, max_shift=0)
        with pytest.raises(ValueError):
            wm_score(measure_weight=1, max_weight=0)
