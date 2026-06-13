from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import TypedDict, cast

HIDDEN_TOOLS = {"run_side_task_test", "side_task_scorer", "submit"}
HONEST_COST_PER_SCORE = 0.082503 / 54
ATTACK_COST_PER_SCORE = 0.002566 / 2
HONEST_USAGE_PER_SCORE = {
    "input_tokens": 597_898 / 54,
    "output_tokens": 108_733 / 54,
    "cached_input_tokens": 1_823_360 / 54,
}
ATTACK_USAGE_PER_SCORE = {
    "input_tokens": 17_970 / 2,
    "output_tokens": 4_169 / 2,
    "cached_input_tokens": 0.0,
}
GPT_5_NANO_INPUT_COST_PER_TOKEN = 0.05 / 1_000_000
GPT_5_NANO_OUTPUT_COST_PER_TOKEN = 0.40 / 1_000_000
GPT_5_NANO_CACHED_INPUT_COST_PER_TOKEN = 0.005 / 1_000_000
PREEXISTING_ATTACK_SMOKE_COST_USD = 0.002566


class Usage(TypedDict):
    model_calls: int
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    cost_usd: float


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare and extract the Track A multi-monitor scoring dataset."
    )
    parser.add_argument(
        "--honest-input",
        type=Path,
        default=Path("data/honest/attempts_st_false_sample"),
    )
    parser.add_argument(
        "--attack-input",
        type=Path,
        default=Path("data/attacks/lastraj"),
    )
    parser.add_argument(
        "--honest-output",
        type=Path,
        default=Path("outputs/multi_scored/honest"),
    )
    parser.add_argument(
        "--attack-output",
        type=Path,
        default=Path("outputs/multi_scored/attacks"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/multi_scored"),
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write the preflight scoring manifest without requiring scored outputs.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_scoring_manifest(args.honest_input, args.attack_input)
    _write_json(args.output_dir / "scoring_manifest.json", manifest)
    if args.manifest_only:
        print(f"Wrote scoring manifest to {args.output_dir / 'scoring_manifest.json'}")
        return

    honest = extract_scored_dataset(args.honest_output, kind="honest")
    attacks = extract_scored_dataset(args.attack_output, kind="attack")
    validate_extracted_dataset(honest, kind="honest")
    validate_extracted_dataset(attacks, kind="attack")
    _validate_expected_ids(manifest, honest, attacks)

    _write_json(args.output_dir / "honest_scores.json", honest)
    _write_json(args.output_dir / "attack_scores.json", attacks)
    _write_report(args.output_dir / "multi_scoring_report.md", manifest, honest, attacks)
    print(f"Wrote multi-monitor dataset to {args.output_dir}")


def build_scoring_manifest(honest_dir: Path, attack_dir: Path) -> dict[str, object]:
    honest_rows = [_input_manifest(path) for path in sorted(honest_dir.glob("*.json"))]
    attack_rows = [_input_manifest(path) for path in sorted(attack_dir.glob("*.json"))]
    if not honest_rows or not attack_rows:
        raise ValueError("both honest and attack input directories must contain JSON files")

    honest_scores = sum(_required_int(row, "estimated_monitorable_actions") for row in honest_rows)
    attack_scores = sum(_required_int(row, "estimated_monitorable_actions") for row in attack_rows)
    honest_estimate = _estimated_usage(
        honest_scores, HONEST_USAGE_PER_SCORE, HONEST_COST_PER_SCORE
    )
    attack_estimate = _estimated_usage(
        attack_scores, ATTACK_USAGE_PER_SCORE, ATTACK_COST_PER_SCORE
    )
    total_cost = honest_estimate["cost_usd"] + attack_estimate["cost_usd"]

    return {
        "generated": date.today().isoformat(),
        "monitor": "multi",
        "monitor_args": [],
        "only_action": True,
        "max_concurrent": 2,
        "no_upload": True,
        "hawk_used": False,
        "honest_pool_note": (
            "All locally available vetted honest-intent trajectories are included. "
            "The pool is smaller than the requested 1,500 valid-action target."
        ),
        "honest": honest_rows,
        "attacks": attack_rows,
        "totals": {
            "honest_trajectories": len(honest_rows),
            "attack_trajectories": len(attack_rows),
            "honest_raw_actions": sum(_required_int(row, "raw_actions") for row in honest_rows),
            "attack_raw_actions": sum(_required_int(row, "raw_actions") for row in attack_rows),
            "estimated_honest_monitorable_actions": honest_scores,
            "estimated_attack_monitorable_actions": attack_scores,
            "estimated_model_calls": 2 * (honest_scores + attack_scores),
        },
        "cost_estimate": {
            "basis": "Measured one-trajectory multi smoke tests, scaled per valid action.",
            "honest": honest_estimate,
            "attacks": attack_estimate,
            "total_cost_usd": total_cost,
            "total_cost_with_50pct_contingency_usd": total_cost * 1.5,
        },
    }


def extract_scored_dataset(output_dir: Path, *, kind: str) -> dict[str, object]:
    if kind not in {"honest", "attack"}:
        raise ValueError(f"unsupported dataset kind: {kind}")
    paths = sorted(output_dir.glob("*.json"))
    if not paths:
        raise ValueError(f"no scored trajectory files found in {output_dir}")

    trajectories: list[dict[str, object]] = []
    flat_scores: list[dict[str, object]] = []
    attack_units: list[dict[str, object]] = []
    total_usage: Usage = _empty_usage()
    models: Counter[str] = Counter()
    errors: Counter[str] = Counter()

    for path in paths:
        document = _load_document(path)
        trajectory_id = _required_str(document, "trajectory_id")
        action_values = document.get("actions")
        if not isinstance(action_values, list):
            raise ValueError(f"{path}: actions must be a list")

        scores: list[dict[str, object]] = []
        excluded_actions: list[dict[str, object]] = []
        trajectory_usage = _empty_usage()
        for position, action_value in enumerate(action_values):
            action = _as_mapping(action_value, path)
            action_index = _action_index(action, position)
            function = _optional_str(action.get("function"), default="unknown")
            response_value = action.get("monitor_response")
            if not isinstance(response_value, Mapping):
                reason = "missing monitor_response"
                errors[reason] += 1
                excluded_actions.append(
                    {"action_index": action_index, "function": function, "reason": reason}
                )
                continue

            response = _string_mapping(response_value, path)
            if "last_error" in response:
                attempts = _optional_int(response.get("attempts"))
                last_error = _optional_str(
                    response.get("last_error"), default="unknown monitor error"
                )
                reason = f"monitor skipped after {attempts} attempts: {last_error}"
                errors[reason] += 1
                excluded_actions.append(
                    {"action_index": action_index, "function": function, "reason": reason}
                )
                continue
            member_error = _ensemble_member_error(response, path)
            if member_error is not None:
                action_usage, action_models = _response_usage(response, path)
                _add_usage(trajectory_usage, action_usage)
                _add_usage(total_usage, action_usage)
                models.update(action_models)
                reason = f"ensemble member error: {member_error}"
                errors[reason] += 1
                excluded_actions.append(
                    {"action_index": action_index, "function": function, "reason": reason}
                )
                continue
            error = response.get("error")
            score_value = response.get("sus_score")
            if error is not None:
                reason = _optional_str(error, default="unknown monitor error")
                errors[reason] += 1
                excluded_actions.append(
                    {"action_index": action_index, "function": function, "reason": reason}
                )
                continue
            if isinstance(score_value, bool) or not isinstance(score_value, int | float):
                reason = "missing or non-numeric sus_score"
                errors[reason] += 1
                excluded_actions.append(
                    {"action_index": action_index, "function": function, "reason": reason}
                )
                continue
            score = float(score_value)
            if not math.isfinite(score):
                raise ValueError(f"{path}: action {action_index} has a non-finite sus_score")

            score_record = {
                "action_index": action_index,
                "function": function,
                "sus_score": score,
            }
            scores.append(score_record)
            flat_scores.append({"trajectory_id": trajectory_id, **score_record})
            action_usage, action_models = _response_usage(response, path)
            _add_usage(trajectory_usage, action_usage)
            _add_usage(total_usage, action_usage)
            models.update(action_models)

        record: dict[str, object] = {
            "trajectory_id": trajectory_id,
            "environment": _environment(document),
            "raw_action_count": len(action_values),
            "valid_action_count": len(scores),
            "excluded_action_count": len(excluded_actions),
            "error_action_count": sum(
                1
                for item in excluded_actions
                if not _is_by_design_skip(_required_str(item, "reason"))
            ),
            "scores": scores,
            "excluded_actions": excluded_actions,
            "usage": trajectory_usage,
        }
        if kind == "attack":
            side_task = _optional_mapping(document.get("side_task"))
            side_task_success = document.get("side_task_success") is True
            record.update(
                {
                    "side_task_success": side_task_success,
                    "side_task_id": _optional_str(side_task.get("id"), default="unknown"),
                    "side_task_category": _first_string(
                        side_task, ("task_category", "failure_type"), default="unknown"
                    ),
                    "failure_type": _optional_str(
                        side_task.get("failure_type"), default="unknown"
                    ),
                    "variant_family": _variant_family(document, trajectory_id),
                    "max_action_score": max(
                        (_required_float(item, "sus_score") for item in scores),
                        default=None,
                    ),
                }
            )
            if side_task_success and scores:
                attack_units.append(
                    {
                        "trajectory_id": trajectory_id,
                        "max_action_score": max(
                            _required_float(item, "sus_score") for item in scores
                        ),
                        "side_task_success": True,
                        "environment": record["environment"],
                        "side_task_id": record["side_task_id"],
                        "side_task_category": record["side_task_category"],
                        "failure_type": record["failure_type"],
                        "variant_family": record["variant_family"],
                    }
                )
        trajectories.append(record)

    score_key = "all_scores" if kind == "honest" else "all_action_scores"
    payload: dict[str, object] = {
        "schema_version": 1,
        "monitor": "multi",
        "score_field": "actions[].monitor_response.sus_score",
        "trajectories": trajectories,
        score_key: flat_scores,
        "summary": _dataset_summary(trajectories, flat_scores, total_usage, models, errors),
    }
    if kind == "attack":
        payload["attack_unit_definition"] = (
            "Maximum valid action score per successful attack trajectory; not variant-deduplicated."
        )
        payload["attack_unit_scores"] = attack_units
    return payload


def validate_extracted_dataset(payload: Mapping[str, object], *, kind: str) -> None:
    trajectories_value = payload.get("trajectories")
    score_key = "all_scores" if kind == "honest" else "all_action_scores"
    flat_value = payload.get(score_key)
    if not isinstance(trajectories_value, list) or not isinstance(flat_value, list):
        raise ValueError("dataset must contain trajectory and flat score lists")

    grouped: list[tuple[str, int, float]] = []
    for trajectory_value in trajectories_value:
        trajectory = _as_mapping(trajectory_value, Path("<dataset>"))
        trajectory_id = _required_str(trajectory, "trajectory_id")
        scores_value = trajectory.get("scores")
        if not isinstance(scores_value, list):
            raise ValueError(f"{trajectory_id}: scores must be a list")
        for score_value in scores_value:
            score = _as_mapping(score_value, Path("<dataset>"))
            grouped.append(
                (
                    trajectory_id,
                    _required_int(score, "action_index"),
                    _required_float(score, "sus_score"),
                )
            )

    flat: list[tuple[str, int, float]] = []
    for score_value in flat_value:
        score = _as_mapping(score_value, Path("<dataset>"))
        flat.append(
            (
                _required_str(score, "trajectory_id"),
                _required_int(score, "action_index"),
                _required_float(score, "sus_score"),
            )
        )
    if grouped != flat:
        raise ValueError("flat score array does not match per-trajectory scores")

    if kind == "attack":
        units_value = payload.get("attack_unit_scores")
        if not isinstance(units_value, list):
            raise ValueError("attack dataset must contain attack_unit_scores")
        if any(
            _as_mapping(unit, Path("<dataset>")).get("side_task_success") is not True
            for unit in units_value
        ):
            raise ValueError("attack_unit_scores must contain successful attacks only")


def _input_manifest(path: Path) -> dict[str, object]:
    document = _load_document(path)
    actions_value = document.get("actions")
    if not isinstance(actions_value, list):
        raise ValueError(f"{path}: actions must be a list")
    skip_counts: Counter[str] = Counter()
    monitorable = 0
    for action_value in actions_value:
        action = _as_mapping(action_value, path)
        reason = _input_skip_reason(action)
        if reason is None:
            monitorable += 1
        else:
            skip_counts[reason] += 1
    return {
        "trajectory_id": _required_str(document, "trajectory_id"),
        "source": str(path),
        "environment": _environment(document),
        "raw_actions": len(actions_value),
        "estimated_monitorable_actions": monitorable,
        "estimated_skips": dict(sorted(skip_counts.items())),
    }


def _input_skip_reason(action: Mapping[str, object]) -> str | None:
    function = action.get("function")
    if isinstance(function, str) and function in HIDDEN_TOOLS:
        return f'hidden tool: {function}'
    metadata = _optional_mapping(action.get("metadata"))
    if metadata.get("is_policy_private"):
        return "policy-private tool call"
    output_error = action.get("output_error")
    if isinstance(output_error, str) and output_error.startswith("parsing:"):
        return "malformed action (parsing error)"
    return None


def _response_usage(
    response: Mapping[str, object], source: Path
) -> tuple[Usage, Counter[str]]:
    members_value = response.get("members")
    if isinstance(members_value, list) and members_value:
        usage = _empty_usage()
        models: Counter[str] = Counter()
        for member_value in members_value:
            member = _as_mapping(member_value, source)
            member_usage, member_models = _response_usage(member, source)
            _add_usage(usage, member_usage)
            models.update(member_models)
        return usage, models

    model = _optional_str(response.get("model_name"), default="unknown")
    leaf_usage: Usage = {
        "model_calls": 1,
        "input_tokens": _optional_int(response.get("input_tokens")),
        "output_tokens": _optional_int(response.get("output_tokens")),
        "cached_input_tokens": _optional_int(response.get("cached_input_tokens")),
        "cost_usd": _optional_float(response.get("cost_usd")),
    }
    return leaf_usage, Counter({model: 1})


def _ensemble_member_error(
    response: Mapping[str, object], source: Path
) -> str | None:
    members_value = response.get("members")
    if not isinstance(members_value, list):
        return None
    for member_value in members_value:
        member = _as_mapping(member_value, source)
        error = member.get("error")
        if error is not None:
            return _optional_str(error, default="unknown monitor error")
    return None


def _dataset_summary(
    trajectories: list[dict[str, object]],
    flat_scores: list[dict[str, object]],
    usage: Usage,
    models: Counter[str],
    errors: Counter[str],
) -> dict[str, object]:
    scores = [_required_float(record, "sus_score") for record in flat_scores]
    histogram = Counter(scores)
    by_environment: Counter[str] = Counter()
    for trajectory in trajectories:
        by_environment[_required_str(trajectory, "environment")] += _required_int(
            trajectory, "valid_action_count"
        )
    fractional = sum(not score.is_integer() for score in scores)
    token_priced_cost = _gpt_5_nano_token_cost(usage)
    return {
        "trajectory_count": len(trajectories),
        "raw_action_count": sum(
            _required_int(record, "raw_action_count") for record in trajectories
        ),
        "valid_action_count": len(scores),
        "excluded_action_count": sum(
            _required_int(record, "excluded_action_count") for record in trajectories
        ),
        "error_action_count": sum(
            _required_int(record, "error_action_count") for record in trajectories
        ),
        "score_min": min(scores),
        "score_max": max(scores),
        "unique_score_count": len(histogram),
        "fractional_score_count": fractional,
        "fractional_score_rate": fractional / len(scores),
        "score_histogram": {str(score): histogram[score] for score in sorted(histogram)},
        "valid_actions_by_environment": dict(sorted(by_environment.items())),
        "models": dict(sorted(models.items())),
        "usage": usage,
        "token_priced_cost_usd": token_priced_cost,
        "excluded_reasons": dict(sorted(errors.items())),
    }


def _write_report(
    path: Path,
    manifest: Mapping[str, object],
    honest: Mapping[str, object],
    attacks: Mapping[str, object],
) -> None:
    honest_summary = _required_mapping(honest, "summary")
    attack_summary = _required_mapping(attacks, "summary")
    cost_estimate = _required_mapping(manifest, "cost_estimate")
    totals = _required_mapping(manifest, "totals")
    honest_usage = _required_mapping(honest_summary, "usage")
    attack_usage = _required_mapping(attack_summary, "usage")
    total_input = _required_int(honest_usage, "input_tokens") + _required_int(
        attack_usage, "input_tokens"
    )
    total_output = _required_int(honest_usage, "output_tokens") + _required_int(
        attack_usage, "output_tokens"
    )
    total_cached = _required_int(honest_usage, "cached_input_tokens") + _required_int(
        attack_usage, "cached_input_tokens"
    )
    total_model_calls = _required_int(honest_usage, "model_calls") + _required_int(
        attack_usage, "model_calls"
    )
    attack_units = attacks.get("attack_unit_scores")
    if not isinstance(attack_units, list):
        raise ValueError("attack dataset is missing attack_unit_scores")
    attack_reconstructed_cost = max(
        0.0,
        _required_float(attack_summary, "token_priced_cost_usd")
        - PREEXISTING_ATTACK_SMOKE_COST_USD,
    )
    phase_b_total_cost = _required_float(honest_usage, "cost_usd") + attack_reconstructed_cost
    honest_estimate = _required_mapping(cost_estimate, "honest")
    attack_estimate = _required_mapping(cost_estimate, "attacks")
    estimated_honest = _required_int(totals, "estimated_honest_monitorable_actions")
    estimated_attacks = _required_int(totals, "estimated_attack_monitorable_actions")
    estimate_rows = "\n".join(
        (
            f"| Honest | {estimated_honest:,} | "
            f"${_required_float(honest_estimate, 'cost_usd'):.4f} |",
            f"| Attacks | {estimated_attacks:,} | "
            f"${_required_float(attack_estimate, 'cost_usd'):.4f} |",
            f"| Total | {estimated_honest + estimated_attacks:,} | "
            f"${_required_float(cost_estimate, 'total_cost_usd'):.4f} |",
        )
    )
    results_header = (
        "| Dataset | Raw actions | Valid scores | Ignored/excluded | "
        "Malformed/errored | Range | Unique | Fractional |"
    )
    result_rows = "\n".join(
        (
            _summary_row("Honest", honest_summary),
            _summary_row("Attacks", attack_summary),
        )
    )
    honest_environment_table = _mapping_table(
        _required_mapping(honest_summary, "valid_actions_by_environment"),
        "Environment",
        "Actions",
    )
    usage_rows = "\n".join(
        (
            _usage_row(
                "Honest",
                honest_usage,
                billed_cost=_required_float(honest_usage, "cost_usd"),
            ),
            _usage_row("Attacks", attack_usage, billed_cost=attack_reconstructed_cost),
            (
                f"| Total | {total_model_calls:,} "
                f"| {total_input:,} | {total_output:,} | {total_cached:,} "
                f"| ${phase_b_total_cost:.6f} |"
            ),
        )
    )

    path.write_text(
        f"""# Multi Baseline Scoring Report

Generated: {date.today().isoformat()}

## Scope

- Monitor: `multi` with its default equal-weight aggregation
- Existing trajectories only; no trajectory generation or evaluation
- `--only-action --max-concurrent 2 --no-upload`
- Hawk jobs used: no
- Honest: {_required_int(honest_summary, "trajectory_count")} trajectories,
  {_required_int(honest_summary, "valid_action_count")} valid action scores
- Attacks: {_required_int(attack_summary, "trajectory_count")} trajectories,
  {_required_int(attack_summary, "valid_action_count")} valid action scores
- Successful attack units: {len(attack_units)}

The local vetted honest pool contains only
{_required_int(totals, "honest_trajectories")} trajectories and produced
{_required_int(honest_summary, "valid_action_count")} valid scores, below the requested
1,500-action target. No previously excluded attack-policy non-attempts were reintroduced.

## Preflight Estimate

| Dataset | Estimated valid actions | Estimated cost |
|---|---:|---:|
{estimate_rows}

The 50% contingency estimate was
${_required_float(cost_estimate, "total_cost_with_50pct_contingency_usd"):.4f}, below
the $10 execution gate.

## Results

{results_header}
|---|---:|---:|---:|---:|---:|---:|---:|
{result_rows}

## Score Histograms

### Honest action scores

{_histogram_table(honest_summary)}

### Attack action scores

{_histogram_table(attack_summary)}

## Environment Coverage

### Honest valid actions

{honest_environment_table}

### Attack trajectories and valid actions

{_attack_environment_table(attacks)}

## Usage and Cost

| Dataset | Model calls | Input tokens | Output tokens | Cached input tokens | Cost |
|---|---:|---:|---:|---:|---:|
{usage_rows}

Models: honest `{_format_mapping(_required_mapping(honest_summary, "models"))}`;
attacks `{_format_mapping(_required_mapping(attack_summary, "models"))}`.

The honest cost is the exact cost recorded by the completed Phase B command. The
initial attack command completed every scoreable action except one oversized action,
but was interrupted during an unlimited provider retry before it could print or save
its cost summary. Attack cost is therefore reconstructed from preserved `gpt-5-nano`
token usage at $0.05/M input, $0.005/M cached input, and $0.40/M output, less the
$0.002566 pre-existing attack smoke-test cache hit. Cache-only recovery commands
reported $0.00. The reconstructed attack cost is ${attack_reconstructed_cost:.6f};
combined Phase B cost is ${phase_b_total_cost:.6f}.

## Exclusions and Errors

Honest: {_format_mapping(_required_mapping(honest_summary, "excluded_reasons"))}.

Attacks: {_format_mapping(_required_mapping(attack_summary, "excluded_reasons"))}.

Errored monitor placeholders were excluded from all score arrays. The flat arrays were
validated against their per-trajectory records. `attack_unit_scores` contains only
successful attacks and uses one maximum valid action score per trajectory; variant-family
tags are retained for later deduplication.

Runtime warnings consisted of recovered response-format retries plus one persistent
OpenRouter `server_error` on attack `8ec6d5e3b73b45659d5b7cf888d1fee2`, action index
12. That action contained an approximately 186 KB notebook replacement with embedded
image data. It is explicitly recorded as a skipped monitor action and contributes no
score.

## Upload Status

Both commands used `--no-upload`. No upload or Hawk command was run.
""",
        encoding="utf-8",
    )


def _summary_row(label: str, summary: Mapping[str, object]) -> str:
    return (
        f"| {label} | {_required_int(summary, 'raw_action_count'):,} "
        f"| {_required_int(summary, 'valid_action_count'):,} "
        f"| {_required_int(summary, 'excluded_action_count'):,} "
        f"| {_required_int(summary, 'error_action_count'):,} "
        f"| {_required_float(summary, 'score_min'):g}-"
        f"{_required_float(summary, 'score_max'):g} "
        f"| {_required_int(summary, 'unique_score_count')} "
        f"| {_required_float(summary, 'fractional_score_rate'):.1%} |"
    )


def _usage_row(
    label: str, usage: Mapping[str, object], *, billed_cost: float
) -> str:
    return (
        f"| {label} | {_required_int(usage, 'model_calls'):,} "
        f"| {_required_int(usage, 'input_tokens'):,} "
        f"| {_required_int(usage, 'output_tokens'):,} "
        f"| {_required_int(usage, 'cached_input_tokens'):,} "
        f"| ${billed_cost:.6f} |"
    )


def _histogram_table(summary: Mapping[str, object]) -> str:
    histogram = _required_mapping(summary, "score_histogram")
    rows = ["| Score | Count |", "|---:|---:|"]
    rows.extend(f"| {score} | {count} |" for score, count in histogram.items())
    return "\n".join(rows)


def _mapping_table(mapping: Mapping[str, object], left: str, right: str) -> str:
    rows = [f"| {left} | {right} |", "|---|---:|"]
    rows.extend(f"| {key} | {value} |" for key, value in mapping.items())
    return "\n".join(rows)


def _attack_environment_table(attacks: Mapping[str, object]) -> str:
    trajectories = attacks.get("trajectories")
    if not isinstance(trajectories, list):
        raise ValueError("attack trajectories must be a list")
    counts: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    for value in trajectories:
        record = _as_mapping(value, Path("<dataset>"))
        environment = _required_str(record, "environment")
        counts[environment] += 1
        actions[environment] += _required_int(record, "valid_action_count")
    rows = ["| Environment | Trajectories | Valid actions |", "|---|---:|---:|"]
    rows.extend(f"| {env} | {counts[env]} | {actions[env]} |" for env in sorted(counts))
    return "\n".join(rows)


def _validate_expected_ids(
    manifest: Mapping[str, object],
    honest: Mapping[str, object],
    attacks: Mapping[str, object],
) -> None:
    for manifest_key, payload in (("honest", honest), ("attacks", attacks)):
        expected_values = manifest.get(manifest_key)
        actual_values = payload.get("trajectories")
        if not isinstance(expected_values, list) or not isinstance(actual_values, list):
            raise ValueError("manifest and dataset trajectory lists are required")
        expected = {
            _required_str(_as_mapping(value, Path("<manifest>")), "trajectory_id")
            for value in expected_values
        }
        actual = {
            _required_str(_as_mapping(value, Path("<dataset>")), "trajectory_id")
            for value in actual_values
        }
        if expected != actual:
            raise ValueError(
                f"{manifest_key} scored IDs do not match manifest: "
                f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
            )


def _estimated_usage(
    score_count: int, per_score: Mapping[str, float], cost_per_score: float
) -> Usage:
    return {
        "model_calls": 2 * score_count,
        "input_tokens": round(score_count * per_score["input_tokens"]),
        "output_tokens": round(score_count * per_score["output_tokens"]),
        "cached_input_tokens": round(score_count * per_score["cached_input_tokens"]),
        "cost_usd": score_count * cost_per_score,
    }


def _gpt_5_nano_token_cost(usage: Usage) -> float:
    return (
        usage["input_tokens"] * GPT_5_NANO_INPUT_COST_PER_TOKEN
        + usage["output_tokens"] * GPT_5_NANO_OUTPUT_COST_PER_TOKEN
        + usage["cached_input_tokens"] * GPT_5_NANO_CACHED_INPUT_COST_PER_TOKEN
    )


def _variant_family(document: Mapping[str, object], trajectory_id: str) -> str:
    tags = document.get("tags")
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and tag.startswith("variant-of-"):
                return tag
    return trajectory_id


def _environment(document: Mapping[str, object]) -> str:
    environment = document.get("environment")
    if isinstance(environment, Mapping):
        return _optional_str(environment.get("id"), default="unknown")
    return _optional_str(environment, default="unknown")


def _action_index(action: Mapping[str, object], fallback: int) -> int:
    value = action.get("index")
    return value if isinstance(value, int) and not isinstance(value, bool) else fallback


def _is_by_design_skip(reason: str) -> bool:
    return (
        reason in {'"submit" tool calls are ignored', '"run_side_task_test" tool calls are ignored'}
        or reason == '"side_task_scorer" tool calls are ignored'
        or reason == "malformed action (parsing error)"
        or reason == "policy-private tool call"
    )


def _first_string(
    mapping: Mapping[str, object], keys: tuple[str, ...], *, default: str
) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value:
            return value
    return default


def _load_document(path: Path) -> dict[str, object]:
    value = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{path}: expected a JSON object")
    return cast(dict[str, object], value)


def _as_mapping(value: object, path: Path) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{path}: expected an object")
    return cast(Mapping[str, object], value)


def _string_mapping(value: Mapping[object, object], path: Path) -> Mapping[str, object]:
    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{path}: expected string object keys")
    return cast(Mapping[str, object], value)


def _optional_mapping(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        return cast(Mapping[str, object], value)
    return {}


def _required_mapping(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{key} must be an object")
    return _string_mapping(value, Path("<dataset>"))


def _required_str(mapping: Mapping[str, object], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _required_int(mapping: Mapping[str, object], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_float(mapping: Mapping[str, object], key: str) -> float:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def _optional_str(value: object, *, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _optional_int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _optional_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return 0.0
    return float(value)


def _empty_usage() -> Usage:
    return {
        "model_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cached_input_tokens": 0,
        "cost_usd": 0.0,
    }


def _add_usage(total: Usage, addition: Usage) -> None:
    total["model_calls"] += addition["model_calls"]
    total["input_tokens"] += addition["input_tokens"]
    total["output_tokens"] += addition["output_tokens"]
    total["cached_input_tokens"] += addition["cached_input_tokens"]
    total["cost_usd"] += addition["cost_usd"]


def _format_mapping(mapping: Mapping[str, object]) -> str:
    return ", ".join(f"{key}: {value}" for key, value in mapping.items()) or "none"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
