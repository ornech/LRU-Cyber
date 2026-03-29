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

## D-004 — Spécification fermée de d2 entropie (issue #5)

**Date :** 2026-03-29
**Statut :** acceptée

### Contexte

La dimension `d2` était décrite comme une entropie du `payload`, mais cette
formulation restait trop ouverte : elle ne fixait ni les champs retenus, ni la
règle de non-calculabilité, ni le traitement documentaire des contenus chiffrés,
compressés ou encodés.

### Décision

`d2` est désormais défini comme l'entropie de Shannon normalisée d'une
concaténation ordonnée de champs explicitement nommés par type d'événement ou
de source.

- Formule canonique : `d2 = H(payload_bytes) / 8`.
- `payload_bytes` est construit uniquement à partir de champs observés en clair
  dans la source.
- Si le contenu utile n'est pas observable ou reste chiffré dans la source,
  `d2` est **non calculable**.
- Aucun décodage implicite, aucune décompression implicite et aucun
  déchiffrement implicite ne sont autorisés.
- Pour HTTP requête, `methode` est explicitement exclue ; seuls `cible`,
  `query_string` et `body` peuvent entrer dans `payload_bytes`.
- Pour DNS, le choix est fermé sur `query_name`. `record_type` est explicitement
  exclu en tant que champ structurel.
- Pour l'événement applicatif générique, seuls `message`, `body`, `content` et
  `payload` sont autorisés. Tout autre champ est exclu tant qu'il n'est pas
  explicitement ajouté au tableau normatif.

### Alternatives rejetées

- Raisonner sur une notion vague de « contenu exploitable observé » : rejeté,
  car non déterministe.
- Définir `d2` protocole par protocole sans s'appuyer sur les champs réellement
  observables dans la source : rejeté.
- Inclure des champs structurels comme `methode` HTTP ou `record_type` DNS dans
  le contenu retenu : rejeté.
- Autoriser un décodage, une décompression ou un déchiffrement implicites :
  rejeté.

### Conséquences

- `d2` devient une dimension documentaire déterministe et traçable.
- Les sources qui ne fournissent pas de contenu clair produisent un état
  « non calculable » au lieu d'un score construit sur une base implicite.
- Toute extension future des champs autorisés devra être explicitement ajoutée à
  la table normative, et non introduite par analogie.

## D-005 — Spécification versionnée de d3 dynamique temporelle (issue #6)

**Date :** 2026-03-29
**Statut :** acceptée

### Contexte

La dimension `d3` était décrite de manière générale mais sans artefact dédié
versionné, ce qui laissait des ambiguïtés sur la convention de mesure, la
normalisation, le traitement du `cold start` et la couverture des profils
temporels.

L'issue #6 impose un livrable strictement documentaire, sans implémentation
runtime, sans logique de matching, sans logique MITRE et sans politique
d'alerte.

### Décision

Adopter une référence versionnée dédiée dans `references/d3_temporal/` :

- `d3_temporal_spec.v1.md` : spécification normative de `d3`.
- `temporal_profiles.v1.yaml` : table versionnée des profils temporels couverts.
- `README.md` : règles de périmètre et de versionnement de la référence `d3`.

Les choix structurants de `v1` sont les suivants :

- convention de mesure explicitement **hybride** : `Δt` inter-événements +
  fenêtre locale sur la même empreinte ;
- normalisation bornée dans `[0,1]` via une forme sigmoïde monotone documentée ;
- couverture documentaire explicite des profils : rafale, exécution scriptée
  régulière, low-and-slow, périodique légitime, sporadique ;
- règle méthodologique ferme : le `cold start` est un état d'**historique
  insuffisant** (`insufficient_history`) et ne doit jamais être interprété
  comme une faible dynamique temporelle.

### Alternatives rejetées

- Assimiler le `cold start` à une valeur basse par défaut : rejeté.
- Définir `d3` uniquement par timestamp absolu : rejeté.
- Introduire des détails d'implémentation exécutable dans `src/` : rejeté
  (hors périmètre).
- Coupler `d3` à la logique DTW, MITRE, matching ou alerting : rejeté.

### Conséquences

- Le projet dispose d'un référentiel `d3` versionné, traçable et autonome.
- Les paramètres numériques (`k`, `f0`, taille de fenêtre, etc.) restent
  explicitement **provisoires** tant qu'aucune calibration corpus n'est
  documentée.
- Toute évolution normative ultérieure devra passer par une nouvelle version de
  fichiers (`v2`, `v3`, ...), sans réécriture silencieuse de `v1`.

## D-006 — Referentiel versionne de d4 intensite operatoire (issue #7)

**Date :** 2026-03-29
**Statut :** acceptee

### Contexte

La dimension `d4` (intensite) etait decrite a haut niveau, sans artefact
versionne fixant a la fois :
- la definition normative,
- la grille commune inter-protocoles,
- la structure de `ActionSemantics`,
- le mapping initial protocole -> capacite,
- le traitement methodologique des cas ambigus.

