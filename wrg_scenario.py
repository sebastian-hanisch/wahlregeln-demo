"""Szenario: ein Profil und das Gleichstandslos aus Profilmodell, Kandidaten- und Wählerzahl und Zufalls-Seed."""

from __future__ import annotations

import numpy as np

import wrg_algorithm as A


def make_profile(model: str, m: int, n: int, seed: int):
    """Profil (n, m) und Gleichstandsrangfolge (m,); beide hängen nur von (model, m, n, seed) ab."""
    if model not in A.PROFILE_MODELS:
        raise ValueError(f"unbekanntes Profilmodell: {model}")
    if m < 2 or n < 1:
        raise ValueError("mindestens zwei Kandidaten und ein Wähler")
    rng = np.random.default_rng(seed)
    profile = A.PROFILE_MODELS[model](n, m, rng)
    tiebreak = rng.permutation(m)
    return profile, tiebreak
