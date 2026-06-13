import math

import numpy as np
import pytest

from monitor_cert import (
    certified_threshold,
    compare_thresholds,
    cp_upper,
    empirical_threshold,
    false_positive_rate,
    safety_at_threshold,
)


def test_cp_upper_handles_all_successes() -> None:
    assert cp_upper(10, 10, 0.1) == 1.0


def test_cp_upper_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="n must be positive"):
        cp_upper(0, 0, 0.1)
    with pytest.raises(ValueError, match="k must satisfy"):
        cp_upper(2, 1, 0.1)
    with pytest.raises(ValueError, match="delta"):
        cp_upper(0, 10, 1.0)


def test_certified_threshold_is_conservative_with_small_calibration_set() -> None:
    honest = np.arange(100, dtype=float)

    threshold = certified_threshold(honest, alpha=0.01, delta=0.1)

    assert math.isinf(threshold)


def test_certified_threshold_finds_lowest_valid_observed_threshold() -> None:
    honest = np.arange(10_000, dtype=float)

    threshold = certified_threshold(honest, alpha=0.01, delta=0.1)
    flagged = int(np.sum(honest >= threshold))

    assert cp_upper(flagged, len(honest), 0.1) <= 0.01
    assert threshold > 9_900
    candidates = np.sort(np.unique(honest))
    previous_threshold = candidates[np.searchsorted(candidates, threshold) - 1]
    previous_flagged = int(np.sum(honest >= previous_threshold))
    assert cp_upper(previous_flagged, len(honest), 0.1) > 0.01


def test_fixed_sequence_equals_ascending_crossover_on_monotone_scores() -> None:
    honest = np.arange(10_000, dtype=float)

    ascending = float(np.inf)
    for threshold in np.sort(np.unique(honest)):
        flagged = int(np.sum(honest >= threshold))
        if cp_upper(flagged, len(honest), 0.1) <= 0.01:
            ascending = float(threshold)
            break

    assert certified_threshold(honest, alpha=0.01, delta=0.1) == ascending


def test_empirical_threshold_uses_score_greater_than_or_equal_rule() -> None:
    honest = np.array([0, 1, 2, 3, 4], dtype=float)

    threshold = empirical_threshold(honest, alpha=0.4)

    assert threshold == 3
    assert false_positive_rate(honest, threshold) == 0.4


def test_ties_are_handled_conservatively() -> None:
    honest = np.array([0, 0, 10, 10, 10], dtype=float)

    threshold = empirical_threshold(honest, alpha=0.5)

    assert math.isinf(threshold)


def test_safety_at_threshold_is_attack_catch_rate() -> None:
    attack_scores = np.array([0.2, 0.8, 1.0, 1.2], dtype=float)

    assert safety_at_threshold(attack_scores, 1.0) == 0.5


def test_safety_at_threshold_restricts_denominator_to_successes() -> None:
    attack_scores = np.array([0.2, 0.8, 1.0, 1.2], dtype=float)
    succeeded = np.array([True, False, True, False])

    assert safety_at_threshold(attack_scores, 1.0, succeeded=succeeded) == 0.5


def test_safety_at_threshold_rejects_empty_success_denominator() -> None:
    with pytest.raises(ValueError, match="at least one"):
        safety_at_threshold([0.2, 0.8], 0.5, succeeded=[False, False])


def test_compare_thresholds_reports_expected_fields() -> None:
    honest = np.arange(10_000, dtype=float)
    attacks = np.array([9_950, 9_975, 9_999], dtype=float)

    results = compare_thresholds(honest, attacks, alpha=0.01, delta=0.1)

    assert set(results) == {"empirical", "certified"}
    assert results["empirical"].threshold <= results["certified"].threshold
    assert results["empirical"].certified_fpr_upper is None
    assert results["certified"].certified_fpr_upper is not None
    assert results["empirical"].attack_safety >= results["certified"].attack_safety


def test_compare_thresholds_reports_held_out_fpr() -> None:
    calibration = np.arange(10_000, dtype=float)
    attacks = np.array([9_950, 9_975, 9_999], dtype=float)
    empirical = empirical_threshold(calibration, alpha=0.01)
    certified = certified_threshold(calibration, alpha=0.01, delta=0.1)

    test = np.zeros(1_000, dtype=float)
    test[:15] = empirical
    test[15:20] = certified

    results = compare_thresholds(
        calibration,
        attacks,
        honest_test=test,
        alpha=0.01,
        delta=0.1,
    )

    assert results["empirical"].honest_fpr > 0.01
    assert results["certified"].honest_fpr <= 0.01


def test_compare_thresholds_reports_zero_certified_upper_when_flagging_nothing() -> None:
    honest = np.arange(100, dtype=float)
    attacks = np.array([98, 99], dtype=float)

    results = compare_thresholds(honest, attacks, alpha=0.01, delta=0.1)

    assert math.isinf(results["certified"].threshold)
    assert results["certified"].honest_fpr == 0.0
    assert results["certified"].certified_fpr_upper == 0.0
