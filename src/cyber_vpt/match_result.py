"""
MatchResult — contrat de domaine du projet CYBER-VPT (C-002).

Invariants fondamentaux
-----------------------
- raw_distance >= 0 et fini (ni NaN ni ±inf)
- normalized_distance ∈ [0, 1] et fini
- match_score ∈ [0, 1] et fini
- match_score = 1 - normalized_distance  (à 1 ULP près)
- completion_probability, si renseignée, ∈ [0, 1] et fini

Description des champs
-----------------------
raw_distance         : distance DTW brute (≥ 0).
normalized_distance  : distance normalisée dans [0, 1].
match_score          : score de correspondance dans [0, 1], égal à
                       ``1 - normalized_distance``.
matched_stage        : indice (entier ≥ 0) de l'étape la mieux alignée
                       dans la séquence de référence.
completion_probability : fraction d'avancement estimée de l'attaque, dans
                         [0, 1] (optionnel — None si non renseignée).
                         **Avertissement :** il s'agit d'une estimation
                         heuristique, non d'une preuve juridique d'intention
                         malveillante.

Rejets obligatoires
-------------------
- raw_distance non fini (NaN, ±inf) ou < 0
- normalized_distance non fini ou hors [0, 1]
- match_score non fini ou hors [0, 1]
- incohérence match_score != 1 - normalized_distance
- matched_stage < 0 ou non entier
- completion_probability renseignée mais non finie ou hors [0, 1]

Exemples valides
----------------
>>> MatchResult(
...     raw_distance=3.2,
...     normalized_distance=0.25,
...     match_score=0.75,
...     matched_stage=2,
... )

>>> MatchResult(
...     raw_distance=3.2,
...     normalized_distance=0.25,
...     match_score=0.75,
...     matched_stage=2,
...     completion_probability=0.60,
... )

Exemples invalides
------------------
>>> MatchResult(raw_distance=-1.0, ...)          # raw_distance < 0
>>> MatchResult(normalized_distance=1.3, ...)    # hors [0, 1]
>>> MatchResult(normalized_distance=0.25,
...             match_score=0.60, ...)           # incohérence
"""

from __future__ import annotations

import math
from typing import Optional

# Tolérance pour la vérification match_score == 1 - normalized_distance.
# Couvre les erreurs d'arrondi flottant standard (IEEE 754).
_SCORE_TOLERANCE = 1e-9


