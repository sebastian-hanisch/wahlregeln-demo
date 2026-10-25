"""Kern: Profile erzeugen und vier Wahlregeln auswerten.

Ein Profil ist ein Feld (n, m) mit den Rangfolgen der n Wähler: Zeile = Wähler, Spalte = Rangplatz (0 = beste), Wert = Kandidat 0 .. m-1.
Regeln: Mehrheitswahl (relative Mehrheit der Erststimmen), Borda-Zählung, Copeland (paarweise Siege), Sofortstichwahl (IRV, Alternativstimme).
Gleichstände entscheidet eine feste Rangfolge der Kandidaten (`tiebreak`: kleinerer Wert = bevorzugt); bei der Sofortstichwahl scheidet unter
mehreren Letzten der am wenigsten bevorzugte aus. Die Rangfolge ist ein Zufallslos und kommt aus dem Zufalls-Seed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

RULE_NAMES = {"plurality": "Mehrheitswahl", "borda": "Borda-Zählung", "copeland": "Copeland (paarweise Siege)", "irv": "Sofortstichwahl (IRV)"}
MALLOWS_PHI = 0.7            # Streuung um die Lager-Rangfolge: kleineres phi = einheitlichere Lager
CAMP_SHARE = 0.55           # Anteil des ersten Lagers


# --- Profile ---------------------------------------------------------------------------------------------------------------------------------

def profile_random(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Zufall (Impartial Culture): jeder Wähler zieht eine der m! Rangfolgen mit gleicher Wahrscheinlichkeit."""
    return np.argsort(rng.random((n, m)), axis=1)


