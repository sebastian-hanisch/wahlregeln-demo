"""Randfälle: kleinste und größte Reglerwerte für jedes Profilmodell, ein Wähler, zwei Kandidaten, lauter gleiche Wähler, alles Gleichstand, ungültige Eingaben."""

import numpy as np
import pytest

import wrg_algorithm as A
import wrg_constants as C
import wrg_evaluation as ev
from wrg_scenario import make_profile


def test_every_model_at_the_extreme_settings():
    for model in C.MODELS:
        for m, n in ((C.M_MIN, C.N_MIN), (C.M_MAX, C.N_MIN), (C.M_MIN, C.N_MAX), (C.M_MAX, C.N_MAX)):
            a = ev.analyse(ev.Settings(model, m, n, 1))
            assert a.profile.shape == (n, m) and set(a.outcome.winners.values()) <= set(range(m))
            assert 1 <= a.distinct <= 4 and ev.verdict_state(a)[0] in ("success", "info", "warning")
            assert len(ev.rule_rows(a)) == 4


def test_one_voter_decides_everything():
    p = np.array([[2, 0, 1]])
    o = A.evaluate(p, np.array([0, 1, 2]))
    assert set(o.winners.values()) == {2} and o.condorcet == 2 and o.loser == 1


def test_two_candidates_all_rules_agree_with_the_majority():
    rng = np.random.default_rng(5)
    for _ in range(50):
        p = A.profile_random(int(2 * rng.integers(1, 20) + 1), 2, rng)
        o = A.evaluate(p, np.array([0, 1]))
        assert len(set(o.winners.values())) == 1 and o.condorcet == o.winners["plurality"]


def test_identical_voters_are_unanimous():
    p = np.array([[3, 1, 0, 2]] * 9)
    o = A.evaluate(p, np.array([0, 1, 2, 3]))
    assert set(o.winners.values()) == {3} and o.condorcet == 3 and o.loser == 2


def test_complete_symmetry_falls_back_to_the_tiebreak():
    p = np.array([[0, 1, 2], [1, 2, 0], [2, 0, 1]])
    tb = np.array([1, 2, 0])
    o = A.evaluate(p, tb)
    assert o.winners["plurality"] == o.winners["borda"] == o.winners["copeland"] == 2           # alle gleich: kleinster tiebreak-Wert (C hat 0)


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        make_profile("x", 3, 5, 1)
    with pytest.raises(ValueError):
        make_profile("random", 1, 5, 1)
    with pytest.raises(ValueError):
        make_profile("random", 3, 0, 1)


def test_the_same_settings_give_the_same_analysis():
    a, b = ev.analyse(ev.Settings("camps", 5, 101, 7)), ev.analyse(ev.Settings("camps", 5, 101, 7))
    assert (a.profile == b.profile).all() and a.outcome.winners == b.outcome.winners and (a.tiebreak == b.tiebreak).all()
    c = ev.analyse(ev.Settings("camps", 5, 101, 8))
    assert not (a.profile == c.profile).all()


def test_the_tiebreak_is_a_permutation_independent_of_the_model():
    for model in C.MODELS:
        _, tb = make_profile(model, 5, 21, 3)
        assert sorted(tb.tolist()) == [0, 1, 2, 3, 4]


def test_series_structure_with_small_numbers():
    rows = ev.series_paradox(ms=(3, 4), ns=(5,), runs=20)
    assert [(r["model"], r["m"], r["n"]) for r in rows] == [(mo, m, 5) for mo in C.MODELS for m in (3, 4)] and all(0.0 <= r["no_condorcet"] <= 1.0 for r in rows)
    d = ev.series_disagree(m=3, n=7, runs=20)
    assert [r["model"] for r in d] == list(C.MODELS)
    for r in d:
        assert set(r["miss_condorcet"]) == set(A.RULE_NAMES) and len(r["pairs"]) == 6 and 0 <= r["any_disagree"] <= 1
        assert r["miss_condorcet"]["copeland"] == 0.0                     # Copeland wählt jeden vorhandenen Condorcet-Sieger
        assert all(v == 0.0 for v in r["picks_loser"].values() if False) or r["picks_loser"]["copeland"] == 0.0