class MatchResult:
    """Résultat immuable d'un rapprochement DTW entre une trajectoire et un modèle.

    Parameters
    ----------
    raw_distance : float
        Distance DTW brute (≥ 0, finie).
    normalized_distance : float
        Distance normalisée dans [0, 1] (finie).
    match_score : float
        Score de correspondance dans [0, 1] (fini), doit être égal à
        ``1 - normalized_distance``.
    matched_stage : int
        Indice (≥ 0) de l'étape la mieux alignée dans le modèle de référence.
    completion_probability : float or None, optional
        Fraction d'avancement estimée de l'attaque, dans [0, 1] (finie).
        Si non renseignée, vaut ``None``.
        **Avertissement :** il s'agit d'une estimation heuristique, non d'une
        preuve juridique d'intention malveillante.

    Raises
    ------
    TypeError
        Si ``matched_stage`` n'est pas un entier.
    ValueError
        Si un invariant du contrat C-002 est violé.
    AttributeError
        Si l'on tente de modifier un champ après construction.
    """

    __slots__ = (
        "raw_distance",
        "normalized_distance",
        "match_score",
        "matched_stage",
        "completion_probability",
    )

    def __init__(
        self,
        raw_distance: float,
        normalized_distance: float,
        match_score: float,
        matched_stage: int,
        completion_probability: Optional[float] = None,
    ) -> None:
        _validate_raw_distance(raw_distance)
        _validate_unit_interval("normalized_distance", normalized_distance)
        _validate_unit_interval("match_score", match_score)
        _validate_score_coherence(normalized_distance, match_score)
        _validate_matched_stage(matched_stage)
        if completion_probability is not None:
            _validate_unit_interval("completion_probability", completion_probability)

        object.__setattr__(self, "raw_distance", float(raw_distance))
        object.__setattr__(self, "normalized_distance", float(normalized_distance))
        object.__setattr__(self, "match_score", float(match_score))
        object.__setattr__(self, "matched_stage", int(matched_stage))
        object.__setattr__(
            self,
            "completion_probability",
            float(completion_probability) if completion_probability is not None else None,
        )

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(
            "MatchResult est immuable : les champs ne peuvent pas être modifiés "
            "après construction."
        )

    def __repr__(self) -> str:
        cp = self.completion_probability
        cp_repr = repr(cp) if cp is not None else "None"
        return (
            f"MatchResult("
            f"raw_distance={self.raw_distance!r}, "
            f"normalized_distance={self.normalized_distance!r}, "
            f"match_score={self.match_score!r}, "
            f"matched_stage={self.matched_stage!r}, "
            f"completion_probability={cp_repr})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MatchResult):
            return NotImplemented
        return (
            self.raw_distance == other.raw_distance
            and self.normalized_distance == other.normalized_distance
            and self.match_score == other.match_score
            and self.matched_stage == other.matched_stage
            and self.completion_probability == other.completion_probability
        )


# ---------------------------------------------------------------------------
# Helpers de validation internes
# ---------------------------------------------------------------------------


def _validate_raw_distance(value: object) -> None:
    """Vérifie que raw_distance est un flottant fini ≥ 0.

    Raises
    ------
    ValueError
        Si la valeur est non finie ou négative.
    """
    fval = _to_finite_float("raw_distance", value)
    if fval < 0.0:
        raise ValueError(
            f"raw_distance vaut {fval!r} : la distance brute doit être ≥ 0."
        )


def _validate_unit_interval(name: str, value: object) -> None:
    """Vérifie qu'une valeur est un flottant fini dans [0, 1].

    Raises
    ------
    ValueError
        Si la valeur est hors de [0, 1] ou non finie.
    """
    fval = _to_finite_float(name, value)
    if fval < 0.0 or fval > 1.0:
        raise ValueError(
            f"'{name}' vaut {fval!r}, hors de [0, 1]. "
            "La valeur doit appartenir à l'intervalle [0, 1]."
        )


def _validate_score_coherence(
    normalized_distance: object, match_score: object
) -> None:
    """Vérifie que match_score == 1 - normalized_distance (à _SCORE_TOLERANCE près).

    Raises
    ------
    ValueError
        Si l'écart dépasse la tolérance numérique.
    """
    nd = float(normalized_distance)  # type: ignore[arg-type]
    ms = float(match_score)  # type: ignore[arg-type]
    expected = 1.0 - nd
    if abs(ms - expected) > _SCORE_TOLERANCE:
        raise ValueError(
            f"Incohérence : match_score={ms!r} mais "
            f"1 - normalized_distance = {expected!r}. "
            "Le score doit être exactement égal à 1 - normalized_distance."
        )


def _validate_matched_stage(value: object) -> None:
    """Vérifie que matched_stage est un entier ≥ 0.

    Raises
    ------
    TypeError
        Si la valeur n'est pas un entier (ou assimilable à un entier).
    ValueError
        Si la valeur est négative.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(
            f"matched_stage doit être un entier, reçu : {type(value).__name__!r}."
        )
    if value < 0:
        raise ValueError(
            f"matched_stage vaut {value!r} : l'indice d'étape doit être ≥ 0."
        )


def _to_finite_float(name: str, value: object) -> float:
    """Convertit ``value`` en float et rejette NaN / ±inf.

    Raises
    ------
    TypeError
        Si la conversion est impossible ou si la valeur est None.
    ValueError
        Si la valeur est NaN ou infinie.
    """
    if value is None:
        raise TypeError(
            f"Le champ '{name}' est None ; une valeur numérique finie est attendue."
        )
    try:
        fval = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"Le champ '{name}' ne peut pas être converti en float : {value!r}."
        ) from exc
    if math.isnan(fval):
        raise ValueError(
            f"Le champ '{name}' est NaN ; seules les valeurs finies sont acceptées."
        )
    if math.isinf(fval):
        raise ValueError(
            f"Le champ '{name}' est infini ({value!r}) ; "
            "seules les valeurs finies sont acceptées."
        )
    return fval