L'issue #7 impose un livrable strictement documentaire/data, sans
implementation runtime, sans logique DTW, sans logique MITRE detaillee,
sans modification de `src/`, `tests/` ou `contracts.md`.

### Decision

Adopter une reference versionnee dediee dans `references/d4_intensity/` :

- `d4_intensity_spec.v1.md` : specification normative de `d4`.
- `action_semantics.v1.yaml` : definition explicite des champs
  `protocol`, `verb`, `permission`, `direction`, `operational_capability`,
  `notes`, `status`.
- `protocol_mappings.v1.yaml` : mapping initial par protocoles/familles.
- `README.md` : regles de perimetre et de versionnement de la reference `d4`.

Choix normatifs structurants de `v1` :

- `d4` mesure la **capacite operatoire observable** a transformer, controler ou
  detruire l'etat cible ; il ne mesure ni danger, ni intention, ni malignite.
- Une action est classee selon son **effet operatoire observable sur la cible**,
  et non selon son verbe natif seul.
- Exemples methodologiques obligatoires :
  - un `GET` HTTP avec effet de bord applicatif n'est pas automatiquement une
    simple lecture,
  - un changement de droits est classe selon la capacite de controle
    effectivement observee.
- Le champ `d4_hint` est explicitement defini comme **provisoire**,
  **ordinal**, **documentaire**, **non calibre empiriquement** et **non
  suffisant a lui seul pour conclure a une attaque**.

### Alternatives rejetees

- Introduire un algorithme executable de calcul `d4` : rejete (hors perimetre).
- Introduire un chargement runtime des tables : rejete (hors perimetre).
- Coupler `d4` a DTW, MITRE detaille, matching ou alerting : rejete.
- Modifier `src/`, `tests/` ou `contracts.md` : rejete.

### Consequences

- `d4` dispose d'un referentiel versionne, tracable et portable entre
  protocoles.
- Les cas ambigus restent documentes comme ambigus (dependants du contexte),
  sans surinterpretation artificielle.
- Toute evolution normative ulterieure devra creer des fichiers `v2+`, sans
  reecriture silencieuse de `v1`.

## D-007 — Referentiel versionne de d5 rarete documentaire (issue #8)

**Date :** 2026-03-30
**Statut :** acceptee

### Contexte

La dimension `d5` (rarete) etait engagee minimalement dans les documents
racine, mais sans referentiel versionne autonome fermant explicitement :
- l'univers de comptage,
- la granularite,
- le traitement normatif de `jamais vu`,
- la projection documentaire canonique dans `[0,1]`,
- la correspondance semantique input/MITRE,
- les limites d'interpretation,
- et les reports hors v1.

L'issue #8 impose une fermeture strictement documentaire, sans implementation
runtime, sans benchmark/calibration, sans tests d'execution, et sans
redefinition transverse de `Fingerprint`.

### Decision

Adopter une reference versionnee dediee dans `references/d5_rarity/` :

- `d5_rarity_spec.v1.md` : specification normative de `d5`.
- `rarity_projection.v1.yaml` : table versionnee des classes ordinales,
  ancres fixes et correspondance documentaire input/MITRE.
- `README.md` : regles de perimetre et de versionnement de la reference `d5`.

Arbitrages normatifs fermes pour `v1` :

- univers de comptage : par famille de source ou protocole ;
- granularite : occurrence d'action observee ;
- `jamais vu` : valeur maximale du continuum scalaire `d5` dans `[0,1]`, sans
  flag cache ;
- projection canonique : ordinale, documentaire, bornee, avec ancres fixes ;
- horizon temporel : explicitement hors v1 ;
- oubli/vieillissement : explicitement hors v1 ;
- limites d'interpretation : socle minimal + cas legitimes de renouvellement
  d'empreinte ;
- symetrie input/MITRE : semantique stricte avec table de correspondance
  documentaire, sans supposer une symetrie empirique de frequence.

### Alternatives rejetees

- Introduire un estimateur runtime (y compris details CMS) : rejete
  (hors perimetre).
- Introduire une politique d'alerte ou de matching : rejete (hors perimetre).
- Redefinir `Fingerprint` comme objet transverse dans l'issue #8 : rejete
  (hors perimetre).
- Fixer en v1 une politique de fenetre temporelle ou d'oubli/vieillissement :
  rejete (report explicite hors v1).

### Consequences

- `d5` dispose d'un referentiel documentaire autonome, versionne et tracable
  dans `references/d5_rarity/`.
- `vecteurs.md` et `specification_homogeneisation.md` restent des documents de
  synthese avec renvois explicites vers le normatif `d5`.
- Toute evolution normative future de `d5` devra creer des fichiers `v2+`,
  sans reecriture silencieuse de `v1`.
