# Spécification d'homogénéisation des vecteurs

**Constat observable :** si les événements observés et les actions MITRE ne sont pas projetés avec les mêmes règles, le matching produit un score numérique, mais pas une preuve de proximité.

L'objectif de ce document est donc de garantir :

$$V_{input} \in [0,1]^5 \quad et \quad V_{mitre} \in [0,1]^5$$

avec **la même sémantique** pour chaque dimension.

## 1. Règle générale
Pour toute dimension `d_i` :
- même définition métier côté input et côté MITRE ;
- même intervalle `[0,1]` ;
- même méthode de normalisation ;
- même jeu de tables ou de barèmes de référence.

Si cette symétrie n'est pas tenue, la comparaison devient rhétorique.

## 2. Protocole de normalisation des actions observées
### 2.1. `d1` — criticité
Entrée : ressource, service, cible ou objet touché.

Règle :

$$d1 = \frac{W(resource)}{W_{max}}$$

La table `W` doit être versionnée et justifiable.

### 2.2. `d2` — entropie
Entree : entropie de Shannon normalisee de `payload_bytes` avec la regle
canonique `d2 = H(payload_bytes) / 8`.

Resume operationnel : `payload_bytes` doit rester une concatenation ordonnee de
champs explicitement autorises et observes en clair ; si ce contenu utile n'est
pas observable en clair, `d2` est non calculable.

Le normatif detaille est centralise dans
`references/d2_entropy/d2_entropy_spec.v1.md` et la table versionnee des regles
par famille de source est centralisee dans
`references/d2_entropy/payload_field_rules.v1.yaml`.

### 2.3. `d3` — dynamique temporelle
Entrée : fréquence locale dérivée d'un `Δt` ou d'une fenêtre glissante.

Règle type :

$$d3 = \frac{1}{1 + e^{-k(f - f_0)}}$$

La fréquence doit être calculée à partir de l'historique de la même empreinte. Un timestamp brut ne suffit pas.

### 2.4. `d4` — intensité
Entrée : sémantique de l'action (`protocol`, `verb`, `permission`, `direction`).

Exemple de barème générique :
- lecture : `0.2`
- écriture : `0.6`
- exécution, suppression, action destructrice : `1.0`

### 2.5. `d5` — rareté
Entrée : empreinte ou signature de porteur.

Regle de synthese : score borne croissant avec la rarete observee, avec la
restriction que `jamais vu` reste dans le continuum scalaire `[0,1]`.

Le normatif detaille `d5` est centralise dans
`references/d5_rarity/d5_rarity_spec.v1.md`.
La table documentaire versionnee des classes ordinales, ancres fixes et
correspondance semantique input/MITRE est centralisee dans
`references/d5_rarity/rarity_projection.v1.yaml`.

## 3. Protocole de vectorisation du référentiel MITRE
Le référentiel MITRE ne doit pas être réduit à un seul vecteur idéal par technique tant qu'une technique comporte plusieurs phases.

Chaque technique est modélisée comme une **séquence de phases vectorisées**.

Exemple de structure logique :
- `phase_1` : préparation / reconnaissance ;
- `phase_2` : accès / exploitation ;
- `phase_3` : action sur objectif.

Chaque phase produit son propre `Vector5D` avec les mêmes règles que les inputs observés.

## 4. Règle de symétrie input / MITRE
Pour toute comparaison, il doit être possible d'affirmer :
- `d1_input` et `d1_mitre` parlent de la même notion ;
- `d2_input` et `d2_mitre` parlent de la même notion ;
- `d3_input` et `d3_mitre` utilisent la même échelle temporelle ;
- `d4_input` et `d4_mitre` utilisent le même barème d'intensité ;
- `d5_input` et `d5_mitre` expriment la même idée de rareté ou d'anomalie de porteur.

Sans cette règle, le moteur compare des nombres, pas des comportements.

## 5. Contrôles obligatoires
### 5.1. Contrôle de validité du vecteur
Tout vecteur construit doit vérifier :
- 5 composantes présentes ;
- aucune composante `NaN` ou infinie ;
- chaque composante dans `[0,1]`.

### 5.2. Contrôle de cohérence du référentiel
Toute séquence MITRE vectorisée doit être accompagnée :
- de sa source ;
- de sa version ;
- de l'hypothèse de mapping retenue ;
- de la justification des poids utilisés.

Un modèle MITRE sans traçabilité n'est pas un référentiel ; c'est une intuition.

## 6. Invariant final
L'homogénéisation est jugée correcte uniquement si :
1. les événements observés et les modèles MITRE produisent des `Vector5D` valides ;
2. les deux côtés utilisent les mêmes conventions ;
3. le moteur de matching peut travailler sans conversion ad hoc spécifique à une source.
