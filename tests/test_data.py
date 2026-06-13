from pathlib import Path

import numpy as np

from monitor_cert import (
    deduplicate_successful_attacks,
    load_attack_records,
    load_honest_scores,
    split_honest_by_trajectory,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_honest_scores_preserves_trajectory_groups() -> None:
    grouped = load_honest_scores(FIXTURES / "honest_trajectories.jsonl")

    assert set(grouped) == {"honest-1", "honest-2", "honest-3"}
    np.testing.assert_array_equal(grouped["honest-1"], np.array([0.1, 0.4]))
    np.testing.assert_array_equal(grouped["honest-2"], np.array([0.2, 0.6, 0.3]))


def test_load_honest_scores_accepts_configurable_score_field() -> None:
    grouped = load_honest_scores(
        FIXTURES / "custom_score_trajectory.json",
        score_field="steps[].scores.suspicion",
    )

    np.testing.assert_array_equal(grouped["custom-1"], np.array([1.25, 2.5]))


def test_split_honest_by_trajectory_has_no_leakage() -> None:
    grouped = load_honest_scores(FIXTURES / "honest_trajectories.jsonl")

    split = split_honest_by_trajectory(grouped, test_fraction=1 / 3, seed=7)

    assert set(split.calibration_trajectory_ids).isdisjoint(split.test_trajectory_ids)
    assert set(split.calibration_trajectory_ids) | set(split.test_trajectory_ids) == set(grouped)
    assert len(split.calibration) + len(split.test) == sum(map(len, grouped.values()))


def test_load_attack_records_and_deduplicate_successful_families() -> None:
    records = load_attack_records(FIXTURES / "attack_trajectories.jsonl")

    first = records[0]
    assert first.max_action_score == 0.9
    assert first.side_task_success is True
    assert first.environment == "slack_clone"
    assert first.side_task_type == "exfiltration"
    assert first.variant_family == "family-1"

    units = deduplicate_successful_attacks(records)

    assert [unit.variant_family for unit in units] == ["attack-3", "family-1"]
    assert [unit.max_action_score for unit in units] == [0.7, 0.9]
    assert all(unit.side_task_success for unit in units)
