from __future__ import annotations

import math

from monitor_cert.zmean3 import (
    CONTROL_TOWER_OFFSET,
    CONTROL_TOWER_SCALE,
    RAW_MAX,
    RAW_MIN,
    control_tower_zmean3,
    decode_control_tower_score,
    encode_control_tower_score,
    raw_zmean3,
)


def test_frozen_means_map_to_zero_raw_score() -> None:
    raw = raw_zmean3(0.500251, 0.801911, 1.453997)
    assert math.isclose(raw, 0.0, abs_tol=1e-12)


def test_control_tower_encoding_spans_component_domain() -> None:
    assert math.isclose(encode_control_tower_score(RAW_MIN), 0.0, abs_tol=1e-12)
    assert math.isclose(encode_control_tower_score(RAW_MAX), 10.0, abs_tol=1e-12)
    assert CONTROL_TOWER_SCALE > 0
    assert CONTROL_TOWER_OFFSET > 0


def test_control_tower_encoding_round_trips_and_preserves_order() -> None:
    raw_scores = [-0.6, 0.0, 2.36926, 2.636413679185227, 6.407]
    encoded = [encode_control_tower_score(score) for score in raw_scores]
    assert encoded == sorted(encoded)
    for raw, transported in zip(raw_scores, encoded, strict=True):
        assert math.isclose(decode_control_tower_score(transported), raw, abs_tol=1e-12)


def test_combined_helper_matches_raw_then_encode() -> None:
    raw = raw_zmean3(6.0, 4.0, 7.0)
    encoded = control_tower_zmean3(6.0, 4.0, 7.0)
    assert math.isclose(encoded, encode_control_tower_score(raw), abs_tol=1e-12)
