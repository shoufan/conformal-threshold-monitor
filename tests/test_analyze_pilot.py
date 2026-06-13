import numpy as np

from scripts.analyze_pilot import _threshold_results


def test_pilot_threshold_results_use_inclusive_tail_rule() -> None:
    honest = np.array([0] * 95 + [4] * 4 + [6], dtype=float)
    attacks = np.array([3, 4, 6, 7], dtype=float)

    results = _threshold_results(honest, attacks, delta=0.1)
    by_key = {(result.method, result.target_fpr): result for result in results}

    assert by_key[("Empirical", 0.05)].threshold == 4
    assert by_key[("Empirical", 0.05)].observed_fpr == 0.05
    assert by_key[("Empirical", 0.05)].attack_detection == 3 / 4
    assert np.isinf(by_key[("Certified", 0.01)].threshold)
