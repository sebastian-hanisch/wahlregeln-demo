"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

MODELS = {
    "random": "Zufall (jeder Wähler ordnet beliebig)",
    "single": "einspitzig (Kandidaten auf einer Achse)",
    "camps": "zwei Lager (55 : 45, gegenläufig, mit Streuung)",
}
DEFAULT_MODEL = "random"

M_MIN, M_MAX, DEFAULT_M = 2, 6, 3             # bei zwei Kandidaten gibt es nie Streit zwischen den Regeln: der kleinste Fall gehört dazu
N_MIN, N_MAX, DEFAULT_N = 3, 301, 51          # Schritt 2: immer eine ungerade Zahl von Wählern (keine Gleichstände zwischen zwei Kandidaten)
SEED_MAX, DEFAULT_SEED = 999999, 3

# Feste Messreihen (unabhängig von den Reglern): nie ein einzelner Seed als Befund
SERIES_SEED = 100000
SERIES_RUNS = 400
SERIES_MS = (3, 4, 5, 6)
SERIES_NS = (11, 51, 201)
SERIES_DISAGREE_M, SERIES_DISAGREE_N = 4, 51

COLOR_PLURALITY = "#4c78a8"
COLOR_BORDA = "#e8a838"
COLOR_COPELAND = "#2F6B65"
COLOR_IRV = "#b04a3a"
COLOR_ALERT = "#c0392b"
COLOR_MUTED = "#8a8f98"
RULE_COLORS = {"plurality": COLOR_PLURALITY, "borda": COLOR_BORDA, "copeland": COLOR_COPELAND, "irv": COLOR_IRV}
CANDIDATE_LABELS = "ABCDEF"

PRESETS = {
    "Zufall, drei Kandidaten": {"model": "random", "m": 3, "n": 51, "seed": DEFAULT_SEED},
    "Viele Kandidaten, viele Wähler": {"model": "random", "m": 5, "n": 201, "seed": DEFAULT_SEED},
    "Einspitzig: ein mittlerer Sieger": {"model": "single", "m": 5, "n": 101, "seed": DEFAULT_SEED},
    "Zwei Lager: der Kompromiss": {"model": "camps", "m": 5, "n": 101, "seed": 1},
    "Ein Zyklus bei wenigen Wählern": {"model": "random", "m": 3, "n": 7, "seed": 8},
}
PRESET_HELP = {
    "Zufall, drei Kandidaten": "Voreinstellung: 51 Wähler ordnen drei Kandidaten völlig zufällig. Der Zufalls-Seed ist ein Beispiel, bei dem die Regeln auseinandergehen: es gibt einen Condorcet-Sieger, aber nicht jede Regel wählt ihn.",
    "Viele Kandidaten, viele Wähler": "5 Kandidaten, 201 Wähler, Zufallsprofil: bei Zufallsprofilen fehlt mit mehr Kandidaten häufiger ein Condorcet-Sieger, und die Regeln widersprechen sich öfter.",
    "Einspitzig: ein mittlerer Sieger": "5 Kandidaten auf einer Achse, Wähler mit Idealpunkt. Es gibt immer einen Condorcet-Sieger (der Kandidat beim mittleren Wähler); die Mehrheitswahl verfehlt ihn trotzdem oft, weil sie nur die Erststimmen zählt.",
    "Zwei Lager: der Kompromiss": "Zwei gegenläufige Lager (55 : 45) mit Streuung. In diesem Beispiel gewinnt Kandidat B (Zweiter im größeren Lager, bester mittlerer Rang) bei Borda, Copeland und Sofortstichwahl, die Mehrheitswahl wählt den Kandidaten des größeren Lagers.",
    "Ein Zyklus bei wenigen Wählern": "7 Wähler, 3 Kandidaten, Zufalls-Seed so gewählt, dass die paarweisen Mehrheiten einen Zyklus bilden: kein Condorcet-Sieger. Ohne Auswahl des Seeds tritt das bei Zufallsprofilen mit drei Kandidaten in rund 8 % der Fälle auf.",
}
