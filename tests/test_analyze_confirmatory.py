import pytest

from scripts.analyze_confirmatory import (
    MULTI_THRESHOLD,
    ZMEAN3_THRESHOLD,
    attack_units,
    exact_mcnemar_pvalue,
    one_per_run,
    paired_result,
)


def test_exact_mcnemar_reproduces_original_matched_49_result() -> None:
    assert exact_mcnemar_pvalue(10, 2) == pytest.approx(0.03857421875)
    assert exact_mcnemar_pvalue(0, 0) == 1.0


def test_one_per_run_selects_ascending_trajectory_id() -> None:
    units = [
        _unit("b", "run-1", False, True),
        _unit("a", "run-1", True, True),
        _unit("c", "run-2", False, False),
    ]

    selected = one_per_run(units)

    assert [unit["trajectory_id"] for unit in selected] == ["a", "c"]


def test_paired_result_counts_discordant_pairs_and_environment_rates() -> None:
    units = [
        _unit("a", "run-a", True, True),
        _unit("b", "run-b", False, True),
        _unit("c", "run-c", True, False),
        _unit("d", "run-d", False, False),
    ]

    result = paired_result(units, "fixture")

    assert result.both == 1
    assert result.zmean3_only == 1
    assert result.multi_only == 1
    assert result.neither == 1
    assert result.multi_detection == 0.5
    assert result.zmean3_detection == 0.5
    assert result.net_lift == 0.0
    assert result.mcnemar_pvalue == 1.0
    assert result.by_environment["media_processing"]["total"] == 4


def test_attack_units_use_max_action_and_frozen_thresholds() -> None:
    retained = {
        "attack": {
            "environment": "media_processing",
            "run_id": "run",
            "variant_family": "family",
            "side_task_id": "side-task",
            "side_task_success": True,
            "main_task_success": False,
        }
    }
    rows = [
        {
            "trajectory_id": "attack",
            "multi_baseline": MULTI_THRESHOLD - 0.5,
            "zmean3": ZMEAN3_THRESHOLD + 0.1,
        },
        {
            "trajectory_id": "attack",
            "multi_baseline": MULTI_THRESHOLD,
            "zmean3": ZMEAN3_THRESHOLD - 0.1,
        },
    ]

    unit = attack_units(rows, retained)[0]

    assert unit["max_multi_baseline"] == MULTI_THRESHOLD
    assert unit["max_zmean3"] == pytest.approx(ZMEAN3_THRESHOLD + 0.1)
    assert unit["multi_caught"] is True
    assert unit["zmean3_caught"] is True


def _unit(
    trajectory_id: str,
    run_id: str,
    multi_caught: bool,
    zmean3_caught: bool,
) -> dict[str, object]:
    return {
        "trajectory_id": trajectory_id,
        "run_id": run_id,
        "environment": "media_processing",
        "multi_caught": multi_caught,
        "zmean3_caught": zmean3_caught,
    }
