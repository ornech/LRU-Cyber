# Cahier des Charges Fonctionnel et Technique (CdCFT)
## Projet : CYBER-VPT (Cyber Vector Predictive Trajectory)

**Périmètre :** Génération d'empreintes dynamiques et corrélation de trajectoires vectorielles basées sur le référentiel MITRE ATT&CK.

---

### 1. Objet du Projet
Développer un moteur capable de :
1. Transformer des flux d'événements (INPUT) en trajectoires vectorielles.
2. Convertir les tactiques/techniques MITRE ATT&CK en trajectoires de référence.
3. Mesurer en temps réel la distance mathématique entre le comportement utilisateur et une attaque connue.

---

### 2. Spécification de la Vectorisation (Espace $\mathbb{R}^5$)
Chaque action est projetée dans un espace vectoriel $V_a = [d_1, d_2, d_3, d_4, d_5]$ où chaque dimension est normalisée entre 0 et 1.

| Dim       | Nom           | Description / Calcul                                                                                                                      |
| :-------- | :------------ | :---------------------------------------------------------------------------------------------------------------------------------------- |
| **$d_1$** | **Criticité** | Poids $W_{res}$ de la ressource (ex: `/admin` vs `/img`).                                                                                 |
| **$d_2$** | **Entropie**  | Entropie de Shannon normalisée des seuls champs observés en clair et explicitement retenus par type d'événement ou de source.             |
| **$d_3$** | **Fréquence** | Inverse du délai temporel ($1/\Delta t$) entre deux actions.                                                                              |
| **$d_4$** | **Intensité** | Poids lié à la méthode/protocole (GET, POST, etc.).                                                                                       |
| **$d_5$** | **Rareté**    | Rareté documentaire scalaire de l'empreinte observée dans `[0,1]`, via projection ordinale à ancres fixes (`jamais vu` = ancre maximale). |

> **Note sur $d_5$ :** Le détail normatif de `d5` est centralisé dans
> `references/d5_rarity/d5_rarity_spec.v1.md` et
> `references/d5_rarity/rarity_projection.v1.yaml`.

---

### 3. Gestion des Empreintes et Trajectoires
#### 3.1. Identifiant d'Empreinte ($ID_{emp}$)
* **Invariants :** Hash concaténé (JA3 + Fingerprint OS + Entropy Headers).
* **Lien Volatile :** Table de correspondance temps réel $ID_{emp} \leftrightarrow IP_{source}$.

#### 3.2. Structure de la Trajectoire ($T_{user}$)
* **Chainage :** Suite ordonnée de "Commits". Chaque commit pointe vers le hash du précédent.
* **Algorithme de Comparaison :** **DTW (Dynamic Time Warping)** pour permettre le matching de séquences à vitesses variables (attaques "Low & Slow").

---

### 4. Moteur de Stockage et Performance (LRU)
* **New List (RAM - 32 Go) :** Stockage des trajectoires actives en haute résolution ($\mathbb{R}^5$).
* **Filtre de Bloom :** Lookup ultra-rapide des empreintes connues pour réduire les accès mémoire inutiles.
* **Old List (Archive) :** Résumé des trajectoires inactives sous forme de **profil archivé statistique** `(mu, sigma, n_points, first_seen, last_seen)` ; pas de PCA tant qu'aucun axe principal ni aucune variance expliquée ne sont stockés.

---

### 5. Système d'Alerte Prédictive
Le matching calcule d'abord une distance normalisée entre la trajectoire utilisateur et
une trajectoire MITRE de référence (via DTW), bornée dans `[0,1]`.

Le score de correspondance est ensuite dérivé de cette distance :
$$match\_score = 1 - normalized\_distance$$

La politique d'alerte est appliquée séparément du calcul de distance/score, à partir de
ce `match_score` et de seuils de décision explicites.

L'alerte identifie précisément quelle étape de la chaîne d'attaque est actuellement mimée.

---

### 6. Contraintes Techniques
* **Langages recommandés :** Rust ou C++ (gestion SIMD/Calcul matriciel), ou Python avec NumPy/PyTorch pour le prototypage.
* **Performance :** Temps de vectorisation < 2ms / log.
