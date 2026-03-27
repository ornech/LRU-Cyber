import math
import time
from collections import Counter

class Vectorizer:
    def __init__(self):
        self.known_signatures = {} # Simulation d'un cache pour d5 (Rareté)

    def calculate_entropy(self, text):
        """Calcule l'entropie de Shannon (d2). Plus c'est haut, plus c'est suspect."""
        if not text: return 0
        probs = [n/len(text) for n in Counter(text).values()]
        entropy = -sum(p * math.log2(p) for p in probs)
        # Normalisation : 0 (texte simple) à 1 (base64/chiffré)
        return min(entropy / 8.0, 1.0)

    def get_rarity_score(self, signature):
        """Calcule la rareté (d5). 1.0 = Première fois qu'on voit cette signature."""
        count = self.known_signatures.get(signature, 0)
        self.known_signatures[signature] = count + 1
        # Formule simple : plus on le voit, plus le score descend vers 0
        return 1.0 / (count + 1)

    def process_log(self, log_data):
        """Transforme un dictionnaire de log en vecteur 5D."""
        # d1: Criticité (Simulé par mot-clé dans l'URL)
        d1 = 0.9 if "admin" in log_data['url'] or "login" in log_data['url'] else 0.2
        
        # d2: Entropie du payload (corps de la requête)
        d2 = self.calculate_entropy(log_data['payload'])
        
        # d3: Fréquence (Simulé ici par une valeur fixe ou calculée)
        d3 = 0.5 
        
        # d4: Intensité (Méthode HTTP)
        methods = {"GET": 0.2, "POST": 0.6, "PUT": 0.8, "DELETE": 1.0}
        d4 = methods.get(log_data['method'], 0.1)
        
        # d5: Rareté de l'User-Agent ou de l'IP
        d5 = self.get_rarity_score(log_data['user_agent'])
        
        return [d1, d2, d3, d4, d5]

# --- TEST RAPIDE ---
v = Vectorizer()
log_normal = {'url': '/index.php', 'payload': 'id=1', 'method': 'GET', 'user_agent': 'Mozilla/5.0'}
log_suspect = {'url': '/admin/config', 'payload': 'aW5qZWN0X3NoZWxsX2NvZGU=', 'method': 'POST', 'user_agent': 'Custom-Scanner-v1'}

print(f"Vecteur Normal : {v.process_log(log_normal)}")
print(f"Vecteur Suspect : {v.process_log(log_suspect)}")