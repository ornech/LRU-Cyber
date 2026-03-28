"""
Tests de contrat pour Vector5D.

Couvre l'intégralité des règles de rejet et les cas limites valides définis
dans le contrat de domaine (src/cyber_vpt/vector5d.py).
"""

import math

import pytest

from src.cyber_vpt.vector5d import Vector5D


# ---------------------------------------------------------------------------
# Exemples valides
# ---------------------------------------------------------------------------


class TestVector5DValidCases:
    """Vector5D doit accepter toute valeur finie dans [0, 1]."""

    def test_zeros(self):
        """Vecteur nul — cas limite inférieur."""
        v = Vector5D(0.0, 0.0, 0.0, 0.0, 0.0)
        assert v.as_tuple() == (0.0, 0.0, 0.0, 0.0, 0.0)

    def test_ones(self):
        """Vecteur maximal — cas limite supérieur."""
        v = Vector5D(1.0, 1.0, 1.0, 1.0, 1.0)
        assert v.as_tuple() == (1.0, 1.0, 1.0, 1.0, 1.0)

    def test_nominal_values(self):
        """Cas nominal avec des valeurs diverses dans (0, 1)."""
        v = Vector5D(0.2, 0.5, 0.8, 0.6, 0.1)
        assert v.d1 == pytest.approx(0.2)
        assert v.d2 == pytest.approx(0.5)
        assert v.d3 == pytest.approx(0.8)
        assert v.d4 == pytest.approx(0.6)
        assert v.d5 == pytest.approx(0.1)

    def test_boundary_zero_and_one_mixed(self):
        """Mélange de bornes 0 et 1 sur différentes dimensions."""
        v = Vector5D(0.0, 1.0, 0.0, 1.0, 0.5)
        assert v.d1 == 0.0
        assert v.d2 == 1.0
        assert v.d5 == 0.5

    def test_integer_inputs_coerced_to_float(self):
        """Les entiers 0 et 1 doivent être acceptés et convertis en float."""
        v = Vector5D(0, 1, 0, 1, 0)
        assert isinstance(v.d1, float)
        assert v.d1 == 0.0
        assert v.d2 == 1.0

    def test_from_sequence_valid(self):
        """from_sequence doit produire le même résultat que le constructeur."""
        seq = [0.1, 0.2, 0.3, 0.4, 0.5]
        v = Vector5D.from_sequence(seq)
        assert v.as_tuple() == (0.1, 0.2, 0.3, 0.4, 0.5)

    def test_as_tuple_returns_five_elements(self):
        """as_tuple doit retourner exactement 5 éléments."""
        v = Vector5D(0.1, 0.2, 0.3, 0.4, 0.5)
        t = v.as_tuple()
        assert len(t) == 5

    def test_equality(self):
        """Deux vecteurs identiques doivent être égaux."""
        v1 = Vector5D(0.3, 0.3, 0.3, 0.3, 0.3)
        v2 = Vector5D(0.3, 0.3, 0.3, 0.3, 0.3)
        assert v1 == v2

    def test_inequality(self):
        """Deux vecteurs distincts ne doivent pas être égaux."""
        v1 = Vector5D(0.1, 0.2, 0.3, 0.4, 0.5)
        v2 = Vector5D(0.5, 0.4, 0.3, 0.2, 0.1)
        assert v1 != v2


# ---------------------------------------------------------------------------
# Rejet — NaN
# ---------------------------------------------------------------------------


class TestVector5DRejectsNaN:
    """Toute dimension NaN doit lever ValueError."""

    @pytest.mark.parametrize(
        "d1, d2, d3, d4, d5",
        [
            (math.nan, 0.5, 0.5, 0.5, 0.5),
            (0.5, math.nan, 0.5, 0.5, 0.5),
            (0.5, 0.5, math.nan, 0.5, 0.5),
            (0.5, 0.5, 0.5, math.nan, 0.5),
            (0.5, 0.5, 0.5, 0.5, math.nan),
        ],
        ids=["nan_d1", "nan_d2", "nan_d3", "nan_d4", "nan_d5"],
    )
    def test_nan_raises_value_error(self, d1, d2, d3, d4, d5):
        with pytest.raises(ValueError, match="NaN"):
            Vector5D(d1, d2, d3, d4, d5)


