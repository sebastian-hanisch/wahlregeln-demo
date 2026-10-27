"""Wahlregeln im Vergleich: wer gewinnt, wenn alle Recht haben? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 1 der Linie „Abstimmen und Fair Teilen“: vier Wahlregeln (Mehrheitswahl, Borda, Copeland, Sofortstichwahl) auf denselben Profilen. Es gibt keine Wahrheit
(anders als in `rangaggregation-demo`): jeder Wähler hat Recht, gefragt ist, was jede Regel aus den Präferenzen macht. Der Kern liegt in wrg_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import wrg_constants as C
import wrg_evaluation as ev
from wrg_evaluation import Settings, analyse, label, num, paradox_row, pct, rule_rows, verdict_disagree, verdict_paradox, verdict_state
from wrg_layout import dunkles_design, kopf_css
from wrg_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from wrg_visualization import build_disagree, build_irv, build_margins, build_paradox, build_scores

st.set_page_config(page_title="Wahlregeln im Vergleich – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _series_paradox():
    return ev.series_paradox()


@st.cache_data(show_spinner=False)
def _series_disagree():
    return ev.series_disagree()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in wrg_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🗳️ Wahlregeln im Vergleich: wer gewinnt, wenn alle Recht haben?")
st.markdown(
    """
Ein Gremium soll **einen** Kandidaten oder Lieferanten wählen, und jedes Mitglied hat eine **Rangfolge**. Es gibt keine „richtige“ Antwort, nur eine **Regel**, die aus den Rangfolgen einen Sieger macht.
Die Demo wendet vier Regeln auf **dieselben Profile** an: **Mehrheitswahl** (nur die Erststimmen), **Borda** (Punkte für jeden Rang), **Copeland** (wer gewinnt die meisten Paarvergleiche) und **Sofortstichwahl** (der Letzte scheidet aus, bis einer bleibt).
Sie zeigt, **wie oft die Regeln einen verschiedenen Sieger küren**, wie oft es **gar keinen Kandidaten gibt, der alle anderen mit Mehrheit schlägt** (Condorcet-Paradoxon) und wie sehr das vom **Profilmodell** abhängt.
Stück 1 der Linie „Abstimmen und Fair Teilen“; die Rangaggregation mit einer wahren Ordnung steht in `rangaggregation-demo`.

