"""Tests for the cluster-robust certification analysis."""

from __future__ import annotations

import math

import numpy as np

from monitor_cert.thresholds import certified_threshold, cp_upper
from scripts.analyze_cluster_robust import (
    ClusteredScores,
    adjusted_certified_threshold,
    cluster_bootstrap_upper,
    cp_upper_continuous,
    deff_adjusted_cp,
    design_effect,
    icc_oneway,
    tail_indicator_icc,
    trajectory_level_section,
)


def _scores(trajectory_ids: list[str], values: list[float]) -> ClusteredScores:
    return ClusteredScores("test", tuple(trajectory_ids), np.asarray(values, dtype=np.float64))


def test_icc_near_one_for_perfectly_clustered_values() -> None:
    trajectory_ids = ["a"] * 10 + ["b"] * 10 + ["c"] * 10
    values = [1.0] * 10 + [5.0] * 10 + [9.0] * 10
    result = icc_oneway(np.asarray(values, dtype=np.float64), tuple(trajectory_ids))
    assert result.icc > 0.99
    assert result.n_clusters == 3
    assert math.isclose(result.mean_cluster_size, 10.0)


def test_icc_degenerate_constant_values_maps_to_zero() -> None:
    trajectory_ids = ["a"] * 5 + ["b"] * 5
    values = [2.0] * 10
    result = icc_oneway(np.asarray(values, dtype=np.float64), tuple(trajectory_ids))
    assert result.icc == 0.0
    assert design_effect(result.icc, result.mean_cluster_size) == 1.0


def test_design_effect_floors_negative_icc_at_one() -> None:
    assert design_effect(-0.2, 50.0) == 1.0
    assert design_effect(0.1, 11.0) == 2.0


def test_cp_upper_continuous_matches_integer_cp() -> None:
    for k, n, delta in [(0, 230, 0.10), (15, 2007, 0.10), (8, 2007, 0.01)]:
        assert math.isclose(cp_upper_continuous(k, n, delta), cp_upper(k, n, delta), rel_tol=1e-12)


def test_deff_adjusted_cp_reduces_to_naive_at_deff_one() -> None:
    assert math.isclose(deff_adjusted_cp(15, 2007, 1.0, 0.10), cp_upper(15, 2007, 0.10))


def test_deff_adjusted_cp_is_wider_for_deff_above_one() -> None:
    assert deff_adjusted_cp(15, 2007, 2.0, 0.10) > cp_upper(15, 2007, 0.10)


def test_adjusted_scan_matches_naive_when_flags_are_unclustered() -> None:
    # One flag-worthy score in each of many clusters: indicator ICC <= 0 -> DEFF = 1.
    rng = np.random.default_rng(7)
    trajectory_ids: list[str] = []
    values: list[float] = []
    for cluster in range(40):
        trajectory_ids.extend([f"t{cluster}"] * 25)
        base = rng.normal(2.0, 1.0, size=25)
        values.extend(float(v) for v in base)
    scores = _scores(trajectory_ids, values)
    naive = certified_threshold(scores.scores, alpha=0.01, delta=0.10)
    indicator = tail_indicator_icc(scores, naive)
    if indicator.icc <= 0.0:
        assert adjusted_certified_threshold(scores, delta=0.10) == naive
    else:
        assert adjusted_certified_threshold(scores, delta=0.10) >= naive


def test_adjusted_scan_never_more_permissive_than_naive() -> None:
    rng = np.random.default_rng(11)
    trajectory_ids: list[str] = []
    values: list[float] = []
    for cluster in range(27):
        trajectory_ids.extend([f"t{cluster}"] * 70)
        shift = rng.normal(0.0, 0.8)
        values.extend(float(v) for v in rng.normal(2.0 + shift, 1.0, size=70))
    scores = _scores(trajectory_ids, values)
    naive = certified_threshold(scores.scores, alpha=0.01, delta=0.10)
    assert adjusted_certified_threshold(scores, delta=0.10) >= naive


def test_cluster_bootstrap_is_seeded_and_ordered() -> None:
    trajectory_ids = [f"t{i}" for i in range(10) for _ in range(20)]
    rng = np.random.default_rng(3)
    values = [float(v) for v in rng.normal(0.0, 1.0, size=200)]
    scores = _scores(trajectory_ids, values)
    threshold = float(np.quantile(scores.scores, 0.98))
    first = cluster_bootstrap_upper(scores, threshold, reps=500, seed=42)
    second = cluster_bootstrap_upper(scores, threshold, reps=500, seed=42)
    assert first == second
    assert first["upper_90"] <= first["upper_95"] <= first["upper_99"]
    assert 0.0 <= first["zero_flag_rep_share"] <= 1.0


def test_trajectory_level_zero_flag_bound_sanity() -> None:
    trajectory_ids = [f"t{i}" for i in range(27) for _ in range(10)]
    values = [0.0] * 270
    scores = _scores(trajectory_ids, values)
    section = trajectory_level_section(scores, threshold=5.0)
    assert section["flagged_trajectories"] == 0
    assert math.isclose(
        section["zero_flag_cp_upper"]["delta_0.1"], 1.0 - 0.10 ** (1.0 / 27.0), rel_tol=1e-12
    )
    assert section["min_trajectories_to_certify_1pct"]["delta_0.1"] == 230
    assert section["min_trajectories_to_certify_1pct"]["delta_0.05"] == 299
    assert section["min_trajectories_to_certify_1pct"]["delta_0.01"] == 459
