# CHANGELOG

## [Unreleased]

### Ajouté

- **Issue #4 — d1 criticité (documentaire + données)** : ajout d'une table
  versionnée de criticité dans
  `references/criticality/criticality_weights.v1.yaml`.
  Chaque entrée contient un poids borné `[0,1]`, une justification technique
  explicite et des exemples de ressources.
- Documentation associée ajoutée dans
  `references/criticality/README.md` : structure de table, règles de
  validation documentaire et règles de versionnement/mise à jour.

- **C-003 — ArchivedProfile** : implémentation de la structure
  `ArchivedProfile` immuable (`src/cyber_vpt/archived_profile.py`).
  Valide au constructeur : `mu` de type `Vector5D`, `sigma` de forme `5x5`
  finie/symétrique/positive semi-définie (valeurs propres nulles autorisées),
  `n_points >= 2`, et cohérence temporelle `first_seen <= last_seen`.
- Tests de contrat `tests/test_archived_profile.py` couvrant les cas valides,
  les rejets obligatoires et l'immutabilité.

- **C-002 — MatchResult** : implémentation de la structure `MatchResult` immuable
  (`src/cyber_vpt/match_result.py`). Valide au constructeur :
  `raw_distance ≥ 0`, `normalized_distance ∈ [0,1]`, `match_score ∈ [0,1]`,
  et la cohérence `match_score = 1 - normalized_distance`.
- Tests de contrat `tests/test_match_result.py` couvrant les cas valides,
  les rejets obligatoires et les bornes exactes.

### Modifié

- Export package : ajout de `ArchivedProfile` dans
  `src/cyber_vpt/__init__.py` (`__all__`).

- **C-002 — completion_probability** : champ optionnel dans `MatchResult`,
  valeur par défaut `None` si non renseigné. La validation (appartenance à
  `[0,1]`, finitude) n'est déclenchée que si la valeur est renseignée.
  Contrat, implémentation et tests sont alignés sur cette règle.
- Tests enrichis : rejet de `NaN` et `±inf` pour `raw_distance`,
  `normalized_distance` et `match_score` ; rejet de `completion_probability`
  invalide (NaN, ±inf, hors [0,1]) ; cohérence stricte `match_score = 1 -
  normalized_distance` aux bornes et au milieu.