def profile_single_peaked(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Einspitzig: die Kandidaten liegen auf einer Achse (Lage 0 .. m-1), jeder Wähler hat einen Idealpunkt und reiht nach Abstand."""
    ideal = rng.random(n) * m - 0.5
    dist = np.abs(ideal[:, None] - np.arange(m)[None, :]) + 1e-9 * rng.random((n, m))
    return np.argsort(dist, axis=1)


def mallows_profile(n: int, base: list[int], phi: float, rng: np.random.Generator) -> np.ndarray:
    """n Ziehungen aus dem Mallows-Modell um die Rangfolge `base` durch wiederholtes Einfügen (für alle Wähler zugleich):
    das i-te Element von `base` landet mit Gewicht phi^(i-j) an Platz j unter den bisherigen i+1 Plätzen.
    Die Wahrscheinlichkeit einer Rangfolge ist proportional zu phi^(Zahl der Fehlstände gegenüber `base`)."""
    m = len(base)
    pos = np.zeros((n, m), dtype=int)                 # pos[v, i] = Platz des i-ten Elements von base bei Wähler v
    for i in range(1, m):
        weights = phi ** (i - np.arange(i + 1))
        cum = np.cumsum(weights / weights.sum())
        j = np.minimum(np.searchsorted(cum, rng.random(n), side="right"), i)
        pos[:, :i] += (pos[:, :i] >= j[:, None])      # die bisherigen Elemente ab Platz j rutschen einen Platz nach hinten
        pos[:, i] = j
    out = np.empty((n, m), dtype=int)
    out[np.arange(n)[:, None], pos] = np.array(base)[None, :]
    return out


def profile_camps(n: int, m: int, rng: np.random.Generator, phi: float = MALLOWS_PHI, share: float = CAMP_SHARE) -> np.ndarray:
    """Zwei Lager: der Anteil `share` der Wähler streut um die Rangfolge 0, 1, .., m-1, der Rest um die umgekehrte (Mallows mit phi)."""
    n_a = int(round(share * n))
    a = mallows_profile(n_a, list(range(m)), phi, rng)
    b = mallows_profile(n - n_a, list(range(m - 1, -1, -1)), phi, rng)
    arr = np.vstack([a, b])
    return arr[rng.permutation(n)]


PROFILE_MODELS = {"random": profile_random, "single": profile_single_peaked, "camps": profile_camps}


# --- Bausteine -------------------------------------------------------------------------------------------------------------------------------

def ranks_of(profile: np.ndarray) -> np.ndarray:
    """rank[v, c] = Rangplatz des Kandidaten c bei Wähler v (0 = beste)."""
    n, m = profile.shape
    r = np.empty_like(profile)
    r[np.arange(n)[:, None], profile] = np.arange(m)[None, :]
    return r


def pairwise(profile: np.ndarray) -> np.ndarray:
    """w[a, b] = Zahl der Wähler, die a vor b reihen (Diagonale 0)."""
    r = ranks_of(profile)
    w = (r[:, :, None] < r[:, None, :]).sum(axis=0)
    np.fill_diagonal(w, 0)
    return w.astype(int)


def plurality_counts(profile: np.ndarray) -> np.ndarray:
    return np.bincount(profile[:, 0], minlength=profile.shape[1])


def borda_scores(profile: np.ndarray) -> np.ndarray:
    """Punkte: der Beste einer Rangfolge bekommt m-1, der Letzte 0."""
    m = profile.shape[1]
    return (m - 1 - ranks_of(profile)).sum(axis=0)


def copeland_scores(w: np.ndarray) -> np.ndarray:
    """Je paarweisem Sieg 1 Punkt, je Gleichstand 0,5."""
    wins = (w > w.T).sum(axis=1).astype(float)
    ties = ((w == w.T).sum(axis=1) - 1) * 0.5      # die Diagonale (a gegen a) zählt als Gleichstand und wird abgezogen
    return wins + ties


def pick(scores: np.ndarray, tiebreak: np.ndarray) -> int:
    """Kandidat mit der größten Punktzahl; bei Gleichstand der mit dem kleinsten tiebreak-Wert."""
    best = np.flatnonzero(scores == scores.max())
    return int(best[np.argmin(tiebreak[best])])


def condorcet_winner(w: np.ndarray) -> int | None:
    """Der Kandidat, der jeden anderen paarweise schlägt (echte Mehrheit); sonst None (Zyklus oder Gleichstand)."""
    m = len(w)
    for a in range(m):
        if all(w[a, b] > w[b, a] for b in range(m) if b != a):
            return a
    return None


def condorcet_loser(w: np.ndarray) -> int | None:
    m = len(w)
    for a in range(m):
        if all(w[a, b] < w[b, a] for b in range(m) if b != a):
            return a
    return None


def irv(profile: np.ndarray, tiebreak: np.ndarray) -> tuple[int, list[dict]]:
    """Sofortstichwahl: in jeder Runde scheidet der Kandidat mit den wenigsten Erststimmen aus (nur Lebende zählen), bis einer bleibt.

    Rückgabe: (Sieger, Runden), Runde = {"counts": Erststimmen je Kandidat (Ausgeschiedene 0), "out": ausgeschiedener Kandidat oder None in der letzten}."""
    n, m = profile.shape
    r = ranks_of(profile)
    alive = np.ones(m, dtype=bool)
    rounds: list[dict] = []
    while True:
        masked = np.where(alive[None, :], r, m + 1)
        first = np.argmin(masked, axis=1)
        counts = np.bincount(first, minlength=m) * alive
        if alive.sum() == 1:
            rounds.append({"counts": counts.copy(), "out": None})
            return int(np.flatnonzero(alive)[0]), rounds
        cand = np.flatnonzero(alive)
        low = cand[counts[cand] == counts[cand].min()]
        out = int(low[np.argmax(tiebreak[low])])           # unter den Letzten scheidet der am wenigsten bevorzugte aus
        rounds.append({"counts": counts.copy(), "out": out})
        alive[out] = False


@dataclass(frozen=True)
class Outcome:
    winners: dict          # Regelname -> Sieger
    condorcet: int | None
    loser: int | None
    plurality: np.ndarray
    borda: np.ndarray
    copeland: np.ndarray
    margins: np.ndarray    # w
    irv_rounds: list


def evaluate(profile: np.ndarray, tiebreak: np.ndarray) -> Outcome:
    w = pairwise(profile)
    pl, bo, co = plurality_counts(profile), borda_scores(profile), copeland_scores(w)
    iw, rounds = irv(profile, tiebreak)
    winners = {"plurality": pick(pl, tiebreak), "borda": pick(bo, tiebreak), "copeland": pick(co, tiebreak), "irv": iw}
    return Outcome(winners, condorcet_winner(w), condorcet_loser(w), pl, bo, co, w, rounds)


# --- Exakte Gegenprobe (kleine Fälle, drei Kandidaten) ---------------------------------------------------------------------------------------

def exact_no_condorcet_probability(n: int) -> float:
    """Zufall mit drei Kandidaten: Wahrscheinlichkeit ohne Condorcet-Sieger bei n Wählern, EXAKT über alle Zusammensetzungen der n Wähler auf die 6 Rangfolgen
    (Gewicht = Multinomialkoeffizient / 6^n). Unabhängig von den Regeln oben: nur Paarzählung."""
    import itertools
    from math import factorial

    perms = list(itertools.permutations(range(3)))
    pos = [{c: i for i, c in enumerate(p)} for p in perms]

    def compositions(total, parts):
        if parts == 1:
            yield (total,)
            return
        for i in range(total + 1):
            for rest in compositions(total - i, parts - 1):
                yield (i,) + rest

    total_prob = 0.0
    for comp in compositions(n, 6):
        w = np.zeros((3, 3), dtype=int)
        for cnt, p in zip(comp, pos):
            if cnt:
                for a in range(3):
                    for b in range(3):
                        if a != b and p[a] < p[b]:
                            w[a, b] += cnt
        if condorcet_winner(w) is None:
            coef = factorial(n)
            for cnt in comp:
                coef //= factorial(cnt)
            total_prob += coef / 6 ** n
    return total_prob
