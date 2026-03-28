# DECISIONS

## D-001 — MatchResult immuable avec validation au constructeur (C-002)

**Date :** 2026-03-28
**Statut :** acceptée

### Contexte

Le contrat C-002 définit `MatchResult` comme la structure centrale de sortie
du moteur DTW. Elle doit garantir quatre invariants :
`raw_distance >= 0`, `normalized_distance ∈ [0,1]`, `match_score ∈ [0,1]`,
et `match_score = 1 - normalized_distance`.

### Décision

`MatchResult` est implémentée comme une classe immuable en Python pur :

- **Immuabilité** : `__slots__` + `object.__setattr__` au constructeur +
  `__setattr__` levant `AttributeError` sur toute modification ultérieure.
  Ce mécanisme est identique à celui retenu pour `Vector5D` (C-001), pour
  assurer la cohérence du projet.
- **Validation au constructeur** : toutes les règles de rejet sont appliquées
  avant l'affectation des champs, garantissant qu'aucune instance invalide
  ne peut exister.
- **Tolérance numérique** : la cohérence `match_score = 1 - normalized_distance`
  est vérifiée à 1e-9 près pour absorber les erreurs d'arrondi IEEE 754,
  sans assouplir le contrat métier.
- **`matched_stage`** : restreint aux entiers non négatifs (`int`, booléens
  exclus) pour éviter les ambiguïtés de typage silencieux.
- **`completion_probability`** : champ optionnel — valeur par défaut `None`
  si non renseignée. La validation (appartenance à `[0,1]`, finitude) n'est
  déclenchée que si la valeur est explicitement fournie (non `None`).
  Ce champ représente une estimation heuristique de la fraction d'avancement
  de l'attaque ; il ne constitue pas une preuve juridique d'intention
  malveillante.

### Alternatives rejetées

- `dataclasses.dataclass(frozen=True)` : moins lisible pour la validation
  fine champ par champ ; messages d'erreur moins précis.
- Validation post-construction (setter/property) : ne garantit pas
  l'invariant dès la création de l'objet.

### Conséquences

Toute instance de `MatchResult` satisfait par construction les invariants
de C-002. Les composants consommateurs (`AlertEngine`, etc.) peuvent s'y
fier sans vérification supplémentaire.
