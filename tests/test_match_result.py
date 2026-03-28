"""
Tests de contrat pour MatchResult (C-002).

Couvre l'intégralité des règles de rejet et des cas limites valides définis
dans le contrat de domaine (src/cyber_vpt/match_result.py).
"""

import math

import pytest

from src.cyber_vpt.match_result import MatchResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid(**overrides) -> MatchResult:
    """Construit un MatchResult valide avec des valeurs par défaut cohérentes.

    completion_probability est omis par défaut pour tester le cas sans valeur.
    """
    defaults = dict(
        raw_distance=3.2,
        normalized_distance=0.25,
        match_score=0.75,
        matched_stage=2,
    )
    defaults.update(overrides)
    return MatchResult(**defaults)


# ---------------------------------------------------------------------------
# Cas valide
# ---------------------------------------------------------------------------


class TestMatchResultValidCases:
    """MatchResult doit accepter tout jeu de valeurs cohérent."""

    def test_nominal_case_without_completion_probability(self):
        """Sans completion_probability : champ vaut None."""
        mr = _valid()
        assert mr.raw_distance == pytest.approx(3.2)
        assert mr.normalized_distance == pytest.approx(0.25)
        assert mr.match_score == pytest.approx(0.75)
        assert mr.matched_stage == 2
        assert mr.completion_probability is None

    def test_nominal_case_with_completion_probability(self):
        """Exemple nominal issu du contrat C-002 avec completion_probability."""
        mr = _valid(completion_probability=0.60)
        assert mr.raw_distance == pytest.approx(3.2)
        assert mr.normalized_distance == pytest.approx(0.25)
        assert mr.match_score == pytest.approx(0.75)
        assert mr.matched_stage == 2
        assert mr.completion_probability == pytest.approx(0.60)

    def test_boundary_zero(self):
        """Bornes inférieures : normalized_distance = 0, match_score = 1."""
        mr = _valid(normalized_distance=0.0, match_score=1.0)
        assert mr.normalized_distance == 0.0
        assert mr.match_score == 1.0

    def test_boundary_one(self):
        """Bornes supérieures : normalized_distance = 1, match_score = 0."""
        mr = _valid(normalized_distance=1.0, match_score=0.0)
        assert mr.normalized_distance == 1.0
        assert mr.match_score == 0.0

    def test_raw_distance_zero(self):
        """raw_distance = 0 est valide (correspondance parfaite)."""
        mr = _valid(raw_distance=0.0, normalized_distance=0.0, match_score=1.0)
        assert mr.raw_distance == 0.0

    def test_matched_stage_zero(self):
        """matched_stage = 0 est valide (première étape)."""
        mr = _valid(matched_stage=0)
        assert mr.matched_stage == 0

    def test_completion_probability_zero(self):
        """completion_probability = 0.0 est valide."""
        mr = _valid(completion_probability=0.0)
        assert mr.completion_probability == 0.0

    def test_completion_probability_one(self):
        """completion_probability = 1.0 est valide."""
        mr = _valid(completion_probability=1.0)
        assert mr.completion_probability == 1.0

    def test_completion_probability_none_explicit(self):
        """completion_probability = None explicite est valide."""
        mr = _valid(completion_probability=None)
        assert mr.completion_probability is None

    def test_fields_accessible_by_name(self):
        """Tous les champs sont accessibles par attribut."""
        mr = _valid()
        assert hasattr(mr, "raw_distance")
        assert hasattr(mr, "normalized_distance")
        assert hasattr(mr, "match_score")
        assert hasattr(mr, "matched_stage")
        assert hasattr(mr, "completion_probability")

    def test_equality_without_completion_probability(self):
        """Deux MatchResult sans completion_probability identiques sont égaux."""
        assert _valid() == _valid()

    def test_equality_with_completion_probability(self):
        """Deux MatchResult avec completion_probability identique sont égaux."""
        assert _valid(completion_probability=0.5) == _valid(completion_probability=0.5)

    def test_inequality(self):
        """Deux MatchResult distincts ne doivent pas être égaux."""
        assert _valid(raw_distance=1.0) != _valid(raw_distance=2.0)

    def test_score_coherence_at_boundary_zero(self):
        """Cohérence stricte à la borne 0 : nd=0 => score=1."""
        mr = _valid(normalized_distance=0.0, match_score=1.0)
        assert mr.match_score == pytest.approx(1.0 - mr.normalized_distance)

    def test_score_coherence_at_boundary_one(self):
        """Cohérence stricte à la borne 1 : nd=1 => score=0."""
        mr = _valid(normalized_distance=1.0, match_score=0.0)
        assert mr.match_score == pytest.approx(1.0 - mr.normalized_distance)

    def test_score_coherence_midpoint(self):
        """Cohérence stricte au milieu : nd=0.5 => score=0.5."""
        mr = _valid(normalized_distance=0.5, match_score=0.5)
        assert mr.match_score == pytest.approx(1.0 - mr.normalized_distance)

    def test_inequality_completion_probability_none_vs_value(self):
        """None != 0.5 pour completion_probability."""
        assert _valid() != _valid(completion_probability=0.5)


