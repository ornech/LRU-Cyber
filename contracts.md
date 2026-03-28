# Contrats — CYBER-VPT

**État observable :** le système manipule trois objets centraux dont la validité ne doit jamais dépendre d'une interprétation implicite : `Vector5D`, `MatchResult`, `ArchivedProfile`.

## 0. Règle générale

Un contrat définit :
- ce qui est autorisé ;
- ce qui est interdit ;
- ce qui doit être rejeté explicitement ;
- ce qui doit être testé.

Tout objet qui viole un contrat est invalide par construction.

---

## 1. Contrat C-001 — Vector5D

### 1.1. Définition

`Vector5D` représente une action projetée dans l'espace normalisé `[0,1]^5`.

Forme :

```text
Vector5D = (d1, d2, d3, d4, d5)
``` 

### 1.2. Invariants

Les conditions suivantes doivent toujours être vraies :

```text
0 <= d1 <= 1
0 <= d2 <= 1
0 <= d3 <= 1
0 <= d4 <= 1
0 <= d5 <= 1
```

Le vecteur appartient donc à :

```text
Vector5D ∈ [0,1]^5
```

### 1.3. Rejets obligatoires

Un `Vector5D` doit être rejeté si :

* une dimension est absente ;
* une dimension vaut `NaN` ;
* une dimension vaut `+inf` ou `-inf` ;
* une dimension est hors de `[0,1]` ;
* l'ordre des dimensions n'est pas garanti.

### 1.4. Sémantique minimale des dimensions

* `d1` : criticité de la ressource ou de la cible.
* `d2` : entropie ou complexité du contenu utile.
* `d3` : dynamique temporelle normalisée.
* `d4` : intensité sémantique de l'action.
* `d5` : rareté de l'empreinte observée.

### 1.5. Exemples

Valide :

```text
(0.2, 0.8, 0.5, 0.4, 0.9)
```

Invalides :

```text
(0.2, 1.4, 0.5, 0.4, 0.9)      # hors intervalle
(0.2, NaN, 0.5, 0.4, 0.9)      # NaN
(0.2, 0.5, 0.4, 0.9)           # dimension manquante
```

### 1.6. Tests attendus

* rejet d'une valeur > 1 ;
* rejet d'une valeur < 0 ;
* rejet de `NaN` ;
* rejet de `±inf` ;
* acceptation d'un vecteur valide ;
* vérification de l'ordre stable `(d1,d2,d3,d4,d5)`.

---

## 2. Contrat C-002 — MatchResult

### 2.1. Définition

`MatchResult` décrit le résultat d'un rapprochement entre une trajectoire observée et un modèle de référence.

Forme :

```text
MatchResult = (
  raw_distance,
  normalized_distance,
  match_score,
  matched_stage,
  completion_probability  -- optionnel (None si non renseignée)
)
```

### 2.2. Invariants

```text
raw_distance >= 0
raw_distance est finie (ni NaN, ni ±inf)

0 <= normalized_distance <= 1
normalized_distance est finie (ni NaN, ni ±inf)

0 <= match_score <= 1
match_score est fini (ni NaN, ni ±inf)

match_score = 1 - normalized_distance

completion_probability, si renseignée, appartient à [0,1]
completion_probability, si renseignée, est finie (ni NaN, ni ±inf)
```

### 2.3. Règle métier

Aucune alerte ne doit être déclenchée directement à partir de `raw_distance`.

Toute décision métier (`WATCH`, `CRITICAL`, etc.) doit être prise à partir de :

* `normalized_distance`,
* `match_score`,
* éventuellement `matched_stage` et `completion_probability`.

### 2.4. Rejets obligatoires

Un `MatchResult` doit être rejeté si :

* `raw_distance` vaut `NaN` ;
* `raw_distance` vaut `+inf` ou `-inf` ;

* `normalized_distance` vaut `NaN` ;
* `normalized_distance` vaut `+inf` ou `-inf` ;
* `normalized_distance` sort de `[0,1]` ;

* `match_score` vaut `NaN` ;
* `match_score` vaut `+inf` ou `-inf` ;
* `match_score` sort de `[0,1]` ;

* `match_score != 1 - normalized_distance` ;

* `completion_probability` est renseignée mais vaut `NaN` ;
* `completion_probability` est renseignée mais vaut `+inf` ou `-inf` ;
* `completion_probability` est renseignée mais sort de `[0,1]` ;

* `matched_stage` est incohérent avec la séquence évaluée.

### 2.5. Exemple

Valide :

```text
raw_distance = 3.2
normalized_distance = 0.25
match_score = 0.75
matched_stage = 2
completion_probability = 0.60
```

Invalide :

```text
normalized_distance = 1.3
match_score = 0.75
```

Invalide :

```text
normalized_distance = 0.25
match_score = 0.60
```

