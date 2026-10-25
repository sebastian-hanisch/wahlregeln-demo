"""Kern von Hand: jede Einheit an den Mini-Profilen aus conftest.py, mit der Rechnung im Kommentar."""

import numpy as np
import pytest

import wrg_algorithm as A

TB_ID = np.array([0, 1, 2])           # Gleichstand: A vor B vor C
TB_REV = np.array([2, 1, 0])          # Gleichstand: C vor B vor A


def test_ranks_of_inverts_the_profile(seven):
    r = A.ranks_of(seven)
    assert r.tolist()[0] == [0, 1, 2] and r.tolist()[3] == [2, 0, 1] and r.tolist()[5] == [2, 1, 0]      # B>C>A: A auf Platz 2, B auf 0, C auf 1
    for v in range(len(seven)):
        assert all(r[v, seven[v, k]] == k for k in range(3))


def test_pairwise_counts_by_hand(seven, cycle):
    w = A.pairwise(seven)
    assert w.tolist() == [[0, 3, 3], [4, 0, 5], [4, 2, 0]]
    assert (w + w.T)[0, 1] == 7 and np.trace(w) == 0
    c = A.pairwise(cycle)
    assert c.tolist() == [[0, 2, 1], [1, 0, 2], [2, 1, 0]]


def test_plurality_borda_copeland_by_hand(seven):
    assert A.plurality_counts(seven).tolist() == [3, 2, 2]
    assert A.borda_scores(seven).tolist() == [6, 9, 6]
    assert A.copeland_scores(A.pairwise(seven)).tolist() == [0.0, 2.0, 1.0]


def test_copeland_counts_ties_as_half():
    w = np.array([[0, 2, 2], [2, 0, 3], [2, 1, 0]])          # A:B gleich (2:2), A:C gleich (2:2), B schlägt C
    assert A.copeland_scores(w).tolist() == [1.0, 1.5, 0.5]       # A: 0 Siege + 2 Gleichstände = 1; B: 1 Sieg + 1 Gleichstand = 1,5; C: 0 Siege + 1 Gleichstand (gegen A) = 0,5


def test_condorcet_winner_and_loser(seven, cycle, loser_wins):
    assert A.condorcet_winner(A.pairwise(seven)) == 1 and A.condorcet_loser(A.pairwise(seven)) == 0
    assert A.condorcet_winner(A.pairwise(cycle)) is None and A.condorcet_loser(A.pairwise(cycle)) is None
    assert A.condorcet_winner(A.pairwise(loser_wins)) == 1 and A.condorcet_loser(A.pairwise(loser_wins)) == 0


def test_pick_breaks_ties_by_the_tiebreak_order():
    assert A.pick(np.array([3, 5, 5]), TB_ID) == 1 and A.pick(np.array([3, 5, 5]), TB_REV) == 2
    assert A.pick(np.array([1, 0, 0]), TB_REV) == 0


def test_irv_by_hand_with_both_tiebreaks(seven):
    # Erststimmen A 3, B 2, C 2: B und C liegen gleich hinten.
    winner, rounds = A.irv(seven, TB_REV)
    # Kleinerer tiebreak-Wert = bevorzugt. Unter den Letzten B (Wert 1) und C (Wert 0) scheidet der Kandidat mit dem größten Wert aus: B.
    # B's 2 Wähler (B>C>A) gehen an C: C 4, A 3, dann scheidet A aus, A's 3 Wähler (A>B>C) gehen an C (B ist weg): C gewinnt mit 7.
    assert winner == 2 and [r["out"] for r in rounds] == [1, 0, None]
    assert rounds[0]["counts"].tolist() == [3, 2, 2] and rounds[1]["counts"].tolist() == [3, 0, 4] and rounds[2]["counts"].tolist() == [0, 0, 7]
    winner, rounds = A.irv(seven, TB_ID)                   # jetzt scheidet C aus (tiebreak 2 ist größer als 1): C's 2 Wähler (C>B>A) gehen an B: B 4, A 3; A scheidet aus; B gewinnt mit 7
    assert winner == 1 and [r["out"] for r in rounds] == [2, 0, None] and rounds[1]["counts"].tolist() == [3, 4, 0]


def test_irv_with_a_single_candidate_left_needs_no_round_of_elimination():
    winner, rounds = A.irv(np.array([[0], [0]]), np.array([0]))
    assert winner == 0 and len(rounds) == 1 and rounds[0]["out"] is None


def test_evaluate_collects_everything(seven, loser_wins):
    o = A.evaluate(seven, TB_ID)
    assert o.winners == {"plurality": 0, "borda": 1, "copeland": 1, "irv": 1} and o.condorcet == 1 and o.loser == 0
    o = A.evaluate(loser_wins, TB_ID)
    assert o.winners["plurality"] == 0 and o.loser == 0 and o.winners["plurality"] == o.loser               # die Mehrheitswahl wählt den Condorcet-Verlierer
    # Borda A 8, B 13, C 9; Copeland B 2; Sofortstichwahl: C scheidet aus (Gleichstand mit B, C hat den größeren tiebreak-Wert), B gewinnt
    assert o.winners["borda"] == 1 and o.winners["copeland"] == 1 and o.winners["irv"] == 1 and o.borda.tolist() == [8, 13, 9]


def test_mallows_with_phi_zero_is_the_base_order_and_with_phi_one_is_uniform():
    rng = np.random.default_rng(1)
    p0 = A.mallows_profile(50, [2, 0, 1], 1e-12, rng)
    assert (p0 == np.array([2, 0, 1])[None, :]).all()
    p1 = A.mallows_profile(6000, [0, 1, 2], 1.0, rng)
    counts = {tuple(row): 0 for row in map(tuple, np.array([[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]]))}
    for row in p1:
        counts[tuple(row)] += 1
    assert all(abs(c - 1000) < 150 for c in counts.values())


def test_profile_shapes_and_each_row_is_a_permutation():
    rng = np.random.default_rng(2)
    for model, gen in A.PROFILE_MODELS.items():
        p = gen(40, 5, rng)
        assert p.shape == (40, 5), model
        assert all(sorted(row) == [0, 1, 2, 3, 4] for row in p.tolist()), model


def test_single_peaked_rows_form_a_valley_over_the_axis():
    """Einspitzig: der Rangplatz fällt von der besten Position nach beiden Seiten, also ist jede Rangfolge eine „Talform“ über der Achse."""
    p = A.profile_single_peaked(60, 6, np.random.default_rng(3))
    r = A.ranks_of(p)
    for row in r:
        peak = int(np.argmin(row))
        assert all(row[i] > row[i + 1] for i in range(peak)) and all(row[i] < row[i + 1] for i in range(peak, 5))


def test_camps_have_two_opposed_base_orders():
    p = A.profile_camps(400, 4, np.random.default_rng(4), phi=0.05, share=0.5)
    first = np.bincount(p[:, 0], minlength=4)
    assert first[0] > 150 and first[3] > 150 and first[1] + first[2] < 60       # fast alle starten bei Kandidat 0 oder 3


def test_exact_probability_without_condorcet_winner_for_three_voters():
    assert A.exact_no_condorcet_probability(1) == pytest.approx(0.0)
    assert A.exact_no_condorcet_probability(3) == pytest.approx(1 / 18)      # 12 von 216 Profilen sind ein Zyklus (zwei zyklische Ordnungen je 6 Anordnungen)
