"""Gemeinsame Fixtures: Mini-Profile, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def cycle():
    """Das Lehrbuchbeispiel: A > B > C, B > C > A, C > A > B. Paarweise A:B = 2:1, B:C = 2:1, C:A = 2:1 (Zyklus, kein Condorcet-Sieger)."""
    return np.array([[0, 1, 2], [1, 2, 0], [2, 0, 1]])


@pytest.fixture
def seven():
    """7 Wähler, 3 Kandidaten: 3 x A>B>C, 2 x B>C>A, 2 x C>B>A.
    Handrechnung: Erststimmen A 3, B 2, C 2 (Mehrheitswahl: A). Paarweise: B schlägt A (4:3), C schlägt A (4:3), B schlägt C (5:2): Condorcet-Sieger B.
    Borda: A 3*2 = 6, B 3*1 + 2*2 + 2*1 = 9, C 2*1 + 2*2 = 6. Copeland: A 0, B 2, C 1."""
    return np.array([[0, 1, 2]] * 3 + [[1, 2, 0]] * 2 + [[2, 1, 0]] * 2)


@pytest.fixture
def loser_wins():
    """10 Wähler: 4 x A>B>C, 3 x B>C>A, 3 x C>B>A. Mehrheitswahl wählt A (4 Erststimmen), aber A verliert gegen B und C (4:6): A ist der Condorcet-Verlierer, B der Condorcet-Sieger (B:C = 7:3)."""
    return np.array([[0, 1, 2]] * 4 + [[1, 2, 0]] * 3 + [[2, 1, 0]] * 3)
