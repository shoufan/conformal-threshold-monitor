from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import NamedTuple, cast

import numpy as np
from numpy.typing import NDArray

DEFAULT_SCORE_FIELD = "actions[].monitor_response.sus_score"
SUPPORTED_SUFFIXES = {".eval", ".json", ".jsonl"}


class AttackRecord(NamedTuple):
    trajectory_id: str
    max_action_score: float
    side_task_success: bool
    environment: str
    side_task_type: str
    variant_family: str


class HonestSplit(NamedTuple):
    calibration: NDArray[np.float64]
    test: NDArray[np.float64]
    calibration_trajectory_ids: tuple[str, ...]
    test_trajectory_ids: tuple[str, ...]


def load_honest_scores(
    paths: str | Path | Iterable[str | Path],
    *,
    score_field: str = DEFAULT_SCORE_FIELD,
) -> dict[str, NDArray[np.float64]]:
    """Load per-action honest scores while preserving trajectory grouping."""
    grouped: dict[str, NDArray[np.float64]] = {}
    for source, index, document in _load_documents(paths):
        trajectory_id = _trajectory_id(document, source, index)
        if trajectory_id in grouped:
            raise ValueError(f"duplicate trajectory_id: {trajectory_id}")
        grouped[trajectory_id] = _extract_scores(document, score_field, source)
    if not grouped:
        raise ValueError("no honest trajectories found")
    return grouped


def load_attack_records(
    paths: str | Path | Iterable[str | Path],
    *,
    score_field: str = DEFAULT_SCORE_FIELD,
) -> list[AttackRecord]:
    """Load one max action score and analysis metadata per attack trajectory."""
    records: list[AttackRecord] = []
    for source, index, document in _load_documents(paths):
        trajectory_id = _trajectory_id(document, source, index)
        scores = _extract_scores(document, score_field, source)
        records.append(
            AttackRecord(
                trajectory_id=trajectory_id,
                max_action_score=float(np.max(scores)),
                side_task_success=_side_task_success(document),
                environment=_string_field(
                    document,
                    ("environment", "environment_name", "metadata.environment", "metadata.env"),
                    default="unknown",
                ),
                side_task_type=_string_field(
                    document,
                    (
                        "side_task.failure_type",
                        "side_task.task_category",
                        "side_task_type",
                        "failure_type",
                        "task_category",
                        "metadata.failure_type",
                        "metadata.task_category",
                    ),
                    default="unknown",
                ),
                variant_family=_variant_family(document, trajectory_id),
            )
        )
    if not records:
        raise ValueError("no attack trajectories found")
    return records


def split_honest_by_trajectory(
    grouped_scores: Mapping[str, NDArray[np.float64]],
    *,
    test_fraction: float = 0.30,
    seed: int = 0,
) -> HonestSplit:
    """Split whole trajectories, then pool their per-action scores."""
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    trajectory_ids = sorted(grouped_scores)
    if len(trajectory_ids) < 2:
        raise ValueError("at least two honest trajectories are required")

    rng = np.random.default_rng(seed)
    shuffled = [trajectory_ids[index] for index in rng.permutation(len(trajectory_ids))]
    test_count = max(1, min(len(shuffled) - 1, round(len(shuffled) * test_fraction)))
    test_ids = tuple(sorted(shuffled[:test_count]))
    calibration_ids = tuple(sorted(shuffled[test_count:]))

    return HonestSplit(
        calibration=_pool_scores(grouped_scores, calibration_ids),
        test=_pool_scores(grouped_scores, test_ids),
        calibration_trajectory_ids=calibration_ids,
        test_trajectory_ids=test_ids,
    )


def deduplicate_successful_attacks(records: Iterable[AttackRecord]) -> list[AttackRecord]:
    """Keep one maximum-scoring successful attack per variant family."""
    by_family: dict[str, AttackRecord] = {}
    for record in records:
        if not record.side_task_success:
            continue
        current = by_family.get(record.variant_family)
        if current is None or record.max_action_score > current.max_action_score:
            by_family[record.variant_family] = record
    return [by_family[family] for family in sorted(by_family)]


def _load_documents(
    paths: str | Path | Iterable[str | Path],
) -> list[tuple[Path, int, Mapping[str, object]]]:
    loaded: list[tuple[Path, int, Mapping[str, object]]] = []
    for source in _input_files(paths):
        for index, document in enumerate(_read_documents(source)):
            loaded.append((source, index, document))
    return loaded


