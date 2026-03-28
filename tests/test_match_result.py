"""
Tests de contrat pour MatchResult (C-002).

Couvre l'intégralité des règles de rejet et des cas limites valides définis
dans le contrat de domaine (src/cyber_vpt/match_result.py).
"""

import pytest

from src.cyber_vpt.match_result import MatchResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid(**overrides) -> MatchResult:
    """Construit un MatchResult valide avec des valeurs par défaut cohérentes."""
    defaults = dict(
        raw_distance=3.2,
        normalized_distance=0.25,
        match_score=0.75,
        matched_stage=2,
        completion_probability=0.60,
    )
    defaults.update(overrides)
    return MatchResult(**defaults)


# ---------------------------------------------------------------------------
# Cas valide
# ---------------------------------------------------------------------------


class TestMatchResultValidCases:
    """MatchResult doit accepter tout jeu de valeurs cohérent."""

    def test_nominal_case(self):
        """Exemple nominal issu du contrat C-002."""
        mr = _valid()
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

    def test_completion_probability_boundaries(self):
        """completion_probability = 0.0 et 1.0 sont valides."""
        mr0 = _valid(completion_probability=0.0)
        mr1 = _valid(completion_probability=1.0)
        assert mr0.completion_probability == 0.0
        assert mr1.completion_probability == 1.0

    def test_fields_accessible_by_name(self):
        """Tous les champs sont accessibles par attribut."""
        mr = _valid()
        assert hasattr(mr, "raw_distance")
        assert hasattr(mr, "normalized_distance")
        assert hasattr(mr, "match_score")
        assert hasattr(mr, "matched_stage")
        assert hasattr(mr, "completion_probability")

    def test_equality(self):
        """Deux MatchResult identiques doivent être égaux."""
        assert _valid() == _valid()

    def test_inequality(self):
        """Deux MatchResult distincts ne doivent pas être égaux."""
        assert _valid(raw_distance=1.0) != _valid(raw_distance=2.0)


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
                completion_probability=0.60,
            )

    def test_score_mismatch_slight(self):
        """Écart d'1 % — doit également être rejeté."""
        with pytest.raises(ValueError, match="Incoh"):
            MatchResult(
                raw_distance=1.0,
                normalized_distance=0.50,
                match_score=0.51,
                matched_stage=1,
                completion_probability=0.50,
            )

    def test_score_inverted(self):
        """match_score = normalized_distance (inversion) doit être rejeté."""
        with pytest.raises(ValueError, match="Incoh"):
            MatchResult(
                raw_distance=1.0,
                normalized_distance=0.30,
                match_score=0.30,
                matched_stage=0,
                completion_probability=0.30,
            )


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

    def test_cannot_add_new_attribute(self):
        mr = _valid()
        with pytest.raises(AttributeError):
            mr.extra = "x"  # type: ignore[attr-defined]
