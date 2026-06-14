from scripts.analyze_phase_k import filter_new_candidates, summarize_tail


def test_summarize_tail_reports_environment_and_trajectory_concentration() -> None:
    rows = [
        {"environment": "alpha", "trajectory_id": "a", "score": 5.0},
        {"environment": "alpha", "trajectory_id": "a", "score": 4.5},
        {"environment": "alpha", "trajectory_id": "b", "score": 4.5},
        {"environment": "beta", "trajectory_id": "c", "score": 4.0},
    ]

    summary = summarize_tail(rows, threshold=4.5)

    assert summary["flagged"] == 3
    assert summary["by_environment"] == {"alpha": 3}
    assert summary["contributing_trajectories"] == 2
    assert summary["largest_trajectory_tail_count"] == 2
    assert summary["largest_trajectory_tail_share"] == 2 / 3


def test_filter_new_candidates_applies_success_and_known_id_rules() -> None:
    rows = [
        {
            "trajectory_id": "new",
            "environment_id": "alpha",
            "main_task_success": True,
            "side_task_success": True,
            "error": None,
            "actions_count": 10,
        },
        {
            "trajectory_id": "known",
            "environment_id": "alpha",
            "main_task_success": True,
            "side_task_success": True,
            "error": None,
            "actions_count": 8,
        },
        {
            "trajectory_id": "failed-main",
            "environment_id": "alpha",
            "main_task_success": False,
            "side_task_success": True,
            "error": None,
            "actions_count": 9,
        },
    ]

    result = filter_new_candidates(
        rows,
        environment="alpha",
        lastraj_ids={"known"},
        frozen_ids=set(),
        local_ids={"known"},
    )

    assert [row["trajectory_id"] for row in result["new_rows"]] == ["new"]
    assert result["valid_dual_success_count"] == 2
    assert result["excluded_lastraj"] == 1
    assert result["new_count"] == 1
