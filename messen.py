"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout."""

import sys
import time

sys.path.insert(0, ".")
import wrg_algorithm as A
import wrg_constants as C
import wrg_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    o = a.outcome
    print(name, {k: ev.label(c) for k, c in o.winners.items()}, "Condorcet", None if o.condorcet is None else ev.label(o.condorcet), "verschieden", a.distinct, ev.verdict_state(a)[0])

print("EXAKT (drei Kandidaten, Zufall)")
for n in (1, 3, 5, 7, 9, 11, 15, 21):
    print("n", n, "ohne Condorcet-Sieger", round(100 * A.exact_no_condorcet_probability(n), 3), "%")

print("REIHE 1 (Anteil ohne Condorcet-Sieger, %)")
rows = ev.series_paradox()
for model in C.MODELS:
    for m in C.SERIES_MS:
        print(model, "m", m, [round(100 * r["no_condorcet"], 1) for r in rows if r["model"] == model and r["m"] == m], "für n", C.SERIES_NS)

print("REIHE 2")
for r in ev.series_disagree():
    print(r["model"], "mindestens zwei uneins", round(100 * r["any_disagree"], 1), "mit Condorcet-Sieger", round(100 * r["share_with_condorcet"], 1))
    print("   verfehlt den Condorcet-Sieger", {k: round(100 * v, 1) for k, v in r["miss_condorcet"].items()})
    print("   wählt den Condorcet-Verlierer", {k: round(100 * v, 1) for k, v in r["picks_loser"].items()})
    print("   Paare uneins", {f"{x}-{y}": round(100 * v, 1) for (x, y), v in r["pairs"].items()})
print("sec", round(time.time() - t0, 1))