# ---------------------------------------------------------------------------
# Rejet — raw_distance < 0
# ---------------------------------------------------------------------------


class TestMatchResultRejectsNegativeRawDistance:
    """raw_distance < 0 doit lever ValueError."""

    def test_raw_distance_negative_small(self):
        with pytest.raises(ValueError, match="distance brute"):
            _valid(raw_distance=-0.001)

    def test_raw_distance_negative_large(self):
        with pytest.raises(ValueError, match="distance brute"):
            _valid(raw_distance=-100.0)


# ---------------------------------------------------------------------------
# Rejet — NaN et ±inf pour raw_distance
# ---------------------------------------------------------------------------


class TestMatchResultRejectsNonFiniteRawDistance:
    """raw_distance NaN ou ±inf doit lever ValueError."""

    def test_raw_distance_nan(self):
        with pytest.raises(ValueError, match="NaN"):
            _valid(raw_distance=float("nan"))

    def test_raw_distance_pos_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(raw_distance=float("inf"))

    def test_raw_distance_neg_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(raw_distance=float("-inf"))


# ---------------------------------------------------------------------------
# Rejet — normalized_distance hors [0, 1]
# ---------------------------------------------------------------------------


class TestMatchResultRejectsInvalidNormalizedDistance:
    """normalized_distance hors [0, 1] doit lever ValueError."""

    def test_normalized_distance_above_one(self):
        with pytest.raises(ValueError, match="normalized_distance"):
            _valid(normalized_distance=1.3, match_score=-0.3)

    def test_normalized_distance_slightly_above_one(self):
        with pytest.raises(ValueError, match="normalized_distance"):
            _valid(normalized_distance=1.001, match_score=-0.001)

    def test_normalized_distance_below_zero(self):
        with pytest.raises(ValueError, match="normalized_distance"):
            _valid(normalized_distance=-0.1, match_score=1.1)

    def test_normalized_distance_negative(self):
        with pytest.raises(ValueError, match="normalized_distance"):
            _valid(normalized_distance=-1.0, match_score=2.0)


# ---------------------------------------------------------------------------
# Rejet — NaN et ±inf pour normalized_distance
# ---------------------------------------------------------------------------


class TestMatchResultRejectsNonFiniteNormalizedDistance:
    """normalized_distance NaN ou ±inf doit lever ValueError."""

    def test_normalized_distance_nan(self):
        with pytest.raises(ValueError, match="NaN"):
            _valid(normalized_distance=float("nan"), match_score=0.5)

    def test_normalized_distance_pos_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(normalized_distance=float("inf"), match_score=0.5)

    def test_normalized_distance_neg_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(normalized_distance=float("-inf"), match_score=0.5)


# ---------------------------------------------------------------------------
# Rejet — match_score hors [0, 1]
# ---------------------------------------------------------------------------


class TestMatchResultRejectsInvalidMatchScore:
    """match_score hors [0, 1] doit lever ValueError."""

    def test_match_score_above_one(self):
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            _valid(normalized_distance=0.0, match_score=1.5)

    def test_match_score_below_zero(self):
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            _valid(normalized_distance=1.0, match_score=-0.5)


# ---------------------------------------------------------------------------
# Rejet — NaN et ±inf pour match_score
# ---------------------------------------------------------------------------


