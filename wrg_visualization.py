"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import wrg_algorithm as A
import wrg_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _labels(m):
    return [C.CANDIDATE_LABELS[i] for i in range(m)]


def build_scores(a):
    """Je Kandidat drei normierte Kennzahlen: Anteil der Erststimmen (Mehrheitswahl), Borda-Punkte im Verhältnis zum Höchstwert, Copeland-Siege im Verhältnis zu m-1.
    Der Sieger der jeweiligen Regel ist mit einem Rahmen markiert (Gleichstand: der per Los gewählte)."""
    o, s = a.outcome, a.settings
    labels = _labels(s.m)
    series = [
        ("plurality", "Mehrheitswahl: Anteil Erststimmen", o.plurality / s.n),
        ("borda", "Borda: Punkte im Verhältnis zum Höchstwert", o.borda / (s.n * (s.m - 1))),
        ("copeland", "Copeland: Siege im Verhältnis zu m − 1", o.copeland / (s.m - 1)),
    ]
    fig = go.Figure()
    for key, name, vals in series:
        winner = o.winners[key]
        fig.add_trace(go.Bar(
            x=labels, y=list(vals), name=name, marker_color=C.RULE_COLORS[key],
            marker_line_width=[3 if i == winner else 0 for i in range(s.m)], marker_line_color="#000000",
            hovertemplate="%{x}: %{y:.3f}<extra>" + name + "</extra>",
        ))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Kandidat")
    fig.update_yaxes(title_text="Kennzahl (0 bis 1)", range=[0, 1.05])
    return _base(fig)


def build_margins(a):
    """Paarweise Mehrheiten: Zelle (Zeile, Spalte) = Anteil der Wähler, die die Zeile vor der Spalte reihen. Über 50 % (blau) heißt: Zeile schlägt Spalte."""
    s = a.settings
    labels = _labels(s.m)
    w = a.outcome.margins
    z = [[None if i == j else w[i, j] / s.n for j in range(s.m)] for i in range(s.m)]
    text = [["" if i == j else f"{100 * w[i, j] / s.n:.0f} %" for j in range(s.m)] for i in range(s.m)]
    fig = go.Figure(go.Heatmap(z=z, x=labels, y=labels, text=text, texttemplate="%{text}", zmin=0, zmax=1, zmid=0.5, colorscale="RdBu", showscale=False,
                               hovertemplate="%{y} vor %{x}: %{z:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="… gegen Kandidat", side="top")
    fig.update_yaxes(title_text="Kandidat …", autorange="reversed")
    return _base(fig, height=340)


def build_irv(a):
    """Runden der Sofortstichwahl: Erststimmen der Lebenden je Runde; in jeder Runde scheidet der Kandidat mit den wenigsten aus."""
    s = a.settings
    labels = _labels(s.m)
    rounds = a.outcome.irv_rounds
    fig = go.Figure()
    for c in range(s.m):
        ys = [int(r["counts"][c]) if int(r["counts"][c]) > 0 or r["out"] != c else 0 for r in rounds]
        fig.add_trace(go.Bar(x=[f"Runde {i + 1}" for i in range(len(rounds))], y=ys, name=labels[c], hovertemplate="%{x}: %{y} Stimmen<extra>" + labels[c] + "</extra>"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Erststimmen unter den Lebenden")
    return _base(fig, height=300)


def build_paradox(rows):
    """Anteil der Profile ohne Condorcet-Sieger über der Wählerzahl; je Profilmodell und Kandidatenzahl eine Linie."""
    dashes = {"random": "solid", "single": "dot", "camps": "dash"}
    palette = ["#4c78a8", "#e8a838", "#2F6B65", "#b04a3a", "#7f7f7f", "#9467bd"]
    fig = go.Figure()
    ms = sorted({r["m"] for r in rows})
    for model in C.MODELS:
        for m in ms:
            pts = sorted((r for r in rows if r["model"] == model and r["m"] == m), key=lambda r: r["n"])
            if not pts:
                continue
            fig.add_trace(go.Scatter(x=[p["n"] for p in pts], y=[p["no_condorcet"] for p in pts], mode="lines+markers",
                                     line=dict(color=palette[ms.index(m) % len(palette)], dash=dashes[model], width=2.5), marker=dict(size=6),
                                     name=f"{m} Kandidaten, {C.MODELS[model].split(' (')[0]}", hovertemplate="%{x} Wähler: %{y:.3f}<extra></extra>"))
    ns = sorted({r["n"] for r in rows})
    fig.update_xaxes(title_text="Zahl der Wähler", type="log", tickmode="array", tickvals=ns, ticktext=[str(n) for n in ns])
    fig.update_yaxes(title_text="Anteil ohne Condorcet-Sieger", range=[-0.01, 0.45], tickformat=".0%")
    return _base(fig, height=420)


def build_disagree(rows):
    """Je Profilmodell: wie oft verfehlt jede Regel den Condorcet-Sieger (nur Profile mit Condorcet-Sieger)?"""
    fig = go.Figure()
    models = [C.MODELS[r["model"]].split(" (")[0] for r in rows]
    for key, name in A.RULE_NAMES.items():
        fig.add_trace(go.Bar(x=models, y=[r["miss_condorcet"][key] for r in rows], name=name, marker_color=C.RULE_COLORS[key],
                             text=[f"{100 * r['miss_condorcet'][key]:.0f} %" for r in rows], textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra>" + name + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Anteil der Profile, in denen die Regel den Condorcet-Sieger verfehlt", range=[0, 0.8], tickformat=".0%")
    return _base(fig, height=380)
