# Wahlregeln im Vergleich: wer gewinnt, wenn alle Recht haben? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-wahlregeln-demo.streamlit.app/)** -->

Erstes Stück der Linie **Abstimmen und Fair Teilen** (Konzepte-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“). Ein Gremium soll **einen** Lieferanten oder Kandidaten wählen, und jedes Mitglied hat eine **Rangfolge**.
Es gibt keine „richtige“ Antwort, nur eine **Regel**, die aus den Rangfolgen einen Sieger macht. Die Demo wendet vier Regeln auf **dieselben Profile** an und fragt: **Wählen sie denselben Sieger, und wie oft gibt es gar keinen Kandidaten, der alle anderen mit Mehrheit schlägt?**
Abgrenzung: `rangaggregation-demo` (Ranking-Linie) führt Rangfolgen mit einer **wahren Ordnung** und Rauschen zusammen (Ziel: die Wahrheit treffen); hier gibt es keine Wahrheit, jeder Wähler hat Recht. Stabile Zuordnungen mit Präferenzen (Gale–Shapley und Verwandte) stehen in der Matching-Linie, zum Beispiel in [gale-shapley-demo](https://github.com/sebastian-hanisch/gale-shapley-demo).

Der Kern ist eigener Code (`numpy`): Mehrheitswahl, Borda-Zählung, Copeland und Sofortstichwahl, drei Profilmodelle, ein exakter Rechenweg für kleine Fälle.

## Warum dieses Problem

Wer „einfach abstimmen lässt“, hat die Regel schon gewählt. Dieselben Stimmzettel können, je nach Zählweise, verschiedene Sieger ergeben, und manchmal gibt es gar keinen Kandidaten, der gegen jeden anderen gewinnt (**Condorcet-Paradoxon**: A schlägt B, B schlägt C, C schlägt A).
Die Demo misst beides auf Profilen, deren Aufbau sie offenlegt, und zeigt dabei: **Das Ergebnis hängt vom Profilmodell ab**, nicht nur von der Regel.

## Modell

**Profil.** n Wähler, m Kandidaten; jeder Wähler hat eine strikte Rangfolge. Drei Profilmodelle: **Zufall** (jeder Wähler zieht eine der m! Rangfolgen mit gleicher Wahrscheinlichkeit), **einspitzig** (Kandidaten auf einer Achse, jeder Wähler reiht nach Abstand zu seinem Idealpunkt), **zwei Lager** (55 % streuen um die Rangfolge A > B > C …, 45 % um die umgekehrte, Streuung nach dem Mallows-Modell mit φ = 0,7).
**Regeln.** Mehrheitswahl: wer die meisten Erststimmen hat. Borda: der erste Platz bringt m − 1 Punkte, der letzte 0. Copeland: je gewonnenem Paarvergleich 1 Punkt, je Gleichstand 0,5. Sofortstichwahl (IRV): der Kandidat mit den wenigsten Erststimmen unter den Lebenden scheidet aus, bis einer bleibt.
**Condorcet-Sieger:** gewinnt jeden Paarvergleich mit Mehrheit; es gibt höchstens einen. **Gleichstand:** ein Zufallslos aus dem Zufalls-Seed legt vorab eine Rangfolge der Kandidaten fest; bei der Sofortstichwahl scheidet unter mehreren Letzten der am wenigsten bevorzugte aus.
Die Wählerzahl ist immer ungerade (zwischen zwei Kandidaten gibt es dann keinen Gleichstand). Formeln und Lesehilfe stehen im 📐-Expander der App.

## Methodik

- **Kern** (`wrg_algorithm.py`): Profile erzeugen (Zufall, einspitzig, Mallows-Lager), Paarzählung, vier Regeln, Condorcet-Sieger und -Verlierer, Sofortstichwahl mit Runden, exakte Wahrscheinlichkeit ohne Condorcet-Sieger bei drei Kandidaten.
- **Szenario und Auswertung** (`wrg_scenario.py`, `wrg_evaluation.py`): Profil und Gleichstandslos aus (Modell, m, n, Zufalls-Seed), Analyse je Einstellung, zwei Messreihen mit festem Programm, alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): fünf Schnellstart-Szenarien, Regler für Profilmodell, Kandidaten, Wähler und Zufalls-Seed, Kennzahlen je Regel, Paarmehrheiten als Karte, die Runden der Sofortstichwahl, das Lehrbuchbeispiel mit drei Wählern, zwei Messreihen auf Klick, Annahmen und Formeln.
- **Messreihen:** je Zelle 400 Profile mit den Zufalls-Seeds 100000 bis 100399, alle drei Profilmodelle; Reihe 1: Kandidaten 3 bis 6, Wähler 11, 51, 201; Reihe 2: 4 Kandidaten, 51 Wähler.