### 2.6. Tests attendus

* cohérence `match_score = 1 - normalized_distance` ;
* rejet d'une distance normalisée > 1 ;
* rejet d'un score négatif ;
* rejet de `NaN` ;
* rejet de `±inf` ;
* rejet de `completion_probability` non finie ;
* rejet de `completion_probability` hors `[0,1]` ;
* vérification qu'aucune politique d'alerte ne dépend de `raw_distance` seule.

---

## 3. Contrat C-003 — ArchivedProfile

### 3.1. Définition

`ArchivedProfile` résume une trajectoire inactive sous forme statistique.

Forme :

```text
ArchivedProfile = (
  μ,
  σ,
  n_points,
  first_seen,
  last_seen
)
```

où :

* `μ` est un `Vector5D` moyen ;
* `σ` est une matrice de covariance `5x5` ;
* `n_points` est le nombre de vecteurs résumés ;
* `first_seen` et `last_seen` bornent temporellement le profil.

### 3.2. Invariants

```text
μ ∈ [0,1]^5
σ ∈ R^(5x5)
σ = σ^T
σ positive semi-définie
n_points >= 2
first_seen <= last_seen
```

### 3.3. Rejets obligatoires

Un `ArchivedProfile` doit être rejeté si :

* `μ` viole le contrat `Vector5D` ;
* `σ` n'est pas de taille `5x5` ;
* `σ` n'est pas symétrique ;
* `σ` n'est pas positive semi-définie ;
* `n_points < 2` ;
* `first_seen > last_seen`.

### 3.4. Règle terminologique

Le terme `PCA` est interdit tant que le système ne stocke pas explicitement :

* des axes principaux ;
* des valeurs propres ;
* une variance expliquée.

Tant que seuls `μ` et `σ` sont stockés, le bon terme est :

```text
profil archivé statistique
```

et non :

```text
PCA
```

### 3.5. Tests attendus

* rejet d'une matrice non symétrique ;
* rejet d'une matrice non positive semi-définie ;
* rejet d'un `n_points = 1` ;
* rejet d'une borne temporelle inversée ;
* acceptation d'un profil statistique valide.

---

## 4. Contrat C-004 — TechniqueModel

### 4.1. Définition

`TechniqueModel` représente une technique MITRE découpée en phases vectorisables.

Forme minimale :

```text
TechniqueModel = (
  tid,
  attack_version,
  name,
  phases,
  hypotheses,
  confidence_level,
  sources
)
```

### 4.2. Invariants

* `tid` ne doit pas être vide ;
* `attack_version` doit être explicitement renseignée ;
* `phases` doit contenir au moins une phase ;
* chaque phase doit contenir une projection `Vector5D` justifiée ;
* `confidence_level` doit être explicite ;
* `sources` doit contenir au moins une référence traçable.

### 4.3. Rejets obligatoires

Un `TechniqueModel` doit être rejeté si :

* une phase n'a pas de source ;
* une phase n'a pas de justification de mapping ;
* une version ATT&CK n'est pas indiquée ;
* une valeur vectorielle n'est pas traçable.

### 4.4. Règle métier

Un vecteur MITRE n'est jamais une vérité observée.
C'est une hypothèse documentaire versionnée et révisable.

---

## 5. Contrat C-005 — AlertEngine

### 5.1. Définition

`AlertEngine` transforme un `MatchResult` en niveau d'alerte.

### 5.2. Invariants

* les seuils `WATCH` et `CRITICAL` doivent être explicitement déclarés ;
* tout seuil non calibré doit être marqué comme provisoire ;
* une alerte doit être explicable par les champs du `MatchResult`.

### 5.3. Interdictions

* pas d'alerte issue d'un seuil implicite ;
* pas d'alerte non reliée à un `MatchResult` ;
* pas de seuil présenté comme stable avant calibration sur données observées.

---

## 6. Contrat de traçabilité

Toute modification d'un contrat doit entraîner :

* une entrée dans `CHANGELOG.md` ;
* si le choix est structurant, une entrée dans `DECISIONS.md` ;
* la mise à jour éventuelle du `lexique.md` ;
* la mise à jour des tests associés.

---

## 7. Ordre de dépendance

Les contrats doivent être implémentés et testés dans cet ordre :

1. `Vector5D`
2. `MatchResult`
3. `ArchivedProfile`
4. `TechniqueModel`
5. `AlertEngine`

Tout apprentissage est interdit tant que les trois premiers contrats ne sont ni écrits ni testés.

---

## 8. Résumé exécutable

Le système n'est autorisé à produire un signal exploitable que si :

* les vecteurs observés respectent `C-001` ;
* les résultats de matching respectent `C-002` ;
* les archives respectent `C-003` ;
* les modèles MITRE respectent `C-004` ;
* les alertes respectent `C-005`.