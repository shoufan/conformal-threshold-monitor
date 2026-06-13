from __future__ import annotations

import math

import numpy as np

from scripts.analyze_official_metrics import histogram_summary, summarize_distribution


def test_summarize_distribution_reports_percentiles_and_granularity() -> None:
    summary = summarize_distribution(np.asarray([0.0, 0.5, 0.5, 1.0]))
    assert summary["count"] == 4
    assert summary["min"] == 0.0
    assert summary["p50"] == 0.5
    assert summary["max"] == 1.0
    assert summary["unique_scores"] == 3
    assert summary["smallest_positive_step"] == 0.5


def test_histogram_summary_preserves_population_counts() -> None:
    rows = histogram_summary(
        np.asarray([0.0, 0.5, 1.0]),
        np.asarray([0.25, 0.75]),
        bins=4,
    )
    assert sum(int(row["honest_count"]) for row in rows) == 3
    assert sum(int(row["attack_count"]) for row in rows) == 2
    assert math.isclose(float(rows[0]["lower"]), 0.0)
    assert math.isclose(float(rows[-1]["upper"]), 1.0)