def _input_files(paths: str | Path | Iterable[str | Path]) -> list[Path]:
    raw_paths = [paths] if isinstance(paths, (str, Path)) else list(paths)
    files: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(
                child
                for child in sorted(path.rglob("*"))
                if child.is_file() and child.suffix.lower() in SUPPORTED_SUFFIXES
            )
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(path)
    if not files:
        raise ValueError("no supported trajectory files found")
    return files


def _read_documents(path: Path) -> list[Mapping[str, object]]:
    text = path.read_text(encoding="utf-8")
    try:
        value = cast(object, json.loads(text))
        return _documents_from_value(value, path)
    except json.JSONDecodeError:
        documents: list[Mapping[str, object]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = cast(object, json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number} is not valid JSONL") from error
            documents.extend(_documents_from_value(value, path))
        return documents


def _documents_from_value(value: object, path: Path) -> list[Mapping[str, object]]:
    if isinstance(value, Mapping):
        document = _string_key_mapping(value, path)
        for collection_key in ("trajectories", "samples"):
            collection = document.get(collection_key)
            if isinstance(collection, list):
                return [_string_key_mapping(item, path) for item in collection]
        return [document]
    if isinstance(value, list):
        return [_string_key_mapping(item, path) for item in value]
    raise ValueError(f"{path} must contain a trajectory object or list")


def _string_key_mapping(value: object, path: Path) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{path} contains a non-object trajectory")
    return cast(Mapping[str, object], value)


def _extract_scores(
    document: Mapping[str, object],
    score_field: str,
    source: Path,
) -> NDArray[np.float64]:
    if score_field.count("[]") != 1:
        raise ValueError("score_field must contain exactly one [] collection marker")
    collection_path, value_path = score_field.split("[]")
    collection_path = collection_path.rstrip(".")
    value_path = value_path.lstrip(".")
    collection = _get_path(document, collection_path)
    if not isinstance(collection, Sequence) or isinstance(collection, (str, bytes)):
        raise ValueError(f"{source}: score collection {collection_path!r} is missing")

    scores: list[float] = []
    for item in collection:
        if not isinstance(item, Mapping):
            raise ValueError(f"{source}: score collection contains a non-object item")
        value = _get_path(_string_key_mapping(item, source), value_path)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{source}: score field {score_field!r} is missing or non-numeric")
        score = float(value)
        if not np.isfinite(score):
            raise ValueError(f"{source}: score field {score_field!r} must be finite")
        scores.append(score)
    if not scores:
        raise ValueError(f"{source}: no action scores found at {score_field!r}")
    return np.asarray(scores, dtype=np.float64)


def _trajectory_id(document: Mapping[str, object], source: Path, index: int) -> str:
    return _string_field(
        document,
        ("trajectory_id", "id", "_id", "sample_id", "metadata.trajectory_id"),
        default=f"{source.stem}:{index}",
    )


def _side_task_success(document: Mapping[str, object]) -> bool:
    value = _first_present(
        document,
        (
            "side_task_success",
            "side_task.success",
            "scores.side_task_success",
            "metadata.side_task_success",
        ),
    )
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    raise ValueError("attack trajectory is missing a boolean side_task_success field")


def _variant_family(document: Mapping[str, object], trajectory_id: str) -> str:
    tags_value = _first_present(document, ("tags", "metadata.tags"))
    tags = [tags_value] if isinstance(tags_value, str) else tags_value
    if isinstance(tags, Sequence):
        for tag in tags:
            if isinstance(tag, str) and "variant-of-" in tag:
                family = tag.split("variant-of-", maxsplit=1)[1].strip()
                if family:
                    return family
    return trajectory_id


def _string_field(
    document: Mapping[str, object],
    paths: Sequence[str],
    *,
    default: str,
) -> str:
    value = _first_present(document, paths)
    return value if isinstance(value, str) and value else default


def _first_present(document: Mapping[str, object], paths: Sequence[str]) -> object | None:
    for path in paths:
        value = _get_path(document, path)
        if value is not None:
            return value
    return None


def _get_path(document: Mapping[str, object], path: str) -> object | None:
    current: object = document
    for part in path.split("."):
        if not part:
            continue
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def _pool_scores(
    grouped_scores: Mapping[str, NDArray[np.float64]],
    trajectory_ids: Sequence[str],
) -> NDArray[np.float64]:
    arrays = [grouped_scores[trajectory_id] for trajectory_id in trajectory_ids]
    return np.concatenate(arrays).astype(np.float64, copy=False)