# ---------------------------------------------------------------------------
# Rejet — infinis
# ---------------------------------------------------------------------------


class TestVector5DRejectsInfinity:
    """Toute dimension ±inf doit lever ValueError."""

    @pytest.mark.parametrize(
        "d1, d2, d3, d4, d5",
        [
            (math.inf, 0.5, 0.5, 0.5, 0.5),
            (-math.inf, 0.5, 0.5, 0.5, 0.5),
            (0.5, math.inf, 0.5, 0.5, 0.5),
            (0.5, -math.inf, 0.5, 0.5, 0.5),
            (0.5, 0.5, math.inf, 0.5, 0.5),
            (0.5, 0.5, 0.5, math.inf, 0.5),
            (0.5, 0.5, 0.5, 0.5, math.inf),
            (0.5, 0.5, 0.5, 0.5, -math.inf),
        ],
        ids=[
            "pos_inf_d1", "neg_inf_d1",
            "pos_inf_d2", "neg_inf_d2",
            "pos_inf_d3",
            "pos_inf_d4",
            "pos_inf_d5", "neg_inf_d5",
        ],
    )
    def test_inf_raises_value_error(self, d1, d2, d3, d4, d5):
        with pytest.raises(ValueError, match="infinie"):
            Vector5D(d1, d2, d3, d4, d5)


# ---------------------------------------------------------------------------
# Rejet — valeurs hors de [0, 1]
# ---------------------------------------------------------------------------


class TestVector5DRejectsOutOfRange:
    """Toute dimension hors de [0, 1] doit lever ValueError."""

    @pytest.mark.parametrize(
        "d1, d2, d3, d4, d5",
        [
            (-0.001, 0.5, 0.5, 0.5, 0.5),
            (1.001, 0.5, 0.5, 0.5, 0.5),
            (0.5, -1.0, 0.5, 0.5, 0.5),
            (0.5, 2.0, 0.5, 0.5, 0.5),
            (0.5, 0.5, 0.5, 0.5, -0.1),
            (0.5, 0.5, 0.5, 0.5, 1.1),
        ],
        ids=[
            "negative_d1", "above_one_d1",
            "negative_d2", "above_one_d2",
            "negative_d5", "above_one_d5",
        ],
    )
    def test_out_of_range_raises_value_error(self, d1, d2, d3, d4, d5):
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            Vector5D(d1, d2, d3, d4, d5)


# ---------------------------------------------------------------------------
# Rejet — dimension absente (None)
# ---------------------------------------------------------------------------


class TestVector5DRejectsMissingDimension:
    """Toute dimension None doit lever TypeError."""

    @pytest.mark.parametrize(
        "d1, d2, d3, d4, d5",
        [
            (None, 0.5, 0.5, 0.5, 0.5),
            (0.5, None, 0.5, 0.5, 0.5),
            (0.5, 0.5, None, 0.5, 0.5),
            (0.5, 0.5, 0.5, None, 0.5),
            (0.5, 0.5, 0.5, 0.5, None),
        ],
        ids=["none_d1", "none_d2", "none_d3", "none_d4", "none_d5"],
    )
    def test_none_raises_type_error(self, d1, d2, d3, d4, d5):
        with pytest.raises(TypeError, match="absente"):
            Vector5D(d1, d2, d3, d4, d5)


# ---------------------------------------------------------------------------
# Rejet — mauvais nombre de dimensions
# ---------------------------------------------------------------------------


class TestVector5DRejectsWrongDimensionCount:
    """Nombre de dimensions incorrect → TypeError."""

    def test_from_sequence_too_few(self):
        with pytest.raises(TypeError, match="5 dimensions"):
            Vector5D.from_sequence([0.5, 0.5, 0.5, 0.5])

    def test_from_sequence_too_many(self):
        with pytest.raises(TypeError, match="5 dimensions"):
            Vector5D.from_sequence([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

    def test_from_sequence_empty(self):
        with pytest.raises(TypeError, match="5 dimensions"):
            Vector5D.from_sequence([])

    def test_constructor_too_few_args(self):
        with pytest.raises(TypeError):
            Vector5D(0.5, 0.5, 0.5, 0.5)  # type: ignore[call-arg]

    def test_constructor_too_many_args(self):
        with pytest.raises(TypeError):
            Vector5D(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)  # type: ignore[call-arg]