## Befunde (gemessen, keine Behauptungen)

Alle Reihen mit festen Zufalls-Seeds (je Zelle 400 Profile; die Standardabweichung eines Anteils liegt bei höchstens 2,5 Prozentpunkten). Die Schnellstart-Szenarien sind Einzelprofile, **von Hand ausgesucht** (siehe unten). **Die Zufallszahlen eines `numpy`-Generators sind nicht über Versionen stabil**: die Tests prüfen deshalb Bänder um diese Zahlen.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Alle Regeln, Paarzählung, Condorcet-Sieger und -Verlierer gleich einer Neuimplementierung mit einfachen Schleifen auf 240 Zufallsprofilen aller drei Modelle; die exakte Wahrscheinlichkeit ohne Condorcet-Sieger gleich der Aufzählung aller 6ⁿ Profile bei n = 3 und 5 (5,556 % und 6,944 %) und gleich der Simulation; die Mallows-Ziehung gleich φ^(Fehlstände) / Z (Chi-Quadrat); einspitzige Profile haben immer einen Condorcet-Sieger, und zwar den Kandidaten beim mittleren Wähler. | `tests/test_oracle_wahlregeln.py` |
| Wie oft gibt es keinen Condorcet-Sieger? | Zufallsprofil, drei Kandidaten, exakt: **5,6 %** (n = 3), **6,9 %** (5), **7,5 %** (7), **8,0 %** (11), **8,4 %** (21): der Anteil steigt mit der Wählerzahl auf einen Grenzwert (etwa 8,8 %, aus dem Gedächtnis, nicht im Original geprüft). Mit mehr Kandidaten wird er größer: bei 51 Wählern **8,2 %, 20,0 %, 24,5 %, 31,8 %** für 3, 4, 5, 6 Kandidaten. | `test_claims.py::test_exact_probabilities_without_a_condorcet_winner_for_three_candidates`, `::test_the_paradox_grows_with_the_number_of_candidates_under_random_profiles` |
| Hängt das vom Profilmodell ab? | **Einspitzig: in allen 12 Zellen 0,0 %**, nie ein Zyklus (Medianwähler). Zwei Lager: 6,8 bis 33,8 %, bei vier Kandidaten fällt der Anteil von 22,2 % (11 Wähler) auf 14,8 % (201), bei sechs von 33,8 % auf 29,8 %: bei zwei Lagern bringen mehr Wähler die Lager klarer hervor, und der Zyklus wird seltener. Zufall m = 5: 20,5 / 24,5 / 28,7 % für 11 / 51 / 201 Wähler. | `test_claims.py::test_single_peaked_profiles_never_have_a_cycle`, `::test_two_camps_have_cycles_that_depend_on_the_number_of_voters` |
| Wie oft widersprechen sich die Regeln? | 4 Kandidaten, 51 Wähler: in **46,8 %** der Zufallsprofile küren mindestens zwei Regeln verschiedene Sieger, bei einspitzigen Profilen in **61,0 %**, bei zwei Lagern in 42,5 %. | `test_claims.py::test_rules_disagree_in_about_half_of_the_profiles` |
| Welche Regel verfehlt den Condorcet-Sieger? | Wenn es einen gibt: **Copeland nie** (0,0 %, ein Satz: der Condorcet-Sieger hat m − 1 Siege), Borda 13,1 %, Sofortstichwahl 6,9 %, **Mehrheitswahl 29,7 %** (Zufall); einspitzig: Mehrheitswahl **59,5 %**, Sofortstichwahl **38,5 %**, Borda 11,2 %; zwei Lager: 28,7 / 8,7 / 8,1 %. | `test_claims.py::test_plurality_misses_the_condorcet_winner_most_often`, `::test_single_peaked_profiles_make_the_sofortstichwahl_miss_the_median_candidate_more_often` |
| Wählt eine Regel den Condorcet-Verlierer? | **Borda, Copeland und Sofortstichwahl nie** (0,0 % über alle 1 200 Profile je Regel), die **Mehrheitswahl** in 1,8 % der Zufallsprofile und in **6,5 %** der einspitzigen: der Kandidat mit den meisten Erststimmen kann gegen jeden anderen verlieren. | `test_claims.py::test_copeland_always_picks_an_existing_condorcet_winner_and_borda_irv_never_pick_the_loser`, `::test_plurality_picks_the_condorcet_loser_sometimes` |
| Schnellstart-Szenarien | Drei Kandidaten, 51 Wähler, Zufalls-Seed 3: Condorcet-Sieger B; Mehrheitswahl und Borda wählen C, Copeland und Sofortstichwahl B. Fünf Kandidaten, 201 Wähler: drei verschiedene Sieger (A, C, D), Condorcet-Sieger C. Einspitzig: Condorcet-Sieger C (mitte), Mehrheitswahl und Sofortstichwahl D. Zwei Lager, Zufalls-Seed 1: Kompromisskandidat B gewinnt bei Borda, Copeland, Sofortstichwahl und ist Condorcet-Sieger, die Mehrheitswahl wählt A. Sieben Wähler, Zufalls-Seed 8: Zyklus, kein Condorcet-Sieger. | `test_claims.py::test_the_presets_tell_the_stories_in_their_help_texts`, `test_presets.py` |

