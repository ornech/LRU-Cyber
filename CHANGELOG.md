# CHANGELOG

## [Unreleased]

### Ajouté

- **Issue #60 - d2 entropy (documentaire + donnees)** : ajout du dossier
  `references/d2_entropy/` avec une specification versionnee
  `d2_entropy_spec.v1.md` et une table versionnee
  `payload_field_rules.v1.yaml`.
- Centralisation du normatif detaille de `d2` dans
  `references/d2_entropy/` et passage des documents racine `vecteurs.md` et
  `specification_homogeneisation.md` a un role de synthese avec renvois
  explicites.

- **Issue #7 — d4 intensite (documentaire + donnees)** : ajout du dossier
  `references/d4_intensity/` avec une specification versionnee
  `d4_intensity_spec.v1.md`, une definition explicite de `ActionSemantics`
  dans `action_semantics.v1.yaml`, et un mapping initial par protocole dans
  `protocol_mappings.v1.yaml`.
- La definition normative retenue pour `d4` est explicitee : `d4` mesure la
  capacite operatoire observable (transformer, controler, detruire) et ne
  mesure ni danger, ni intention, ni malignite.
- La regle methodologique est figee : classer une action selon son effet
  operatoire observable sur la cible, et non selon son verbe natif seul
  (incluant les cas `GET` HTTP a effet de bord et changement de droits).
- Le champ `d4_hint` est documente comme **provisoire**, **ordinal**,
  **documentaire**, **non calibre empiriquement**, et **non suffisant a lui
  seul pour conclure a une attaque**.
- Les cas ambigus obligatoires sont traces comme dependants du contexte
  (lecture massive, ecriture benigne, suppression legitime, creation
  automatique legitime, execution administrative normale, changement de droits
  attendu en maintenance), sans surinterpretation artificielle.

- **Issue #6 — d3 dynamique temporelle (documentaire + données)** : ajout du
  dossier `references/d3_temporal/` avec une spécification versionnée
  `d3_temporal_spec.v1.md` et une table de profils
  `temporal_profiles.v1.yaml`.
- La convention de mesure retenue pour `d3` est explicitement **hybride**
  (`Δt` + fenêtre locale), avec normalisation bornée dans `[0,1]`.
- Le cas `cold start` est figé comme état explicite d'**historique
  insuffisant** (`insufficient_history`) et ne doit pas être interprété comme
  une faible dynamique temporelle.
- Les paramètres numériques de normalisation et de fenêtre sont documentés
  comme **provisoires** tant qu'ils ne sont pas calibrés sur corpus observé.

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

- **Réalignement documentaire** : mise à jour de `README.md` et
  `.github/copilot-instructions.md` pour refléter l'état réel du dépôt.
  L'alerte n'est plus décrite comme `Distance(T_user, T_atk) < ε` mais comme
  une politique séparée appliquée à un `match_score` dérivé d'une distance
  normalisée. La documentation d'état de projet mentionne désormais les
  implémentations déjà présentes (`Vector5D`, `MatchResult`,
  `ArchivedProfile`) et leurs tests, ainsi que la table `d1` versionnée dans
  `references/criticality/criticality_weights.v1.yaml`.

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
