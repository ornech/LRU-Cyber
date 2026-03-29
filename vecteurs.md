# Les vecteurs

## Spécification technique de la vectorisation 5D

**Point de départ observable :** deux événements peuvent avoir des signatures textuelles très différentes tout en participant à la même logique d'attaque. Le projet ne compare donc pas des chaînes, mais des actions ramenées dans un même espace vectoriel.

## 1. Invariant du vecteur

Chaque action observée ou documentée est représentée par :

$$V_a = [d_1, d_2, d_3, d_4, d_5]$$

avec l'invariant :

$$V_a \in [0,1]^5$$

Un vecteur est **invalide** si une composante est absente, non finie, négative ou supérieure à `1`.

## 2. Entrées nécessaires à la vectorisation

La vectorisation ne doit pas dépendre d'un timestamp brut uniquement. Elle a besoin au minimum de trois objets :

- `RawEvent` : événement brut ;
- `Fingerprint` : porteur de l'action ;
- `ActionSemantics` : sens opérationnel de l'action.

### 2.1. RawEvent

Exemples de champs utiles :

- `timestamp`
- `protocol`
- `resource`
- `payload`
- `source`

### 2.2. Fingerprint

Exemples de composantes :

- JA3 ;
- fingerprint OS ;
- entropie ou structure des headers ;
- marqueurs stables de session ou de client.

### 2.3. ActionSemantics

`d4` ne doit pas dépendre d'un simple nom de méthode. Il faut au moins :

- `protocol`
- `verb`
- `permission`
- `direction`

Sans cela, un `POST`, un `DELETE SQL`, un `scp` ou un `chmod` seraient forcés dans le même moule lexical, ce qui fabrique une belle abstraction et un mauvais score.

## 3. Définition des dimensions

| Dimension | Nom                  | Entrée principale                                         | Règle de normalisation                  | Finalité                                                                  |
| :-------- | :------------------- | :-------------------------------------------------------- | :-------------------------------------- | :------------------------------------------------------------------------ |
| `d1`      | Criticité            | ressource ou cible                                        | table de pondération puis normalisation | distinguer une cible sensible d'un bruit de fond                          |
| `d2`      | Entropie             | champs observés retenus par type d'événement ou de source | `H(payload_bytes) / 8`                  | repérer une densité informationnelle inhabituelle dans le contenu observé |
| `d3`      | Dynamique temporelle | `Δt`, fréquence locale                                    | sigmoïde bornée dans `[0,1]`            | capturer rafale, script ou accélération d'exécution                       |
| `d4`      | Intensité            | sémantique de l'action                                    | barème borné par protocole/permission   | distinguer lecture, écriture, exécution, destruction                      |
| `d5`      | Rareté               | empreinte                                                 | score estimé par fréquence d'apparition | renforcer un signal porté par un acteur atypique                          |

## 4. Règles détaillées par dimension

### 4.1. `d1` — criticité

`d1` mesure l'importance de la cible touchée.

Exemple de principe :

$$d1 = \frac{W(resource)}{W_{max}}$$

La table de pondération doit être versionnée. Une valeur de criticité non tracée rend le score discutable.

### 4.2. `d2` — entropie

`d2` mesure le desordre informationnel du contenu observe avec la forme
canonique `d2 = H(payload_bytes) / 8`.

Le detail normatif (definition stricte de `payload_bytes`, regles de non
calculabilite, interdictions explicites, limites d'interpretation) est
centralise dans `references/d2_entropy/d2_entropy_spec.v1.md`.

### 4.3. `d3` — dynamique temporelle

`d3` ne doit pas être calculé à partir du seul timestamp absolu.

Le moteur doit dériver :

- `Δt` depuis le dernier commit de la même empreinte ;
- une fréquence locale ou une densité d'événements sur fenêtre glissante.

Exemple de mise à l'échelle :

$$d3 = \frac{1}{1 + e^{-k(f - f_0)}}$$

Cette forme borne `d3` dans `[0,1]` et évite qu'une rafale écrase toutes les autres dimensions.

### 4.4. `d4` — intensité

`d4` mesure la portée opérationnelle de l'action.

Exemple de barème générique :

- lecture : `0.2`
- écriture : `0.6`
- exécution / suppression / action destructive : `1.0`

Le barème doit être décliné par protocole. Une lecture SQL et un `GET /health` n'ont pas la même surface de risque, même si l'étiquette « READ » rassure un instant.

### 4.5. `d5` — rareté

`d5` mesure la rareté de l'empreinte observée, dans un scalaire borne `[0,1]`.

Le normatif detaille de `d5` (univers de comptage, granularite,
projection ordinale a ancres fixes, traitement de `jamais vu`, limites
d'interpretation, correspondance documentaire input/MITRE, et elements hors
v1) est centralise dans `references/d5_rarity/d5_rarity_spec.v1.md`.

## 5. Contrat de construction

Un `Vector5D` valide doit satisfaire les trois points suivants :

- les cinq dimensions existent ;
- chaque dimension est finie ;
- chaque dimension appartient à `[0,1]`.

La validation doit être faite **au constructeur**, puis vérifiée en test. Une validation seulement documentaire ne protège rien.

## 6. Usage côté trajectoire

Chaque vecteur est inséré dans un commit :

`{ previous_hash, vector, timestamp, cumulative_score }`

La trajectoire résultante reste une **séquence ordonnée**. Le système ne cherche pas un mot-clé final ; il cherche une dérive progressive vers une forme déjà connue.

## 7. Usage côté MITRE

Les actions MITRE doivent être vectorisées avec les mêmes règles que les actions observées.

Conséquence directe :

- même définition de `d1` à `d5` ;
- mêmes bornes ;
- mêmes tables de correspondance ;
- même sémantique de `d3` et `d4`.

Sinon `V_input` et `V_mitre` n'ont que l'apparence d'être comparables.
