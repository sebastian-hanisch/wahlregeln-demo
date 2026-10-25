"""Verdikte (reine Funktionen): Art und jede Zahl im Text an handgesetzten Profilen und Werten, jeder Zweig."""

import numpy as np

import wrg_algorithm as A
import wrg_constants as C
import wrg_evaluation as ev
from wrg_evaluation import Analysis, Settings

TB_ID = np.array([0, 1, 2])
TB_REV = np.array([2, 1, 0])


def make(profile, tiebreak=TB_ID):
    p = np.asarray(profile)
    return Analysis(Settings("random", p.shape[1], p.shape[0], 0), p, tiebreak, A.evaluate(p, tiebreak))


def test_num_pct_label():
    assert ev.num(3.14159, 2) == "3,14" and ev.pct(0.456) == "46 %" and ev.pct(0.0456, 1) == "4,6 %" and ev.label(0) == "A" and ev.label(5) == "F"


def test_verdict_when_the_rules_disagree_but_a_condorcet_winner_exists(seven):
    kind, text = ev.verdict_state(make(seven))
    assert kind == "warning"
    assert text == ("Die vier Regeln wählen 2 verschiedene Sieger. Der Condorcet-Sieger ist **B**; ihn wählen 3 von 4 Regeln, abweichend: Mehrheitswahl: A.")


def test_verdict_when_all_rules_agree_with_the_condorcet_winner():
    kind, text = ev.verdict_state(make([[0, 1, 2]] * 3))
    assert kind == "success"
    assert text == "Alle vier Regeln wählen **A**, und das ist der Condorcet-Sieger (er schlägt jeden anderen Kandidaten mit Mehrheit)."


def test_verdict_with_a_cycle_when_all_rules_still_agree(cycle):
    kind, text = ev.verdict_state(make(cycle, TB_ID))
    assert kind == "info"
    assert text == "Es gibt **keinen Condorcet-Sieger**: die paarweisen Mehrheiten bilden einen Zyklus, kein Kandidat schlägt alle anderen. Trotzdem wählen alle vier Regeln **A**."


def test_verdict_with_a_cycle_and_different_winners(cycle):
    kind, text = ev.verdict_state(make(cycle, TB_REV))
    assert kind == "warning"
    assert text == ("Es gibt **keinen Condorcet-Sieger**: die paarweisen Mehrheiten bilden einen Zyklus, kein Kandidat schlägt alle anderen. "
                    "Die vier Regeln wählen 2 verschiedene Sieger (Mehrheitswahl: C, Borda-Zählung: C, Copeland (paarweise Siege): C, Sofortstichwahl (IRV): B); "
                    "welche „richtig“ ist, entscheidet hier allein die Regel.")


def test_distinct_counts_the_different_winners(seven, loser_wins):
    assert make(seven).distinct == 2 and make([[0, 1, 2]] * 3).distinct == 1
    assert make(loser_wins).distinct == 2          # Mehrheitswahl A, die übrigen B


def test_rule_rows_by_hand(seven):
    rows = ev.rule_rows(make(seven))
    assert [r["Regel"] for r in rows] == ["Mehrheitswahl", "Borda-Zählung", "Copeland (paarweise Siege)", "Sofortstichwahl (IRV)"]
    assert [r["Sieger"] for r in rows] == ["A", "B", "B", "B"]
    assert rows[0]["Kennzahl"] == "3 Erststimmen (43 %)" and rows[1]["Kennzahl"] == "9 Punkte (höchstens 14)"
    assert rows[2]["Kennzahl"] == "2,0 von 2 paarweisen Siegen" and rows[3]["Kennzahl"] == "3 Runden, in der letzten 7 Stimmen"
    assert [r["gleich dem Condorcet-Sieger"] for r in rows] == ["nein", "ja", "ja", "ja"]


def test_rule_rows_without_a_condorcet_winner(cycle):
    assert {r["gleich dem Condorcet-Sieger"] for r in ev.rule_rows(make(cycle))} == {"kein Condorcet-Sieger"}


def test_textbook_cycle_is_computed_from_the_pair_counts():
    profile, lines = ev.textbook_cycle()
    assert profile == [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
    assert lines == ["A schlägt B (2 : 1)", "B schlägt C (2 : 1)", "C schlägt A (2 : 1)"]


def rows_paradox():
    def row(model, m, n, share):
        return {"model": model, "m": m, "n": n, "no_condorcet": share, "runs": 400}

    return [row("random", 3, 11, 0.05), row("random", 5, 201, 0.25), row("random", 4, 51, 0.15), row("single", 5, 51, 0.0), row("camps", 5, 11, 0.2)]


def test_paradox_row_and_verdict():
    r = rows_paradox()[0]
    assert ev.paradox_row(r) == {"Profilmodell": C.MODELS["random"], "Kandidaten": 3, "Wähler": 11, "ohne Condorcet-Sieger": "5,0 %"}
    kind, text = ev.verdict_paradox(rows_paradox())
    assert kind == "info"
    assert text == ("Bei zufälligen Profilen fehlt der Condorcet-Sieger in 5,0 % der Profile (3 Kandidaten, 11 Wähler) bis 25,0 % (5 Kandidaten, 201 Wähler). "
                    "Bei einspitzigen Profilen höchstens 0,0 %.")


def test_paradox_verdict_without_single_peaked_rows():
    kind, text = ev.verdict_paradox([r for r in rows_paradox() if r["model"] == "random"])
    assert "einspitzig" not in text


def test_disagree_verdict_by_hand():
    def row(model, share):
        return {"model": model, "m": 4, "n": 51, "any_disagree": share}

    kind, text = ev.verdict_disagree([row("random", 0.468), row("single", 0.61), row("camps", 0.412)])
    assert kind == "info"
    assert text == ("Anteil der Profile, in denen mindestens zwei der vier Regeln verschiedene Sieger küren (4 Kandidaten, 51 Wähler): "
                    "Zufall: 47 %; einspitzig: 61 %; zwei Lager: 41 %.")
