"""
Vector5D — contrat de domaine du projet CYBER-VPT.

Invariant fondamental : chaque composante appartient à [0, 1].

Dimensions
----------
d1 : Criticité    — importance opérationnelle de la ressource/cible.
d2 : Entropie     — niveau de désordre informationnel du payload.
d3 : Dynamique temporelle — rythme d'enchaînement des actions (Δt / fréquence).
d4 : Intensité    — portée opérationnelle de l'action.
d5 : Rareté       — écart du porteur par rapport au comportement habituel.

Règles de rejet (vérifiées au constructeur)
--------------------------------------------
- Toute dimension manquante (valeur absente, None) est rejetée.
- Toute valeur non finie (NaN, +inf, -inf) est rejetée.
- Toute valeur hors de [0, 1] est rejetée.

Exemples valides
----------------
>>> Vector5D(0.0, 0.0, 0.0, 0.0, 0.0)   # zéro absolu
>>> Vector5D(1.0, 1.0, 1.0, 1.0, 1.0)   # maximum absolu
>>> Vector5D(0.2, 0.5, 0.8, 0.6, 0.1)   # cas nominal

Exemples invalides
------------------
>>> Vector5D(float('nan'), 0.5, 0.5, 0.5, 0.5)   # NaN → ValueError
>>> Vector5D(float('inf'), 0.5, 0.5, 0.5, 0.5)   # +inf → ValueError
>>> Vector5D(-0.1, 0.5, 0.5, 0.5, 0.5)           # négatif → ValueError
>>> Vector5D(1.1, 0.5, 0.5, 0.5, 0.5)            # supérieur à 1 → ValueError
>>> Vector5D(0.5, 0.5, 0.5, 0.5)                 # 4 dimensions → TypeError
"""

from __future__ import annotations

import math
from typing import Sequence


_DIMS = ("d1", "d2", "d3", "d4", "d5")


class Vector5D:
    """Vecteur métier 5D normalisé dans le cube unité [0, 1]^5.

    Parameters
    ----------
    d1 : float
        Criticité — importance de la cible (∈ [0, 1]).
    d2 : float
        Entropie — niveau de désordre informationnel du payload (∈ [0, 1]).
    d3 : float
        Dynamique temporelle — rythme d'enchaînement des actions (∈ [0, 1]).
    d4 : float
        Intensité — portée opérationnelle de l'action (∈ [0, 1]).
    d5 : float
        Rareté — écart de l'empreinte par rapport au parc habituel (∈ [0, 1]).

    Raises
    ------
    TypeError
        Si une dimension est absente (None) ou si le mauvais nombre d'arguments
        est fourni.
    ValueError
        Si une dimension est non finie (NaN, ±inf) ou hors de [0, 1].
    """

    __slots__ = ("d1", "d2", "d3", "d4", "d5")

    def __init__(
        self,
        d1: float,
        d2: float,
        d3: float,
        d4: float,
        d5: float,
    ) -> None:
        values = (d1, d2, d3, d4, d5)
        for name, value in zip(_DIMS, values):
            _validate_component(name, value)

        self.d1 = float(d1)
        self.d2 = float(d2)
        self.d3 = float(d3)
        self.d4 = float(d4)
        self.d5 = float(d5)

    # ------------------------------------------------------------------
    # Alternative constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_sequence(cls, values: Sequence[float]) -> "Vector5D":
        """Construit un ``Vector5D`` à partir d'une séquence de longueur 5.

        Parameters
        ----------
        values:
            Séquence de cinq flottants dans [0, 1].

        Raises
        ------
        TypeError
            Si la séquence ne contient pas exactement 5 éléments.
        ValueError
            Si une composante est invalide.

        Examples
        --------
        >>> Vector5D.from_sequence([0.1, 0.2, 0.3, 0.4, 0.5])
        Vector5D(d1=0.1, d2=0.2, d3=0.3, d4=0.4, d5=0.5)
        """
        if len(values) != 5:
            raise TypeError(
                f"Un Vector5D requiert exactement 5 dimensions, "
                f"{len(values)} fournie(s)."
            )
        return cls(*values)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Vector5D("
            f"d1={self.d1}, d2={self.d2}, d3={self.d3}, "
            f"d4={self.d4}, d5={self.d5})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector5D):
            return NotImplemented
        return (
            self.d1 == other.d1
            and self.d2 == other.d2
            and self.d3 == other.d3
            and self.d4 == other.d4
            and self.d5 == other.d5
        )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def as_tuple(self) -> tuple[float, float, float, float, float]:
        """Retourne les composantes sous forme de tuple ``(d1, …, d5)``."""
        return (self.d1, self.d2, self.d3, self.d4, self.d5)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_component(name: str, value: object) -> None:
    """Valide une composante de ``Vector5D``.

    Parameters
    ----------
    name:
        Nom de la dimension (utilisé dans le message d'erreur).
    value:
        Valeur à valider.

    Raises
    ------
    TypeError
        Si ``value`` est ``None``.
    ValueError
        Si ``value`` est NaN, ±inf, ou hors de [0, 1].
    """
    if value is None:
        raise TypeError(
            f"La dimension '{name}' est absente (None). "
            "Toutes les cinq dimensions sont obligatoires."
        )

    try:
        fval = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"La dimension '{name}' ne peut pas être convertie en float : "
            f"{value!r}."
        ) from exc

    if math.isnan(fval):
        raise ValueError(
            f"La dimension '{name}' est NaN. "
            "Seules les valeurs finies dans [0, 1] sont acceptées."
        )

    if math.isinf(fval):
        raise ValueError(
            f"La dimension '{name}' est infinie ({value!r}). "
            "Seules les valeurs finies dans [0, 1] sont acceptées."
        )

    if fval < 0.0 or fval > 1.0:
        raise ValueError(
            f"La dimension '{name}' vaut {fval!r}, hors de [0, 1]. "
            "Toutes les dimensions doivent appartenir à l'intervalle [0, 1]."
        )
