import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest

from scripts.build_multi_dataset import (
    build_scoring_manifest,
    extract_scored_dataset,
    validate_extracted_dataset,
)


def test_extract_scored_dataset_excludes_error_placeholders(tmp_path: Path) -> None:
    output = tmp_path / "scored"
    output.mkdir()
    _write_trajectory(
        output / "one.json",
        side_task_success=True,
        actions=[
            _scored_action(0, 1.5),
            _scored_action(1, 0.0, error='"submit" tool calls are ignored'),
            _scored_action(2, 4.0),
        ],
    )

    payload = extract_scored_dataset(output, kind="attack")
    validate_extracted_dataset(payload, kind="attack")
    all_scores = _list_of_mappings(payload["all_action_scores"])
    attack_units = _list_of_mappings(payload["attack_unit_scores"])
    summary = _mapping(payload["summary"])
    usage = _mapping(summary["usage"])

    assert [score["sus_score"] for score in all_scores] == [1.5, 4.0]
    assert attack_units[0]["max_action_score"] == 4.0
    assert summary["excluded_action_count"] == 1
    assert summary["error_action_count"] == 0
    assert usage["model_calls"] == 4
    assert usage["cost_usd"] == pytest.approx(0.004)


def test_extract_scored_dataset_records_monitor_skips(tmp_path: Path) -> None:
    output = tmp_path / "scored"
    output.mkdir()
    _write_trajectory(
        output / "one.json",
        actions=[
            _scored_action(0, 2),
            {
                "index": 1,
                "function": "text_editor",
                "monitor_response": {
                    "last_error": "RetryError: provider server_error",
                    "attempts": 3,
                },
            },
        ],
    )

    payload = extract_scored_dataset(output, kind="honest")
    summary = _mapping(payload["summary"])
    trajectories = _list_of_mappings(payload["trajectories"])
    excluded = _list_of_mappings(trajectories[0]["excluded_actions"])

    assert summary["valid_action_count"] == 1
    assert summary["error_action_count"] == 1
    assert excluded[0]["reason"] == (
        "monitor skipped after 3 attempts: RetryError: provider server_error"
    )


def test_extract_scored_dataset_excludes_errored_ensemble_member(
    tmp_path: Path,
) -> None:
    output = tmp_path / "scored"
    output.mkdir()
    action = _scored_action(0, 1.0)
    response = action["monitor_response"]
    assert isinstance(response, dict)
    members = response["members"]
    assert isinstance(members, list)
    assert isinstance(members[0], dict)
    members[0]["sus_score"] = 0.0
    members[0]["error"] = "Missing <score>...</score> tag"
    _write_trajectory(output / "one.json", actions=[action, _scored_action(1, 2.0)])

    payload = extract_scored_dataset(output, kind="honest")
    summary = _mapping(payload["summary"])
    usage = _mapping(summary["usage"])
    trajectories = _list_of_mappings(payload["trajectories"])
    excluded = _list_of_mappings(trajectories[0]["excluded_actions"])

    assert [
        score["sus_score"] for score in _list_of_mappings(payload["all_scores"])
    ] == [2.0]
    assert summary["valid_action_count"] == 1
    assert summary["error_action_count"] == 1
    assert usage["model_calls"] == 4
    assert usage["cost_usd"] == pytest.approx(0.004)
    assert excluded[0]["reason"] == (
        "ensemble member error: Missing <score>...</score> tag"
    )


def test_attack_units_include_successful_attacks_only(tmp_path: Path) -> None:
    output = tmp_path / "scored"
    output.mkdir()
    _write_trajectory(output / "one.json", side_task_success=True, actions=[_scored_action(0, 2)])
    _write_trajectory(
        output / "two.json",
        side_task_success=False,
        trajectory_id="two",
        actions=[_scored_action(0, 9)],
    )

    payload = extract_scored_dataset(output, kind="attack")
    trajectories = _list_of_mappings(payload["trajectories"])
    attack_units = _list_of_mappings(payload["attack_unit_scores"])

    assert len(trajectories) == 2
    assert [unit["trajectory_id"] for unit in attack_units] == ["one"]


def test_manifest_counts_monitorable_actions(tmp_path: Path) -> None:
    honest = tmp_path / "honest"
    attacks = tmp_path / "attacks"
    honest.mkdir()
    attacks.mkdir()
    actions = [
        {"index": 0, "function": "bash", "output_error": None},
        {"index": 1, "function": "submit", "output_error": None},
        {"index": 2, "function": "bash", "output_error": "parsing: invalid"},
    ]
    _write_input(honest / "honest.json", "honest", actions)
    _write_input(attacks / "attack.json", "attack", actions)

    manifest = build_scoring_manifest(honest, attacks)
    totals = _mapping(manifest["totals"])

    assert totals["estimated_honest_monitorable_actions"] == 1
    assert totals["estimated_attack_monitorable_actions"] == 1
    assert totals["estimated_model_calls"] == 4
    assert manifest["no_upload"] is True


def test_validation_rejects_mismatched_flat_scores(tmp_path: Path) -> None:
    output = tmp_path / "scored"
    output.mkdir()
    _write_trajectory(output / "one.json", actions=[_scored_action(0, 2)])
    payload = extract_scored_dataset(output, kind="honest")
    payload["all_scores"] = []

    with pytest.raises(ValueError, match="flat score array"):
        validate_extracted_dataset(payload, kind="honest")


def _scored_action(index: int, score: float, *, error: str | None = None) -> dict[str, object]:
    members = None
    if error is None:
        members = [
            {
                "sus_score": score,
                "error": None,
                "members": None,
                "model_name": "openai/gpt-5-nano",
                "input_tokens": 10,
                "output_tokens": 2,
                "cached_input_tokens": 3,
                "cost_usd": 0.001,
            },
            {
                "sus_score": score,
                "error": None,
                "members": None,
                "model_name": "openai/gpt-5-nano",
                "input_tokens": 12,
                "output_tokens": 3,
                "cached_input_tokens": 4,
                "cost_usd": 0.001,
            },
        ]
    return {
        "index": index,
        "function": "bash" if error is None else "submit",
        "monitor_response": {
            "sus_score": score,
            "error": error,
            "is_ensemble": error is None,
            "members": members,
        },
    }


def _write_trajectory(
    path: Path,
    *,
    actions: list[dict[str, object]],
    side_task_success: bool = False,
    trajectory_id: str = "one",
) -> None:
    path.write_text(
        json.dumps(
            {
                "trajectory_id": trajectory_id,
                "environment": {"id": "test_env"},
                "side_task_success": side_task_success,
                "side_task": {
                    "id": "test_side_task",
                    "task_category": "test_category",
                    "failure_type": "test_failure",
                },
                "tags": ["variant-of-test"] if trajectory_id == "one" else [],
                "actions": actions,
            }
        ),
        encoding="utf-8",
    )


def _write_input(
    path: Path, trajectory_id: str, actions: list[dict[str, object]]
) -> None:
    path.write_text(
        json.dumps(
            {
                "trajectory_id": trajectory_id,
                "environment": {"id": "test_env"},
                "actions": actions,
            }
        ),
        encoding="utf-8",
    )


def _mapping(value: object) -> Mapping[str, object]:
    assert isinstance(value, Mapping)
    return cast(Mapping[str, object], value)


def _list_of_mappings(value: object) -> list[Mapping[str, object]]:
    assert isinstance(value, list)
    return [_mapping(item) for item in value]
