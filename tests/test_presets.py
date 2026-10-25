"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, keiner auf einem Reglerrand und keiner, der durch eine einzelne Regleränderung vom Standard entsteht."""

import wrg_constants as C
import wrg_evaluation as ev
import wrg_presets as P

FIRST = "Zufall, drei Kandidaten"


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds_and_on_the_step_grid():
    for name, p in C.PRESETS.items():
        assert p["model"] in C.MODELS and C.M_MIN <= p["m"] <= C.M_MAX and C.N_MIN <= p["n"] <= C.N_MAX and 0 <= p["seed"] <= C.SEED_MAX, name
        assert (p["n"] - C.N_MIN) % 2 == 0, name                      # Schrittweite 2 ab dem Minimum: immer ungerade Wählerzahl


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[FIRST]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_preset_sits_on_a_slider_bound():
    bounds = {"m": (C.M_MIN, C.M_MAX), "n": (C.N_MIN, C.N_MAX)}
    for name, preset in C.PRESETS.items():
        for key, (lo, hi) in bounds.items():
            assert preset[key] not in (lo, hi), (name, key)


def test_no_single_change_of_the_default_produces_another_preset():
    default = C.PRESETS[FIRST]
    for name, p in C.PRESETS.items():
        if name != FIRST:
            assert sum(1 for k in p if p[k] != default[k]) >= 2, name


def test_presets_are_pairwise_different_and_cover_all_models():
    values = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(values)) == len(values)
    assert {p["model"] for p in C.PRESETS.values()} == set(C.MODELS)


def test_the_cycle_preset_really_has_no_condorcet_winner_and_the_default_has_one_but_disagreement():
    cyc = ev.analyse(ev.Settings(**C.PRESETS["Ein Zyklus bei wenigen Wählern"]))
    assert cyc.outcome.condorcet is None
    base = ev.analyse(ev.Settings(**C.PRESETS[FIRST]))
    assert base.outcome.condorcet is not None and base.distinct >= 2


def test_the_camps_preset_shows_the_compromise_story():
    a = ev.analyse(ev.Settings(**C.PRESETS["Zwei Lager: der Kompromiss"]))
    w = a.outcome.winners
    assert w["borda"] == w["copeland"] == w["irv"] == a.outcome.condorcet and w["plurality"] != w["borda"]


def test_the_single_peaked_preset_has_a_middle_condorcet_winner_that_plurality_misses():
    a = ev.analyse(ev.Settings(**C.PRESETS["Einspitzig: ein mittlerer Sieger"]))
    assert a.outcome.condorcet == 2 and a.outcome.winners["plurality"] != 2