class TestMatchResultRejectsNonFiniteMatchScore:
    """match_score NaN ou ±inf doit lever ValueError."""

    def test_match_score_nan(self):
        with pytest.raises(ValueError, match="NaN"):
            _valid(match_score=float("nan"))

    def test_match_score_pos_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(match_score=float("inf"))

    def test_match_score_neg_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(match_score=float("-inf"))


# ---------------------------------------------------------------------------
# Rejet — incohérence match_score / normalized_distance
# ---------------------------------------------------------------------------


class TestMatchResultRejectsIncoherentScore:
    """match_score != 1 - normalized_distance doit lever ValueError."""

    def test_score_mismatch_typical(self):
        """Exemple canonique du contrat : nd=0.25, score=0.60 au lieu de 0.75."""
        with pytest.raises(ValueError, match="Incoh"):
            MatchResult(
                raw_distance=3.2,
                normalized_distance=0.25,
                match_score=0.60,
                matched_stage=2,
            )

    def test_score_mismatch_slight(self):
        """Écart d'1 % — doit également être rejeté."""
        with pytest.raises(ValueError, match="Incoh"):
            MatchResult(
                raw_distance=1.0,
                normalized_distance=0.50,
                match_score=0.51,
                matched_stage=1,
            )

    def test_score_inverted(self):
        """match_score = normalized_distance (inversion) doit être rejeté."""
        with pytest.raises(ValueError, match="Incoh"):
            MatchResult(
                raw_distance=1.0,
                normalized_distance=0.30,
                match_score=0.30,
                matched_stage=0,
            )


# ---------------------------------------------------------------------------
# Rejet — completion_probability invalide (si renseignée)
# ---------------------------------------------------------------------------


class TestMatchResultRejectsInvalidCompletionProbability:
    """completion_probability renseignée mais invalide doit lever ValueError."""

    def test_completion_probability_above_one(self):
        with pytest.raises(ValueError, match="completion_probability"):
            _valid(completion_probability=1.1)

    def test_completion_probability_below_zero(self):
        with pytest.raises(ValueError, match="completion_probability"):
            _valid(completion_probability=-0.1)

    def test_completion_probability_nan(self):
        with pytest.raises(ValueError, match="NaN"):
            _valid(completion_probability=float("nan"))

    def test_completion_probability_pos_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(completion_probability=float("inf"))

    def test_completion_probability_neg_inf(self):
        with pytest.raises(ValueError, match="infini"):
            _valid(completion_probability=float("-inf"))


# ---------------------------------------------------------------------------
# Bornes exactes 0 et 1 pour normalized_distance / match_score
# ---------------------------------------------------------------------------


class TestMatchResultExactBounds:
    """Les bornes exactes 0 et 1 doivent être acceptées."""

    def test_zero_distance_score_one(self):
        mr = _valid(normalized_distance=0.0, match_score=1.0)
        assert mr.normalized_distance == 0.0
        assert mr.match_score == 1.0

    def test_max_distance_score_zero(self):
        mr = _valid(normalized_distance=1.0, match_score=0.0)
        assert mr.normalized_distance == 1.0
        assert mr.match_score == 0.0


# ---------------------------------------------------------------------------
# Immutabilité
# ---------------------------------------------------------------------------


class TestMatchResultIsImmutable:
    """MatchResult doit être immuable après construction."""

    def test_cannot_modify_raw_distance(self):
        mr = _valid()
        with pytest.raises(AttributeError):
            mr.raw_distance = 0.0  # type: ignore[misc]

    def test_cannot_modify_normalized_distance(self):
        mr = _valid()
        with pytest.raises(AttributeError):
            mr.normalized_distance = 0.5  # type: ignore[misc]

    def test_cannot_modify_match_score(self):
        mr = _valid()
        with pytest.raises(AttributeError):
            mr.match_score = 0.5  # type: ignore[misc]

    def test_cannot_modify_matched_stage(self):
        mr = _valid()
        with pytest.raises(AttributeError):
            mr.matched_stage = 5  # type: ignore[misc]

    def test_cannot_modify_completion_probability(self):
        mr = _valid(completion_probability=0.5)
        with pytest.raises(AttributeError):
            mr.completion_probability = 0.9  # type: ignore[misc]

    def test_cannot_add_new_attribute(self):
        mr = _valid()
        with pytest.raises(AttributeError):
            mr.extra = "x"  # type: ignore[attr-defined]

