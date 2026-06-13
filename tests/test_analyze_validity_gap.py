import numpy as np

from monitor_cert import cp_upper
from scripts.analyze_validity_gap import (
    evaluate_split,
    minimum_sample_size,
    run_exhaustive_subsampling,
    summarize_trials,
)


def test_zero_tail_minimum_sample_size_matches_closed_form() -> None:
    assert minimum_sample_size(0.01, 0.10, 0) == 230
    assert minimum_sample_size(0.01, 0.05, 0) == 299
    assert minimum_sample_size(0.01, 0.01, 0) == 459


def test_positive_tail_minimum_is_smallest_valid_n() -> None:
    minimum = minimum_sample_size(0.01, 0.10, 2)

    assert minimum == 531
    assert cp_upper(2, minimum, 0.10) <= 0.01
    assert cp_upper(2, minimum - 1, 0.10) > 0.01


def test_exhaustive_subsampling_uses_trajectory_complements() -> None:
    grouped = {
        "a": np.array([0.0, 0.0]),
        "b": np.array([1.0, 1.0, 1.0]),
        "c": np.array([2.0]),
        "d": np.array([3.0, 3.0]),
    }
    attacks = np.array([2.0, 4.0])

    trials = run_exhaustive_subsampling(
        grouped,
        attacks,
        calibration_trajectory_counts=(2,),
    )

    assert len(trials) == 6 * 2 * 3
    assert {trial.calibration_action_count + trial.test_action_count for trial in trials} == {
        8
    }


def test_split_records_all_alpha_delta_pairs() -> None:
    calibration = np.array([0.0] * 99 + [4.0])
    test = np.array([0.0] * 100)
    attacks = np.array([3.0, 4.0, 6.0])

    trials = evaluate_split(
        calibration,
        test,
        attacks,
        calibration_trajectory_count=2,
    )
    summaries = summarize_trials(trials)

    assert len(trials) == 6
    assert len(summaries) == 6
    assert all(summary.combinations == 1 for summary in summaries)
    assert all(summary.empirical_violation_rate == 0 for summary in summaries)
