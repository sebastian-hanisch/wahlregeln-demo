"""Orakel (DEMO-PLAYBOOK §12): unabhängige Rechenwege für Regeln, exakte Wahrscheinlichkeit und das Profilmodell.

(1) Neuimplementierung der Regeln mit einfachen Schleifen über Wähler und Kandidaten, auf zufälligen Profilen aller Modelle.
(2) Exakte Aufzählung ALLER 6^n Profile bei n = 3, 5 gegen die Wahrscheinlichkeit aus den Zusammensetzungen und gegen die Simulation.
(3) Mallows: Häufigkeit der sechs Rangfolgen gegen phi^(Fehlstände) / Z (Chi-Quadrat).
(4) Einspitzige Profile haben stets einen Condorcet-Sieger (Medianwähler).
"""

import itertools

import numpy as np
import pytest

import wrg_algorithm as A


def naive_pairwise(profile):
    n, m = profile.shape
    w = [[0] * m for _ in range(m)]
    for row in profile.tolist():
        for i in range(m):
            for j in range(i + 1, m):
                w[row[i]][row[j]] += 1                      # row[i] steht vor row[j]
    return w


def naive_pick(scores, tiebreak):
    best = max(scores)
    cands = [c for c, s in enumerate(scores) if s == best]
    return min(cands, key=lambda c: tiebreak[c])


def naive_irv(profile, tiebreak):
    m = profile.shape[1]
    alive = set(range(m))
    while len(alive) > 1:
        counts = {c: 0 for c in alive}
        for row in profile.tolist():
            for c in row:
                if c in alive:
                    counts[c] += 1
                    break
        low = min(counts.values())
        losers = [c for c in alive if counts[c] == low]
        alive.discard(max(losers, key=lambda c: tiebreak[c]))
    return next(iter(alive))


def naive_all(profile, tiebreak):
    n, m = profile.shape
    w = naive_pairwise(profile)
    plurality = [sum(1 for row in profile.tolist() if row[0] == c) for c in range(m)]
    borda = [sum(m - 1 - row.index(c) for row in profile.tolist()) for c in range(m)]
    copeland = [sum(1.0 if w[a][b] > w[b][a] else (0.5 if w[a][b] == w[b][a] else 0.0) for b in range(m) if b != a) for a in range(m)]
    cw = next((a for a in range(m) if all(w[a][b] > w[b][a] for b in range(m) if b != a)), None)
    cl = next((a for a in range(m) if all(w[a][b] < w[b][a] for b in range(m) if b != a)), None)
    return {"plurality": plurality, "borda": borda, "copeland": copeland, "w": w,
            "winners": {"plurality": naive_pick(plurality, tiebreak), "borda": naive_pick(borda, tiebreak), "copeland": naive_pick(copeland, tiebreak), "irv": naive_irv(profile, tiebreak)},
            "cw": cw, "cl": cl}


@pytest.mark.parametrize("model", list(A.PROFILE_MODELS))
def test_rules_match_the_naive_reimplementation_on_random_profiles(model):
    rng = np.random.default_rng(100)
    for t in range(80):
        m = int(rng.integers(2, 7))
        n = int(rng.integers(1, 40))
        profile = A.PROFILE_MODELS[model](n, m, rng)
        tiebreak = rng.permutation(m)
        o = A.evaluate(profile, tiebreak)
        ref = naive_all(profile, tiebreak)
        assert o.margins.tolist() == ref["w"], (model, t)
        assert o.plurality.tolist() == ref["plurality"] and o.borda.tolist() == ref["borda"] and o.copeland.tolist() == ref["copeland"], (model, t)
        assert o.winners == ref["winners"], (model, t)
        assert o.condorcet == ref["cw"] and o.loser == ref["cl"], (model, t)


def test_invariants_of_the_scores():
    rng = np.random.default_rng(101)
    for _ in range(100):
        m, n = int(rng.integers(2, 7)), int(rng.integers(1, 60))
        o = A.evaluate(A.profile_random(n, m, rng), rng.permutation(m))
        assert o.plurality.sum() == n and o.borda.sum() == n * m * (m - 1) // 2 and o.copeland.sum() == m * (m - 1) / 2
        assert ((o.margins + o.margins.T)[~np.eye(m, dtype=bool)] == n).all()
        assert o.irv_rounds[-1]["counts"].sum() == n                                    # in der letzten Runde hat der Sieger alle Stimmen


