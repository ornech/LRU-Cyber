# CHANGELOG

## [Unreleased]

### Ajouté

- **C-002 — MatchResult** : implémentation de la structure `MatchResult` immuable
  (`src/cyber_vpt/match_result.py`). Valide au constructeur :
  `raw_distance ≥ 0`, `normalized_distance ∈ [0,1]`, `match_score ∈ [0,1]`,
  et la cohérence `match_score = 1 - normalized_distance`.
- Tests de contrat `tests/test_match_result.py` couvrant les cas valides,
  les rejets obligatoires et les bornes exactes.
