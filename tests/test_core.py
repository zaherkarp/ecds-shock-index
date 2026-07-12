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
    """CCS is a completeness *gap*: higher = less complete = more risk."""

    def test_gap_from_average(self):
        assert ccs_score(0.8, 0.9) == pytest.approx(0.15)

    def test_perfect_capture_is_zero_risk(self):
        assert ccs_score(1.0, 1.0) == pytest.approx(0.0)

    def test_no_capture_is_max_risk(self):
        assert ccs_score(0.0, 0.0) == pytest.approx(1.0)

    def test_clips_above_one(self):
        # Negative inputs would push the gap above 1.0; clamp at 1.0.
        assert ccs_score(-0.5, 0.0) == pytest.approx(1.0)

    def test_clips_below_zero(self):
        # Over-complete inputs would push the gap below 0.0; clamp at 0.0.
        assert ccs_score(1.2, 1.0) == pytest.approx(0.0)


class TestEavScore:
    """EAV is symmetric on the log scale: eav(r) == eav(1/r). See ADR-0003."""

    def test_baseline_is_zero_risk(self):
        assert eav_score(1.0, baseline=1.0) == pytest.approx(0.0)

    def test_above_baseline(self):
        # |ln 1.5| / ln 2 = 0.4054651081 / 0.6931471806 (ADR-0003 table)
        assert eav_score(1.5, baseline=1.0) == pytest.approx(0.5849625007)

    def test_reciprocal_symmetry_interior(self):
        # Load-bearing symmetry oracle: |ln 0.8| = ln 1.25 = 0.2231435513
        assert eav_score(0.8) == pytest.approx(0.3219280949)
        assert eav_score(1.25) == pytest.approx(0.3219280949)

    def test_reciprocal_symmetry_sweep(self):
        for ratio in (0.6, 0.75, 0.9, 1.1, 1.3, 1.45):
            assert eav_score(ratio) == pytest.approx(eav_score(1.0 / ratio))

    def test_saturates_at_doubling_and_halving(self):
        assert eav_score(2.0, baseline=1.0) == pytest.approx(1.0)
        assert eav_score(0.5, baseline=1.0) == pytest.approx(1.0)

    def test_clips_high_ratio(self):
        assert eav_score(3.0, baseline=1.0) == pytest.approx(1.0)

    def test_sensitivity_scales_deviation(self):
        # Saturation anchor moves to 2**sensitivity: |ln 1.5| / (2 ln 2)
        assert eav_score(1.5, baseline=1.0, sensitivity=2.0) == pytest.approx(0.2924812504)

    def test_nonpositive_ratio_is_max_risk(self):
        # A variance ratio <= 0 is degenerate and scores 1.0 explicitly.
        assert eav_score(0.0) == pytest.approx(1.0)
        assert eav_score(-1.0) == pytest.approx(1.0)

    def test_invalid_baseline(self):
        with pytest.raises(ValueError, match="baseline"):
            eav_score(1.0, baseline=0)
        with pytest.raises(ValueError, match="baseline"):
            eav_score(1.0, baseline=-1)

    def test_invalid_sensitivity(self):
        with pytest.raises(ValueError, match="sensitivity"):
            eav_score(1.0, sensitivity=0)


class TestCprScore:
    def test_within_guardrail_scales_realized(self):
        # Half the guardrail consumed, no latent term -> 0.8 * 0.5.
        assert cpr_score(0.025, guardrail=0.05) == pytest.approx(0.4)

    def test_at_guardrail_is_full_realized(self):
        assert cpr_score(0.05, guardrail=0.05) == pytest.approx(0.8)

    def test_beyond_guardrail_adds_latent(self):
        # realized=1.0, latent=(0.55-0.05)/0.5=1.0 -> 0.8 + 0.2.
        assert cpr_score(0.55, guardrail=0.05, max_shift=0.5) == pytest.approx(1.0)

    def test_negative_shift_uses_absolute(self):
        assert cpr_score(-0.025, guardrail=0.05) == pytest.approx(0.4)

    def test_zero_shift(self):
        assert cpr_score(0.0) == pytest.approx(0.0)

    def test_invalid_guardrail(self):
        with pytest.raises(ValueError, match="guardrail"):
            cpr_score(0.2, guardrail=0)

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


class TestNonFiniteInputs:
    """No non-finite input may map into [0, 1]. See ADR-0004.

    Previously NaN silently scored 1.0 (maximum risk) via ``min(1.0, nan)``
    argument ordering, and infinities scored sign-dependent extremes.
    """

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_ccs_rejects_nonfinite(self, bad):
        with pytest.raises(ValueError, match="finite"):
            ccs_score(bad, 0.9)
        with pytest.raises(ValueError, match="finite"):
            ccs_score(0.9, bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_eav_rejects_nonfinite(self, bad):
        with pytest.raises(ValueError, match="finite"):
            eav_score(bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_cpr_rejects_nonfinite(self, bad):
        with pytest.raises(ValueError, match="finite"):
            cpr_score(bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_wm_rejects_nonfinite(self, bad):
        with pytest.raises(ValueError, match="finite"):
            wm_score(bad)

    def test_ccs_positive_inf_scored_minimum_before(self):
        # 1 - (inf + 0.9)/2 = -inf clipped to 0.0 (silent minimum risk lane)
        with pytest.raises(ValueError, match="finite"):
            ccs_score(float("inf"), 0.9)

    def test_wm_negative_inf_scored_minimum_before(self):
        # -inf / 5 clipped to 0.0 (silent minimum risk lane)
        with pytest.raises(ValueError, match="finite"):
            wm_score(float("-inf"))

    def test_ccs_inf_minus_inf_regenerates_nan(self):
        # inf + (-inf) = nan internally; defeats a NaN-only boundary check
        with pytest.raises(ValueError, match="finite"):
            ccs_score(float("inf"), float("-inf"))


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
    def test_default_weights_exact(self):
        # Hazard-only defaults: neutral renormalization of (0.35, 0.25, 0.20)
        # by 1/(1 - 0.20); WM exposure enters only at contract aggregation.
        # See ADR-0002.
        calc = ShockIndexCalculator()
        assert calc.alpha_ccs == 0.4375
        assert calc.beta_eav == 0.3125
        assert calc.gamma_cpr == 0.25
        assert calc.delta_wm == 0.0

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