## Ehrliche Grenzen

- **Die Profile sind Modelle, keine Daten.** Das Zufallsprofil (jede Rangfolge gleich wahrscheinlich) ist **unrealistisch**, weil echte Wähler selten völlig ungeordnet urteilen; es liefert die obere Grenze für Zyklen. Einspitzig und zwei Lager sind Gegenpole. Echte Präferenzen liegen dazwischen, und diese Demo misst sie nicht.
- **Die Schnellstart-Szenarien sind ausgesucht.** Die Zufalls-Seeds sind so gewählt, dass die Beispiele ihre Geschichte erzählen (die Regeln gehen auseinander, es gibt einen Kompromiss, es gibt einen Zyklus). Die Häufigkeit steht in den Messreihen, nicht in den Beispielen: bei drei Kandidaten und 51 Wählern fehlt der Condorcet-Sieger nur in etwa 8 % der Zufallsprofile.
- **Anteile sind grob.** 400 Profile je Zelle, Standardabweichung bis 2,5 Prozentpunkte; kleine Unterschiede zwischen Zellen sind kein Befund (bei drei Kandidaten und 11 Wählern liefert die Simulation 7,0 %, exakt sind 8,0 %). Wer Prozentpunkte vergleichen will, braucht mehr Profile.
- **Gleichstand per Los.** Bei kleinen Wählerzahlen entscheidet das Los öfter, das Ergebnis hängt dann am Zufalls-Seed. Bei der Sofortstichwahl gibt es mehrere Gleichstandsregeln in der Literatur; hier scheidet der am wenigsten bevorzugte unter den Letzten aus.
- **Ehrliche Wähler.** Alle Wähler geben ihre wahre Rangfolge an; taktisches Wählen ist nicht Teil dieser Demo. Auch Rangfolgen mit offenen Plätzen oder Gleichständen und gewichtete Stimmen gibt es nicht.
- **Eigener Code ohne Bibliotheksorakel.** Die Neuimplementierung der Regeln in den Tests ist wieder eigener Code, nur auf andere Weise gerechnet; die Rechenwege sind unabhängig, aber nicht gegen eine fremde Bibliothek geprüft.
- **Grenzwert und Literatur** (Condorcet 1785, Borda 1781, Copeland 1951, Black 1948, Arrow 1951, Gehrlein zum Grenzwert 8,8 %; Überblick: Brandt u. a., *Handbook of Computational Social Choice*, 2016) aus dem Gedächtnis, nicht im Original geprüft.

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9188 (im Plan nicht vergeben; 9170 bis 9187 sind belegt).
- **Kandidatenzahl ab 2:** die Reglerspanne beginnt bei 2 statt 3, damit die Voreinstellung (3 Kandidaten) nicht auf dem Reglerrand liegt; bei zwei Kandidaten gibt es nie Streit zwischen den Regeln (jede Regel wählt die Mehrheit).
- **Zwei Lager statt 60 : 40 und φ = 0,5:** die ersten Parameter lieferten fast immer denselben Sieger bei allen vier Regeln (das größere Lager gewinnt überall). Bei 55 : 45 und φ = 0,7 ist die Mehrheitswahl in 52 % der Profile anderer Meinung als Borda (150 Profile, Kandidaten 5, Wähler 101, Vorprobe) und Borda wählt in 63 % einen mittleren Kandidaten.
- **Vormessung gegen die App:** der Plan nannte 3 000 Profile je Zelle (Vormessung S1: 5,6 / 8,8 / 7,8 / 8,2 % für 3 Kandidaten); die App rechnet 400 Profile je Zelle (7,0 / 8,2 / 10,2 %), das ist innerhalb der Schwankung, die exakten Werte stehen im Befund oben.
- **Namen:** die Stichwahl-Sukzession des Plans heißt in der App **Sofortstichwahl (IRV)**.

