"""Abbildungen: Spuren je Figur, Werte, Achsen gesperrt."""

import numpy as np

import wrg_algorithm as A
import wrg_constants as C
import wrg_evaluation as ev
import wrg_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def analysis(seven):
    tb = np.array([0, 1, 2])
    return ev.Analysis(ev.Settings("random", 3, 7, 0), seven, tb, A.evaluate(seven, tb))


def test_scores_figure_by_hand(seven):
    fig = V.build_scores(analysis(seven))
    assert [t.name.split(":")[0] for t in fig.data] == ["Mehrheitswahl", "Borda", "Copeland"] and _locked(fig)
    assert list(fig.data[0].x) == ["A", "B", "C"]
    assert np.allclose(fig.data[0].y, [3 / 7, 2 / 7, 2 / 7]) and np.allclose(fig.data[1].y, [6 / 14, 9 / 14, 6 / 14]) and np.allclose(fig.data[2].y, [0.0, 1.0, 0.5])
    assert list(fig.data[0].marker.line.width) == [3, 0, 0] and list(fig.data[1].marker.line.width) == [0, 3, 0]          # der Sieger ist umrahmt


def test_margin_heatmap_by_hand(seven):
    fig = V.build_margins(analysis(seven))
    z = fig.data[0].z
    assert z[0][0] is None and np.isclose(z[1][0], 4 / 7) and np.isclose(z[1][2], 5 / 7) and np.isclose(z[0][1], 3 / 7)
    assert fig.data[0].text[1][2] == "71 %" and _locked(fig)


def test_irv_rounds_figure(seven):
    fig = V.build_irv(analysis(seven))
    assert [t.name for t in fig.data] == ["A", "B", "C"] and _locked(fig)
    assert list(fig.data[0].y) == [3, 3, 0] and list(fig.data[1].y) == [2, 4, 7] and list(fig.data[2].y) == [2, 0, 0]


def rows_paradox():
    return [{"model": mo, "m": m, "n": n, "no_condorcet": 0.1 * m, "runs": 10} for mo in C.MODELS for m in (3, 4) for n in (11, 51)]


def test_paradox_figure_has_a_line_per_model_and_candidate_count():
    fig = V.build_paradox(rows_paradox())
    assert len(fig.data) == 6 and _locked(fig)
    assert fig.data[0].name.startswith("3 Kandidaten") and list(fig.data[0].x) == [11, 51]


def test_disagree_figure_has_a_bar_per_rule():
    rows = [{"model": mo, "miss_condorcet": {k: 0.1 for k in A.RULE_NAMES}} for mo in C.MODELS]
    fig = V.build_disagree(rows)
    assert [t.name for t in fig.data] == list(A.RULE_NAMES.values()) and _locked(fig)
    assert list(fig.data[0].x) == ["Zufall", "einspitzig", "zwei Lager"]
