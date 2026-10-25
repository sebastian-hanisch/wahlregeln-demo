"""Befunde der README als Bänder: jede Zahl, die dort steht, ist hier an den festen Plänen der App geprüft (Seeds und Profile wie in messen.py).

Bänder statt Punktwerte: die Zufallszahlen eines numpy-Generators sind nicht über Versionen stabil. Je Zelle 400 Profile: die Standardabweichung eines Anteils
liegt bei höchstens 2,5 Prozentpunkten, die Bänder sind deshalb mindestens ±6 Punkte breit. Exakte Wahrscheinlichkeiten und Sätze stehen ohne Band.
"""

import pytest

import wrg_algorithm as A
import wrg_constants as C
import wrg_evaluation as ev


@pytest.fixture(scope="module")
def paradox():
    return {(r["model"], r["m"], r["n"]): r["no_condorcet"] for r in ev.series_paradox()}


@pytest.fixture(scope="module")
def disagree():
    return {r["model"]: r for r in ev.series_disagree()}


def test_exact_probabilities_without_a_condorcet_winner_for_three_candidates():
    exact = {n: A.exact_no_condorcet_probability(n) for n in (3, 5, 11, 21)}
    assert exact[3] == pytest.approx(0.05556, abs=1e-4) and exact[5] == pytest.approx(0.06944, abs=1e-4)
    assert exact[11] == pytest.approx(0.07981, abs=1e-4) and exact[21] == pytest.approx(0.08365, abs=1e-4)
    assert exact[3] < exact[5] < exact[11] < exact[21] < 0.0877                                  # steigt mit der Wählerzahl auf etwa 8,8 % (Grenzwert aus dem Gedächtnis, nicht geprüft)


def test_the_paradox_grows_with_the_number_of_candidates_under_random_profiles(paradox):
    at_51 = [paradox[("random", m, 51)] for m in (3, 4, 5, 6)]
    assert at_51 == sorted(at_51) and at_51[0] == pytest.approx(0.082, abs=0.06) and at_51[-1] == pytest.approx(0.318, abs=0.08)
    assert paradox[("random", 5, 201)] == pytest.approx(0.287, abs=0.08)


def test_the_simulated_paradox_matches_the_exact_value_for_three_candidates(paradox):
    assert paradox[("random", 3, 11)] == pytest.approx(A.exact_no_condorcet_probability(11), abs=0.04)


def test_single_peaked_profiles_never_have_a_cycle(paradox):
    assert all(v == 0.0 for (model, _, _), v in paradox.items() if model == "single") and len([1 for k in paradox if k[0] == "single"]) == 12


def test_two_camps_have_cycles_that_depend_on_the_number_of_voters(paradox):
    assert paradox[("camps", 4, 11)] == pytest.approx(0.222, abs=0.08) and paradox[("camps", 4, 201)] == pytest.approx(0.148, abs=0.07)
    assert paradox[("camps", 6, 201)] == pytest.approx(0.298, abs=0.08)


def test_rules_disagree_in_about_half_of_the_profiles(disagree):
    assert disagree["random"]["any_disagree"] == pytest.approx(0.468, abs=0.07)
    assert disagree["single"]["any_disagree"] == pytest.approx(0.61, abs=0.07)
    assert disagree["camps"]["any_disagree"] == pytest.approx(0.425, abs=0.07)


def test_copeland_always_picks_an_existing_condorcet_winner_and_borda_irv_never_pick_the_loser(disagree):
    for model, r in disagree.items():
        assert r["miss_condorcet"]["copeland"] == 0.0, model
        assert r["picks_loser"]["borda"] == r["picks_loser"]["copeland"] == r["picks_loser"]["irv"] == 0.0, model


def test_plurality_misses_the_condorcet_winner_most_often(disagree):
    assert disagree["random"]["miss_condorcet"]["plurality"] == pytest.approx(0.297, abs=0.07)
    assert disagree["single"]["miss_condorcet"]["plurality"] == pytest.approx(0.595, abs=0.07)
    for model in C.MODELS:
        miss = disagree[model]["miss_condorcet"]
        assert miss["plurality"] > miss["irv"] > miss["copeland"] and miss["plurality"] > miss["borda"] > miss["copeland"]


def test_single_peaked_profiles_make_the_sofortstichwahl_miss_the_median_candidate_more_often(disagree):
    assert disagree["single"]["miss_condorcet"]["irv"] == pytest.approx(0.385, abs=0.07) and disagree["random"]["miss_condorcet"]["irv"] == pytest.approx(0.069, abs=0.05)
    assert disagree["single"]["miss_condorcet"]["borda"] == pytest.approx(0.112, abs=0.06)


def test_plurality_picks_the_condorcet_loser_sometimes(disagree):
    assert disagree["single"]["picks_loser"]["plurality"] == pytest.approx(0.065, abs=0.04) and disagree["random"]["picks_loser"]["plurality"] == pytest.approx(0.018, abs=0.025)
    assert disagree["single"]["picks_loser"]["plurality"] > disagree["random"]["picks_loser"]["plurality"]


def test_the_share_of_profiles_with_a_condorcet_winner(disagree):
    assert disagree["single"]["share_with_condorcet"] == 1.0
    assert disagree["random"]["share_with_condorcet"] == pytest.approx(0.80, abs=0.07) and disagree["camps"]["share_with_condorcet"] == pytest.approx(0.838, abs=0.07)


def test_the_presets_tell_the_stories_in_their_help_texts():
    d = ev.analyse(ev.Settings(**C.PRESETS["Zufall, drei Kandidaten"]))
    assert d.outcome.condorcet == 1 and d.outcome.winners == {"plurality": 2, "borda": 2, "copeland": 1, "irv": 1}
    many = ev.analyse(ev.Settings(**C.PRESETS["Viele Kandidaten, viele Wähler"]))
    assert many.distinct == 3 and many.outcome.condorcet == 2
    camps = ev.analyse(ev.Settings(**C.PRESETS["Zwei Lager: der Kompromiss"]))
    assert camps.outcome.winners == {"plurality": 0, "borda": 1, "copeland": 1, "irv": 1}