## Verifikation

- **Kern:** jede Einheit an einem Mini-Profil von Hand (Zyklus mit drei Wählern, 7 Wähler mit Condorcet-Sieger B und Mehrheitswahl-Sieger A, 10 Wähler mit Mehrheitswahl-Sieger als Condorcet-Verlierer; Sofortstichwahl Runde für Runde mit beiden Gleichstandslosen), Randfälle (ein Wähler, zwei Kandidaten, lauter gleiche Wähler, vollständige Symmetrie, ungültige Eingaben, kleinste und größte Reglerwerte für jedes Modell).
- **Orakel:** Neuimplementierung der Regeln mit Schleifen auf 240 Profilen, Aufzählung aller 6ⁿ Profile, exakte Wahrscheinlichkeit gegen Simulation (Vier-Sigma-Band), Chi-Quadrat der Mallows-Verteilung, Sätze als Eigenschaftstests (Condorcet-Sieger ist eindeutig und gewinnt Copeland; Summen der Punkte).
- **Verdikte:** reine Funktionen, jeder Zweig (Zyklus mit Einigkeit und ohne, Regeln uneinig mit Condorcet-Sieger, alle einig) und jede Zahl im Text an handgesetzten Profilen (`tests/test_verdicts.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich und auf dem Raster der Regler, keines auf einem Reglerrand, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern); die Presets erzählen ihre Geschichte (Zyklus, Kompromiss, mittlerer Sieger) im Test.
- **Mutationsprüfung** (`tools/mutate_demo.py`): 62 Stellen im Kern `wrg_algorithm.py`, **57 gefangen**, 5 als äquivalent festgehalten, keine Zeitüberschreitung. Der erste Lauf ließ genau diese 5 überleben, keine echte Lücke: in `exact_no_condorcet_probability` und in `pairwise` verwechselt `<` mit `<=` nur gleiche Kandidaten (a = b ist ausgeschlossen oder die Diagonale wird danach genullt); in `irv` ist der Wert für ausgeschiedene Kandidaten (`m + 1`) nur größer als jeder Rangplatz, `m` und `m + 2` leisten dasselbe (zwei Mutanten); in `profile_single_peaked` ist das Vorzeichen des winzigen Zufallsrauschens (1e-9) für das Brechen von Gleichständen gleichgültig.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `wrg_algorithm.py` | Kern: Profile, Regeln, Condorcet, exakte Wahrscheinlichkeit |
| `wrg_constants.py` | Regler-Grenzen, feste Pläne, Farben, Presets |
| `wrg_evaluation.py` | Analyse, Messreihen, Verdikte, Tabellen |
| `wrg_layout.py` | Fester Kopf (Stylesheet) |
| `wrg_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `wrg_scenario.py` | Profil und Gleichstandslos aus (Modell, m, n, Zufalls-Seed) |
| `wrg_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Profile, Kern, Orakel, Verdikte, Randfälle, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe, Claims |

## Bewusst nicht umgesetzt

- **Taktisches Wählen:** jeder Wähler gibt seine wahre Rangfolge an; die Manipulierbarkeit der Regeln ist eine eigene Frage.
- **Weitere Condorcet-Verfahren** (Schulze, Ranked Pairs, Kemeny) und **zweistufige Wahlverfahren:** die Rangaggregation mit Kemeny steht in `rangaggregation-demo`.
- **Unvollständige Stimmzettel, Gleichstände in den Rangfolgen, gewichtete Stimmen:** würden jede Regel ändern.
- **Echte Wahl- oder Umfragedaten:** nur synthetische Profile (Datenschutz, Positionierung).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
