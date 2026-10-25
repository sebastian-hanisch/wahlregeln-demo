"""Auswertung: ein Profil analysieren, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import wrg_algorithm as A
import wrg_constants as C
from wrg_scenario import make_profile


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 0) -> str:
    return f"{100 * x:.{digits}f} %".replace(".", ",")


def label(c) -> str:
    return C.CANDIDATE_LABELS[int(c)]


@dataclass(frozen=True)
class Settings:
    model: str = C.DEFAULT_MODEL
    m: int = C.DEFAULT_M
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    profile: np.ndarray
    tiebreak: np.ndarray
    outcome: A.Outcome

    @property
    def distinct(self) -> int:
        return len(set(self.outcome.winners.values()))


def analyse(settings: Settings) -> Analysis:
    profile, tiebreak = make_profile(settings.model, settings.m, settings.n, settings.seed)
    return Analysis(settings, profile, tiebreak, A.evaluate(profile, tiebreak))


def rule_rows(a: Analysis) -> list[dict]:
    """Tabelle der vier Regeln: Sieger, Kennzahl des Siegers, stimmt der Sieger mit dem Condorcet-Sieger überein."""
    o, n = a.outcome, a.settings.n
    cw = o.condorcet
    info = {
        "plurality": lambda c: f"{int(o.plurality[c])} Erststimmen ({pct(o.plurality[c] / n)})",
        "borda": lambda c: f"{int(o.borda[c])} Punkte (höchstens {n * (a.settings.m - 1)})",
        "copeland": lambda c: f"{num(o.copeland[c], 1)} von {a.settings.m - 1} paarweisen Siegen",
        "irv": lambda c: f"{len(o.irv_rounds)} Runden, in der letzten {int(o.irv_rounds[-1]['counts'][c])} Stimmen",
    }
    rows = []
    for key, name in A.RULE_NAMES.items():
        c = o.winners[key]
        rows.append({"Regel": name, "Sieger": label(c), "Kennzahl": info[key](c),
                     "gleich dem Condorcet-Sieger": "kein Condorcet-Sieger" if cw is None else ("ja" if c == cw else "nein")})
    return rows


def textbook_cycle() -> tuple[list[list[int]], list[str]]:
    """Das Lehrbuchbeispiel mit drei Wählern: A > B > C, B > C > A, C > A > B. Rückgabe: Profil und die drei Paarvergleiche als Text, aus der Paarzählung berechnet."""
    profile = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
    w = A.pairwise(np.array(profile))
    lines = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        big, small = (a, b) if w[a, b] > w[b, a] else (b, a)
        lines.append(f"{label(big)} schlägt {label(small)} ({max(w[a, b], w[b, a])} : {min(w[a, b], w[b, a])})")
    return profile, lines


def verdict_state(a: Analysis) -> tuple[str, str]:
    """Verdikt der Kernfrage für ein Profil als (Art, Text), rein: die App ruft st.<Art>(Text), der Test prüft jede Zahl im Text."""
    o = a.outcome
    winners = {A.RULE_NAMES[k]: label(c) for k, c in o.winners.items()}
    distinct = sorted(set(winners.values()))
    cw = o.condorcet
    if cw is None:
        body = "Es gibt **keinen Condorcet-Sieger**: die paarweisen Mehrheiten bilden einen Zyklus, kein Kandidat schlägt alle anderen."
        if len(distinct) == 1:
            return "info", f"{body} Trotzdem wählen alle vier Regeln **{distinct[0]}**."
        return "warning", f"{body} Die vier Regeln wählen {len(distinct)} verschiedene Sieger ({', '.join(f'{r}: {c}' for r, c in winners.items())}); welche „richtig“ ist, entscheidet hier allein die Regel."
    agree_with_cw = [r for r, c in winners.items() if c == label(cw)]
    if len(distinct) == 1:
        return "success", f"Alle vier Regeln wählen **{distinct[0]}**, und das ist der Condorcet-Sieger (er schlägt jeden anderen Kandidaten mit Mehrheit)."
    off = [f"{r}: {c}" for r, c in winners.items() if c != label(cw)]
    return "warning", (f"Die vier Regeln wählen {len(distinct)} verschiedene Sieger. Der Condorcet-Sieger ist **{label(cw)}**; ihn wählen {len(agree_with_cw)} von 4 Regeln, "
                       f"abweichend: {', '.join(off)}.")


# --- Messreihen --------------------------------------------------------------------------------------------------------------------------------

def run_profiles(model: str, m: int, n: int, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[A.Outcome]:
    return [A.evaluate(*make_profile(model, m, n, seed + j)) for j in range(runs)]


def series_paradox(ms=C.SERIES_MS, ns=C.SERIES_NS, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Anteil der Profile ohne Condorcet-Sieger je Profilmodell, Kandidatenzahl und Wählerzahl (feste Seeds seed .. seed+runs-1)."""
    rows = []
    for model in C.MODELS:
        for m in ms:
            for n in ns:
                outs = run_profiles(model, m, n, runs, seed)
                rows.append({"model": model, "m": m, "n": n, "no_condorcet": float(np.mean([o.condorcet is None for o in outs])), "runs": runs})
    return rows


