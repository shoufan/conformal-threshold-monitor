import pytest

from scripts.analyze_ensemble import (
    ComponentRecord,
    Normalization,
    add_candidate_scores,
    candidate_scores,
    honest_normalization,
)


def test_candidate_scores_match_predeclared_rules() -> None:
    normalization = Normalization(
        means={"orthogonal": 1.0, "old_action": 2.0, "goal_analysis": 3.0},
        standard_deviations={"orthogonal": 1.0, "old_action": 2.0, "goal_analysis": 4.0},
    )

    scores = candidate_scores(3.0, 4.0, 7.0, normalization)

    assert scores["multi_baseline"] == 3.5
    assert scores["mean3"] == pytest.approx(14 / 3)
    assert scores["max3"] == 7.0
    assert scores["zmean3"] == pytest.approx((2.0 + 1.0 + 1.0) / 3)


def test_zmean_normalization_uses_honest_records_only() -> None:
    honest = [
        _record(orthogonal=0.0, old_action=1.0, goal=2.0),
        _record(orthogonal=2.0, old_action=3.0, goal=6.0, index=1),
    ]
    normalization = honest_normalization(honest)

    assert normalization.means == {
        "orthogonal": 1.0,
        "old_action": 2.0,
        "goal_analysis": 4.0,
    }
    assert normalization.standard_deviations == {
        "orthogonal": 1.0,
        "old_action": 1.0,
        "goal_analysis": 2.0,
    }


def test_reconstructed_multi_must_match_stored_parent() -> None:
    record = _record(orthogonal=0.0, old_action=2.0, goal=3.0, stored_multi=0.0)
    normalization = Normalization(
        means={"orthogonal": 0.0, "old_action": 0.0, "goal_analysis": 0.0},
        standard_deviations={"orthogonal": 1.0, "old_action": 1.0, "goal_analysis": 1.0},
    )

    with pytest.raises(ValueError, match="reconstructed multi score mismatch"):
        add_candidate_scores([record], normalization)


def _record(
    *,
    orthogonal: float,
    old_action: float,
    goal: float,
    stored_multi: float | None = None,
    index: int = 0,
) -> ComponentRecord:
    return ComponentRecord(
        trajectory_id="trajectory",
        environment="media_processing",
        action_index=index,
        tool_call_id=f"call-{index}",
        function="bash",
        orthogonal_score=orthogonal,
        old_action_score=old_action,
        goal_analysis_score=goal,
        stored_multi_score=(
            (orthogonal + old_action) / 2 if stored_multi is None else stored_multi
        ),
        orthogonal_cost_usd=0.0,
        old_action_cost_usd=0.0,
        goal_analysis_cost_usd=0.0,
    )
