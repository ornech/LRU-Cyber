# Convergence et Rapprochement Vectoriel (CYBER-PATH)

Ce document détaille la philosophie mathématique permettant de comparer des flux de données brutes avec le référentiel théorique **MITRE ATT&CK**.

## 1. Le Concept de l'Espace Commun
Pour que la prédiction fonctionne, l'**Input** (ce qui arrive) et le **MITRE** (ce qu'on redoute) doivent exister dans le même "monde numérique". Cet espace est défini par notre hypercube $[0, 1]^5$.

* **L'Input ($V_{in}$)** : C'est une observation empirique. Elle est souvent bruitée, incomplète ou fragmentée dans le temps.
* **Le MITRE ($V_{mt}$)** : C'est une signature idéale. Elle représente la "forme pure" d'une technique d'attaque (ex: T1190).



---

## 2. Pourquoi l'Homogénéisation est Vitale ?
Sans une normalisation stricte, le moteur de comparaison (DTW) serait "aveugle" aux signaux faibles.

1.  **Équilibre des Poids :** Si la fréquence ($d_3$) n'est pas ramenée entre 0 et 1, une attaque rapide (100 requêtes/sec) écraserait totalement une exfiltration discrète en termes de distance mathématique.
2.  **Calcul de la "Dérive" :** En homogénéisant les dimensions, on peut mesurer précisément comment un utilisateur "glisse" d'un comportement sain vers une trajectoire d'attaque.
3.  **Indépendance du Protocole :** Que l'attaque soit en HTTP, SSH ou SQL, une fois vectorisée en 5D, elle devient une **forme géométrique universelle**.



---

## 3. Mécanisme de Rapprochement (Matching)
Le système utilise la **Distance Euclidienne** pondérée au sein de l'algorithme **DTW**.

### A. La Signature "Fantôme"
Chaque technique MITRE est enregistrée comme une séquence de vecteurs idéaux. 
> *Exemple pour une Injection SQL (T1190) :*
> 1.  `V_recon`  : [0.3, 0.2, 0.1, 0.2, 0.5] (Exploration)
> 2.  `V_exploit`: [0.9, 0.8, 0.9, 0.7, 0.9] (Attaque)

### B. Le Miroir Prédictif
Le moteur **CYBER-PATH** projette la trajectoire en cours de l'utilisateur sur les modèles MITRE. 
* Si la trajectoire utilisateur "mime" les premiers vecteurs d'une attaque, le système calcule le **Vecteur de Probabilité de Complétion**.
* **Alerte Prédictive :** L'alerte est levée si la distance cumulative descend sous le seuil $\epsilon$, même si l'action finale (exfiltrer) n'a pas encore eu lieu.



---

## 4. Tableau de Convergence des Dimensions

| Dimension | Réalité (Input Log) | Théorie (Modèle MITRE) | Point de Convergence |
| :--- | :--- | :--- | :--- |
| **d1 : Criticité** | Sensibilité de l'URL/IP touchée | Cibles habituelles de la technique | **Importance de la cible** |
| **d2 : Entropie** | Chaos textuel du payload réel | Complexité attendue du shellcode | **Niveau d'obfuscation** |
| **d3 : Fréquence** | Délai entre les actions logs | Rythme d'exécution type (Script/Humain) | **Dynamique temporelle** |
| **d4 : Intensité** | Verbe HTTP / Permissions SQL | Dangerosité de l'action requise | **Gravité de l'acte** |
| **d5 : Rareté** | Nouveauté de l'empreinte client | Profil d'attaquant (externe/interne) | **Anomalie d'identité** |

---

## 5. Conclusion
L'homogénéisation transforme la cybersécurité en un problème de **Reconnaissance de Formes**. Grâce à ces 5 dimensions, **CYBER-PATH** ne cherche plus des coupables, il cherche des **trajectoires suspectes**.