def series_disagree(m: int = C.SERIES_DISAGREE_M, n: int = C.SERIES_DISAGREE_N, runs: int = C.SERIES_RUNS, seed: int = C.SERIES_SEED) -> list[dict]:
    """Wie oft küren zwei Regeln verschiedene Sieger, wie oft verfehlt eine Regel den Condorcet-Sieger, wie oft siegt der Condorcet-Verlierer (je Profilmodell)."""
    keys = list(A.RULE_NAMES)
    rows = []
    for model in C.MODELS:
        outs = run_profiles(model, m, n, runs, seed)
        pairs = {(x, y): float(np.mean([o.winners[x] != o.winners[y] for o in outs])) for i, x in enumerate(keys) for y in keys[i + 1:]}
        with_cw = [o for o in outs if o.condorcet is not None]
        miss = {k: (float(np.mean([o.winners[k] != o.condorcet for o in with_cw])) if with_cw else 0.0) for k in keys}
        loser = {k: float(np.mean([o.loser is not None and o.winners[k] == o.loser for o in outs])) for k in keys}
        rows.append({"model": model, "m": m, "n": n, "runs": runs, "pairs": pairs, "miss_condorcet": miss, "picks_loser": loser,
                     "any_disagree": float(np.mean([len(set(o.winners.values())) > 1 for o in outs])), "share_with_condorcet": len(with_cw) / runs})
    return rows


def paradox_row(r: dict) -> dict:
    return {"Profilmodell": C.MODELS[r["model"]], "Kandidaten": r["m"], "Wähler": r["n"], "ohne Condorcet-Sieger": pct(r["no_condorcet"], 1)}


def verdict_paradox(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 1: nennt für das Zufallsprofil den kleinsten und größten Anteil, für das einspitzige den größten."""
    rnd = [r for r in rows if r["model"] == "random"]
    single = [r for r in rows if r["model"] == "single"]
    lo, hi = min(rnd, key=lambda r: r["no_condorcet"]), max(rnd, key=lambda r: r["no_condorcet"])
    s_hi = max(single, key=lambda r: r["no_condorcet"]) if single else None
    text = (f"Bei zufälligen Profilen fehlt der Condorcet-Sieger in {pct(lo['no_condorcet'], 1)} der Profile ({lo['m']} Kandidaten, {lo['n']} Wähler) "
            f"bis {pct(hi['no_condorcet'], 1)} ({hi['m']} Kandidaten, {hi['n']} Wähler).")
    if s_hi is not None:
        text += f" Bei einspitzigen Profilen höchstens {pct(s_hi['no_condorcet'], 1)}."
    return "info", text


def verdict_disagree(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 2: Anteil der Profile, in denen mindestens zwei Regeln verschiedene Sieger küren, je Profilmodell."""
    parts = [f"{C.MODELS[r['model']].split(' (')[0]}: {pct(r['any_disagree'], 0)}" for r in rows]
    r0 = rows[0]
    return "info", f"Anteil der Profile, in denen mindestens zwei der vier Regeln verschiedene Sieger küren ({r0['m']} Kandidaten, {r0['n']} Wähler): " + "; ".join(parts) + "."