def test_a_condorcet_winner_is_unique_and_wins_copeland():
    rng = np.random.default_rng(102)
    found = 0
    for _ in range(300):
        m, n = int(rng.integers(3, 6)), 2 * int(rng.integers(1, 20)) + 1
        profile = A.profile_random(n, m, rng)
        o = A.evaluate(profile, rng.permutation(m))
        if o.condorcet is not None:
            found += 1
            assert o.winners["copeland"] == o.condorcet and o.copeland[o.condorcet] == m - 1
            assert sum(1 for a in range(m) if all(o.margins[a, b] > o.margins[b, a] for b in range(m) if b != a)) == 1
    assert found > 150


def enumerate_exact(n):
    """Anteil der 6^n Profile ohne Condorcet-Sieger (jede Wählerfolge einzeln, ohne Zusammensetzungen)."""
    perms = list(itertools.permutations(range(3)))
    ranks = [np.argsort(p) for p in perms]
    cycles = 0
    for combo in itertools.product(range(6), repeat=n):
        w = np.zeros((3, 3), dtype=int)
        for i in combo:
            rk = ranks[i]
            for a in range(3):
                for b in range(3):
                    if a != b and rk[a] < rk[b]:
                        w[a, b] += 1
        if A.condorcet_winner(w) is None:
            cycles += 1
    return cycles / 6 ** n


@pytest.mark.parametrize("n", [3, 5])
def test_exact_probability_matches_full_enumeration(n):
    assert A.exact_no_condorcet_probability(n) == pytest.approx(enumerate_exact(n), abs=1e-12)


@pytest.mark.parametrize("n", [3, 5, 9])
def test_simulation_matches_the_exact_probability(n):
    exact = A.exact_no_condorcet_probability(n)
    rng = np.random.default_rng(200 + n)
    runs = 6000
    hits = sum(A.condorcet_winner(A.pairwise(A.profile_random(n, 3, rng))) is None for _ in range(runs))
    sigma = (exact * (1 - exact) / runs) ** 0.5
    assert abs(hits / runs - exact) < 4 * sigma + 1e-9


def inversions(perm, base):
    pos = {c: i for i, c in enumerate(base)}
    seq = [pos[c] for c in perm]
    return sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])


def test_mallows_matches_phi_to_the_number_of_inversions():
    phi, n = 0.6, 60000
    rng = np.random.default_rng(300)
    p = A.mallows_profile(n, [0, 1, 2], phi, rng)
    perms = list(itertools.permutations(range(3)))
    weights = np.array([phi ** inversions(q, [0, 1, 2]) for q in perms])
    expected = weights / weights.sum() * n
    counts = {q: 0 for q in perms}
    for row in p.tolist():
        counts[tuple(row)] += 1
    chi2 = sum((counts[q] - e) ** 2 / e for q, e in zip(perms, expected))
    assert chi2 < 20.5                                    # 5 Freiheitsgrade, p = 0,001


def test_mallows_with_a_reversed_base_is_the_mirror_image():
    phi = 0.5
    rng = np.random.default_rng(301)
    p = A.mallows_profile(30000, [2, 1, 0], phi, rng)
    base_freq = np.mean([row == [2, 1, 0] for row in p.tolist()])
    z = 1 * (1 + phi) * (1 + phi + phi ** 2)
    assert base_freq == pytest.approx(1 / z, abs=0.012)


def test_single_peaked_profiles_always_have_a_condorcet_winner():
    rng = np.random.default_rng(400)
    for _ in range(400):
        m, n = int(rng.integers(3, 7)), 2 * int(rng.integers(1, 40)) + 1
        profile = A.profile_single_peaked(n, m, rng)
        assert A.condorcet_winner(A.pairwise(profile)) is not None


def test_single_peaked_condorcet_winner_is_the_candidate_nearest_the_median_ideal_point():
    for seed in range(40):
        rng = np.random.default_rng(seed)
        n, m = 51, 5
        ideal = np.random.default_rng(seed).random(n) * m - 0.5            # dieselbe Ziehung wie in profile_single_peaked (erste Ziehung des Generators)
        profile = A.profile_single_peaked(n, m, np.random.default_rng(seed))
        cw = A.condorcet_winner(A.pairwise(profile))
        median = np.median(ideal)
        assert cw == int(np.argmin(np.abs(median - np.arange(m))))
