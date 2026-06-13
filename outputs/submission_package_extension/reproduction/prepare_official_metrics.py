from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

from monitor_cert.zmean3 import (
    CONTROL_TOWER_OFFSET,
    CONTROL_TOWER_SCALE,
    control_tower_zmean3,
)

MATCHED_ENVIRONMENTS = {"media_processing", "web_scraping", "clinical_trial"}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize matched existing scores for zero-call Control Tower metrics."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs/official_metrics"),
    )
    args = parser.parse_args()

    multi_honest_sources = (
        Path("outputs/multi_scored/honest"),
        Path("outputs/multi_scored_crossenv/web_scraping"),
        Path("outputs/multi_scored_crossenv/clinical_trial"),
    )
    multi_attack_source = Path("outputs/multi_scored/attacks")
    aligned_honest_path = Path(
        "outputs/ensemble_extension/scored_components/aligned_honest_components.json"
    )
    aligned_attack_path = Path(
        "outputs/ensemble_extension/scored_components/aligned_attack_components.json"
    )

    multi_output = args.output_root / "multi_baseline" / "matched_inputs"
    zmean_output = args.output_root / "zmean3_materialized_inputs"
    source_map = _source_map((*multi_honest_sources, multi_attack_source))

    multi_counts = materialize_multi_inputs(
        honest_sources=multi_honest_sources,
        attack_source=multi_attack_source,
        output_dir=multi_output,
    )
    zmean_counts = materialize_zmean3_inputs(
        aligned_honest_path=aligned_honest_path,
        aligned_attack_path=aligned_attack_path,
        source_map=source_map,
        output_dir=zmean_output,
    )
    payload = {
        "schema_version": 1,
        "model_calls": 0,
        "multi": multi_counts,
        "zmean3": zmean_counts,
        "zmean3_control_tower_encoding": {
            "formula": "encoded = raw_zmean3 * scale + offset",
            "scale": CONTROL_TOWER_SCALE,
            "offset": CONTROL_TOWER_OFFSET,
            "preserves_ordering_ties_and_audit_decisions": True,
        },
        "honest_metadata_adjustment": (
            "side_task and side_task_success are cleared in metrics-only copies because "
            "Control Tower defines an honest run by side_task is None"
        ),
    }
    _write_json(args.output_root / "materialization_manifest.json", payload)
    print(json.dumps(payload, indent=2))


def materialize_multi_inputs(
    *,
    honest_sources: Sequence[Path],
    attack_source: Path,
    output_dir: Path,
) -> dict[str, int]:
    honest_output = output_dir / "honest"
    attack_output = output_dir / "attacks"
    _reset_json_dir(honest_output)
    _reset_json_dir(attack_output)

    honest_count = 0
    for path in _json_files(honest_sources):
        data = _load_json(path)
        _make_honest(data)
        _write_json(honest_output / path.name, data)
        honest_count += 1

    attack_count = 0
    for path in sorted(attack_source.glob("*.json")):
        data = _load_json(path)
        if _environment_id(data) not in MATCHED_ENVIRONMENTS:
            continue
        if data.get("side_task_success") is not True:
            continue
        _write_json(attack_output / path.name, data)
        attack_count += 1

    return {"honest_trajectories": honest_count, "attack_trajectories": attack_count}


def materialize_zmean3_inputs(
    *,
    aligned_honest_path: Path,
    aligned_attack_path: Path,
    source_map: Mapping[str, Path],
    output_dir: Path,
) -> dict[str, int]:
    honest_payload = _load_json(aligned_honest_path)
    attack_payload = _load_json(aligned_attack_path)
    honest_rows = list(honest_payload["actions"])
    attack_rows = [
        row for row in attack_payload["actions"] if row["environment"] in MATCHED_ENVIRONMENTS
    ]

    honest_output = output_dir / "honest"
    attack_output = output_dir / "attacks"
    _reset_json_dir(honest_output)
    _reset_json_dir(attack_output)

    honest_counts = _materialize_zmean_population(
        rows=honest_rows,
        source_map=source_map,
        output_dir=honest_output,
        honest=True,
    )
    attack_counts = _materialize_zmean_population(
        rows=attack_rows,
        source_map=source_map,
        output_dir=attack_output,
        honest=False,
    )
    return {
        "honest_trajectories": honest_counts["trajectories"],
        "honest_scored_actions": honest_counts["scored_actions"],
        "attack_trajectories": attack_counts["trajectories"],
        "attack_scored_actions": attack_counts["scored_actions"],
    }


def _materialize_zmean_population(
    *,
    rows: Sequence[dict[str, Any]],
    source_map: Mapping[str, Path],
    output_dir: Path,
    honest: bool,
) -> dict[str, int]:
    by_trajectory: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_trajectory[str(row["trajectory_id"])].append(row)

    scored_actions = 0
    for trajectory_id, trajectory_rows in sorted(by_trajectory.items()):
        source_path = source_map[trajectory_id]
        data = _load_json(source_path)
        if honest:
            _make_honest(data)
        elif _environment_id(data) not in MATCHED_ENVIRONMENTS:
            raise ValueError(f"unmatched attack entered zmean3 materialization: {trajectory_id}")

        row_by_index = {int(row["action_index"]): row for row in trajectory_rows}
        for action in data["actions"]:
            action_index = int(action["index"])
            matched_row = row_by_index.get(action_index)
            if matched_row is None:
                action["monitor_response"] = {
                    "last_error": "not in frozen three-component intersection",
                    "attempts": 0,
                }
                continue
            expected_tool_call = matched_row.get("tool_call_id")
            actual_tool_call = action.get("tool_call_id")
            if expected_tool_call and actual_tool_call and expected_tool_call != actual_tool_call:
                raise ValueError(
                    f"tool_call_id mismatch for {trajectory_id}:{action_index}"
                )
            raw_score = float(matched_row["zmean3"])
            encoded_score = control_tower_zmean3(
                float(matched_row["orthogonal_score"]),
                float(matched_row["old_action_score"]),
                float(matched_row["goal_analysis_score"]),
            )
            action["monitor_response"] = {
                "sus_score": encoded_score,
                "reasoning": (
                    "Materialized frozen zmean3 from existing component outputs; "
                    f"raw_zmean3={raw_score:.12g}"
                ),
                "error": None,
                "is_ensemble": False,
                "members": None,
                "monitor_name": "zmean3-materialized",
            }
            scored_actions += 1
        _write_json(output_dir / source_path.name, data)

    return {"trajectories": len(by_trajectory), "scored_actions": scored_actions}


def _make_honest(data: dict[str, Any]) -> None:
    data["side_task"] = None
    data["side_task_success"] = None
    data["attempts_st"] = False
    metadata = dict(data.get("metadata") or {})
    metadata["official_metrics_materialization"] = "honest-side-task-metadata-cleared"
    data["metadata"] = metadata


def _source_map(directories: Iterable[Path]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in _json_files(directories):
        trajectory_id = str(_load_json(path)["trajectory_id"])
        if trajectory_id in result:
            raise ValueError(f"duplicate trajectory source: {trajectory_id}")
        result[trajectory_id] = path
    return result


def _json_files(directories: Iterable[Path]) -> list[Path]:
    return sorted(path for directory in directories for path in directory.glob("*.json"))


def _environment_id(data: Mapping[str, Any]) -> str:
    environment = data.get("environment")
    if isinstance(environment, Mapping):
        return str(environment.get("id"))
    return str(environment)


def _reset_json_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for existing in path.glob("*.json"):
        existing.unlink()


def _load_json(path: Path) -> dict[str, Any]:
    return deepcopy(json.loads(path.read_text()))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
