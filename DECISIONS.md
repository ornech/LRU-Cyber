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

## D-002 — ArchivedProfile immuable avec validation stricte au constructeur (C-003)

**Date :** 2026-03-28
**Statut :** acceptée

### Contexte

Le contrat C-003 impose un profil archivé statistique robuste :
`mu` de type `Vector5D`, `sigma` de forme `5x5` finie, symétrique et
positive semi-définie, `n_points >= 2`, et cohérence temporelle
`first_seen <= last_seen`.

### Décision

`ArchivedProfile` est implémentée comme une classe immuable en Python pur,
avec validation exhaustive au constructeur :

- **Immuabilité** : `__slots__` + `object.__setattr__` au constructeur +
  `__setattr__` bloquant toute mutation ultérieure.
- **Type de `mu`** : `mu` doit être une instance de `Vector5D` (et non un tuple
  ou une séquence implicite), afin de réutiliser explicitement C-001.
- **Validation de `sigma`** : conversion en `ndarray` float puis vérification de
  la forme `(5,5)`, de la finitude (`NaN`/`±inf` interdits), de la symétrie et
  de la positive semi-définition via `eigvalsh`.
- **Tolérances numériques** : des tolérances strictes (`1e-12`) sont appliquées
  pour la symétrie et la PSD afin de ne pas rejeter des matrices valides à cause
  d'artefacts flottants.
- **Règle PSD** : les valeurs propres nulles sont explicitement autorisées.
- **Validation métier restante** : `n_points` entier (booléens exclus) et
  `n_points >= 2`, puis `first_seen` et `last_seen` en `datetime` avec
  `first_seen <= last_seen`.

### Alternatives rejetées

- Accepter un `mu` séquentiel puis le convertir implicitement : rejeté pour
  éviter la duplication partielle de C-001 et garder une frontière claire.
- Validation différée (post-construction) : rejetée car elle autorise des états
  invalides temporaires.

### Conséquences

Toute instance d'`ArchivedProfile` est valide par construction et directement
consommable par les composants aval, sans ajouter de logique hors périmètre.

## D-003 — Table versionnée de criticité d1 (issue #4)

**Date :** 2026-03-28
**Statut :** acceptée

### Contexte

La dimension `d1` (criticité) est définie dans la documentation, mais la table
de pondération n'était pas versionnée dans un artefact de données dédié.
L'issue #4 demande un livrable strictement documentaire/data, sans implémentation
runtime, sans logique de matching, et sans logique MITRE.

### Décision

Adopter une première table versionnée dans
`references/criticality/criticality_weights.v1.yaml` avec les propriétés
suivantes :

- poids bornés dans `[0,1]` pour toutes les catégories ;
- justification technique explicite obligatoire pour chaque entrée ;
- exemples de ressources obligatoires pour chaque catégorie ;
- catégorie de repli explicite (`fallback`) ;
- règles de revue et de versionnement documentées dans
  `references/criticality/README.md`.

La version `v1` est marquée `provisional` pour signaler qu'elle constitue une
base initiale de référence documentaire et qu'elle pourra être révisée via une
nouvelle version de fichier.

### Alternatives rejetées

- Introduire une logique de chargement runtime : rejeté (hors périmètre issue #4).
- Modifier des contrats, du code `src/` ou des tests : rejeté (hors périmètre).
- Coupler cette table à des règles MITRE, DTW, matching ou alerting : rejeté
  pour conserver une séparation claire des responsabilités.

### Conséquences

- La criticité `d1` dispose d'un référentiel de données explicite et versionné.
- Les révisions futures devront créer `criticality_weights.vN.yaml` sans
  réécriture silencieuse de `v1`.
- Les évolutions d'implémentation éventuelles resteront traitées dans une issue
  distincte.