Weiter unten: der Abschnitt **🔬 Messreihen**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So zählen die vier Regeln", expanded=True):
    st.markdown(
        """
1. **Mehrheitswahl:** jeder Wähler zählt nur seinen ersten Platz; wer die meisten Erststimmen hat, gewinnt (auch mit weniger als der Hälfte).
2. **Borda:** der erste Platz bringt m − 1 Punkte, der letzte 0; wer die meisten Punkte über alle Wähler hat, gewinnt.
3. **Copeland:** je Paar zählt die Mehrheit der Wähler; ein Sieg bringt 1 Punkt, ein Gleichstand 0,5; wer die meisten Punkte hat, gewinnt. Ein **Condorcet-Sieger** gewinnt jeden Paarvergleich.
4. **Sofortstichwahl:** in jeder Runde zählen die Erststimmen unter den noch Lebenden, der Kandidat mit den wenigsten scheidet aus, seine Stimmen gehen an den nächsten Platz; es bleibt einer übrig.
5. **Gleichstand:** ein festes Zufallslos (aus dem Zufalls-Seed) legt vorher eine Rangfolge der Kandidaten fest; bei der Sofortstichwahl scheidet unter mehreren Letzten der am wenigsten bevorzugte aus.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    model = st.selectbox("Profilmodell", list(C.MODELS), format_func=C.MODELS.get, key="model_select",
                         help="Wie die Wähler ihre Rangfolgen bilden. Zufall: jede der m! Rangfolgen gleich wahrscheinlich. Einspitzig: die Kandidaten liegen auf einer Achse, jeder Wähler reiht nach Abstand zu seinem Idealpunkt. Zwei Lager: 55 % streuen um eine Rangfolge, 45 % um die umgekehrte.")
    m = st.slider("Kandidaten", *bounds("m_slider"), key="m_slider", help="Wie viele Kandidaten zur Wahl stehen.")
    n = st.slider("Wähler", *bounds("n_slider"), key="n_slider", step=2, help="Immer eine ungerade Zahl: zwischen zwei Kandidaten gibt es dann keinen Gleichstand.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Profil ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"model_select": model, "m_slider": int(m), "n_slider": int(n), "seed_input": int(seed)})

settings = Settings(model=model, m=int(m), n=int(n), seed=int(seed))
a = _analysis(settings)
o = a.outcome

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Condorcet-Sieger", "keiner (Zyklus)" if o.condorcet is None else label(o.condorcet), delta="schlägt jeden anderen mit Mehrheit" if o.condorcet is not None else "kein Kandidat schlägt alle", delta_color="off")
m2.metric("Verschiedene Sieger", f"{a.distinct} von 4 Regeln", delta="alle Regeln einig" if a.distinct == 1 else "die Regeln widersprechen sich", delta_color="off")
m3.metric("Mehrheitswahl", label(o.winners["plurality"]), delta=f"{pct(o.plurality[o.winners['plurality']] / settings.n)} der Erststimmen", delta_color="off")
m4.metric("Borda", label(o.winners["borda"]), delta=f"{int(o.borda[o.winners['borda']])} Punkte", delta_color="off")
st.table(rule_rows(a))
c1, c2 = st.columns(2)
c1.plotly_chart(build_scores(a), width="stretch", key="main_scores")
c2.plotly_chart(build_margins(a), width="stretch", key="main_margins")
st.caption("Links: die Kennzahlen der drei punktebasierten Regeln je Kandidat, der Sieger jeder Regel mit schwarzem Rahmen (Gleichstand: Los). Rechts: Anteil der Wähler, die die Zeile vor der Spalte reihen; blau über 50 %, rot darunter. Ein Condorcet-Sieger ist eine Zeile, die überall blau ist.")
with st.expander("Sofortstichwahl Runde für Runde"):
    st.plotly_chart(build_irv(a), width="stretch", key="irv_chart")
    st.caption("Je Runde die Erststimmen unter den noch Lebenden; der Kandidat mit den wenigsten scheidet aus. Gleichstand unter den Letzten: der am wenigsten bevorzugte Kandidat (Los).")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wählen die Regeln denselben Sieger?")
kind, text = verdict_state(a)
getattr(st, kind)(text)

with st.expander("Das Lehrbuchbeispiel: drei Wähler, ein Zyklus"):
    profile, lines = ev.textbook_cycle()
    st.markdown("Drei Wähler, drei Kandidaten, jeder ordnet anders:")
    st.table([{"Wähler": f"Wähler {i + 1}", "1. Platz": label(r[0]), "2. Platz": label(r[1]), "3. Platz": label(r[2])} for i, r in enumerate(profile)])
    st.markdown("Paarvergleiche (zwei von drei Wählern entscheiden): " + "; ".join(lines) + ". **Jeder Kandidat verliert gegen einen anderen: es gibt keinen Condorcet-Sieger, die Mehrheit ist im Kreis.**")

st.markdown("---")

# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Messreihen: wie oft widersprechen sich die Regeln?")
st.caption(
    f"Feste Programme, unabhängig von den Reglern: je Zelle {C.SERIES_RUNS} Profile mit den Zufalls-Seeds {C.SERIES_SEED} bis {C.SERIES_SEED + C.SERIES_RUNS - 1}, alle drei Profilmodelle. "
    "Jede Reihe rechnet auf Klick in einigen Sekunden."
)
tab1, tab2 = st.tabs(["Condorcet-Paradoxon", "Regeln im Widerspruch"])
with tab1:
    st.markdown("**Wie oft fehlt ein Condorcet-Sieger?** Anteil der Profile ohne einen Kandidaten, der alle anderen mit Mehrheit schlägt, nach Kandidaten- und Wählerzahl.")
    if st.button("Reihe rechnen", key="paradox_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_paradox()
        st.session_state["paradox_done"] = time.perf_counter() - t0
    if "paradox_done" in st.session_state:
        rows = _series_paradox()
        st.plotly_chart(build_paradox(rows), width="stretch", key="paradox_chart")
        st.table([paradox_row(r) for r in rows if r["model"] == "random"])
        kind, text = verdict_paradox(rows)
        getattr(st, kind)(text)
        st.caption(f"Die Tabelle zeigt das Zufallsprofil; Linien: durchgezogen Zufall, gepunktet einspitzig, gestrichelt zwei Lager. Rechenzeit dieser Sitzung: {num(st.session_state['paradox_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown(f"**Wie oft verfehlt eine Regel den Condorcet-Sieger?** {C.SERIES_DISAGREE_M} Kandidaten, {C.SERIES_DISAGREE_N} Wähler; nur Profile, in denen es einen Condorcet-Sieger gibt.")
    if st.button("Reihe rechnen", key="disagree_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe (einige Sekunden) …"):
            _series_disagree()
        st.session_state["disagree_done"] = time.perf_counter() - t0
    if "disagree_done" in st.session_state:
        rows = _series_disagree()
        st.plotly_chart(build_disagree(rows), width="stretch", key="disagree_chart")
        st.table([{"Profilmodell": C.MODELS[r["model"]], "mit Condorcet-Sieger": pct(r["share_with_condorcet"]), "mindestens zwei Regeln uneins": pct(r["any_disagree"]),
                   "Mehrheitswahl wählt den Condorcet-Verlierer": pct(r["picks_loser"]["plurality"], 1)} for r in rows])
        kind, text = verdict_disagree(rows)
        getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Jeder Wähler gibt seine wahre Rangfolge an** | Wähler können taktisch lügen; ab drei Kandidaten ist keine der Regeln dagegen gefeit. | Manipulation (Stück 3 der Linie) |
| **Die Profile sind Modelle** | Die Anteile hängen vom Profilmodell ab: bei einspitzigen Profilen gibt es nie einen Zyklus, bei Zufallsprofilen oft. Echte Präferenzen liegen dazwischen. | diese Demo (drei Modelle) |
| **Vollständige Rangfolgen ohne Gleichstände** | Echte Wähler lassen Plätze offen oder bewerten gleich; das ändert alle vier Regeln. | – |
| **Ein Gleichstand wird per Los entschieden** | Bei kleinen Wählerzahlen entscheidet das Los öfter; das Ergebnis hängt dann am Zufalls-Seed. | – |
| **Es gibt keine Wahrheit** | Wenn die Rangfolgen verrauschte Messungen einer wahren Ordnung wären, wäre das Ziel ein anderes (die Wahrheit treffen). | `rangaggregation-demo` |
| **Alle Wähler zählen gleich** | Gewichtete Stimmen und Delegation sind nicht Teil dieser Demo. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Profil.** $n$ Wähler, $m$ Kandidaten; jeder Wähler $v$ hat eine strikte Rangfolge, $\mathrm{rk}_v(c) \in \{0, \dots, m-1\}$ ist der Rangplatz von $c$ (0 = beste).

**Regeln.** Mehrheitswahl: $P(c) = \#\{v : \mathrm{rk}_v(c) = 0\}$. Borda: $B(c) = \sum_v \big(m - 1 - \mathrm{rk}_v(c)\big)$.
Paarweise Mehrheit: $W(a, b) = \#\{v : \mathrm{rk}_v(a) < \mathrm{rk}_v(b)\}$.

$$\mathrm{Cop}(a) = \#\{b : W(a, b) > W(b, a)\} + \tfrac{1}{2}\,\#\{b \ne a : W(a, b) = W(b, a)\}.$$

Ein **Condorcet-Sieger** ist ein $a$ mit $W(a, b) > W(b, a)$ für alle $b \ne a$; er ist eindeutig, wenn er existiert. Die **Sofortstichwahl** scheidet nacheinander den Kandidaten mit den wenigsten Erststimmen unter den Lebenden aus.

**Condorcet-Paradoxon.** Bei Zufallsprofilen mit drei Kandidaten wird die Wahrscheinlichkeit ohne Condorcet-Sieger bei wachsender Wählerzahl etwa 8,8 % (aus dem Gedächtnis nach Gehrlein, nicht im Original geprüft); die Demo rechnet kleine Fälle **exakt** über alle Zusammensetzungen der Wähler auf die sechs Rangfolgen und die großen per Simulation.

**Mallows-Modell (zwei Lager).** Die Wahrscheinlichkeit einer Rangfolge $\pi$ um die Grundrangfolge $\sigma$ ist $\propto \varphi^{d(\pi, \sigma)}$ mit der Zahl $d$ der Fehlstände (hier $\varphi = 0{,}7$).

**Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Condorcet (1785), Borda (1781), Copeland (1951), Black (1948, einspitzige Präferenzen), Arrow (1951); Überblick: Brandt, Conitzer, Endriss, Lang, Procaccia (Hrsg.), *Handbook of Computational Social Choice*, Cambridge University Press 2016.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
