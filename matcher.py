import json
import math

class CyberMatcher:
    def __init__(self, library_path='mitre_v2_vectorized.json'):
        """Initialise le moteur en chargeant la bibliothèque en RAM."""
        self.library = self.load_library(library_path)
        print(f"[MATCHER] Bibliothèque chargée avec {len(self.library)} techniques.")

    def load_library(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def calculate_euclidean_distance(self, v1, v2):
        """Calcule la distance mathématique entre deux vecteurs 5D."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def predict_attack(self, user_vector, threshold=0.6, top_n=3):
        results = []
        for technique in self.library:
            mitre_vector = technique.get('v_vector')
            if not mitre_vector or len(mitre_vector) != 5:
                continue
            
            distance = self.calculate_euclidean_distance(user_vector, mitre_vector)
            
            results.append({
                'tid': technique['tid'],
                'name': technique['name'],
                'distance': round(distance, 4)
            })
        
        # On trie TOUS les résultats par distance (du plus proche au plus éloigné)
        results.sort(key=lambda x: x['distance'])
        
        # On sépare ce qui est une ALERTE (sous le seuil) du reste
        alerts = [r for r in results[:top_n] if r['distance'] <= threshold]
        closest = results[:top_n]
        
        return alerts, closest

# --- TEST DU MOTEUR EN CONDITIONS SIMULÉES ---
if __name__ == "__main__":
    matcher = CyberMatcher()
    
    log_suspect = [0.2, 0.8, 0.6, 0.9, 0.5]
    print(f"\n[ANALYSE] Vecteur entrant : {log_suspect}")
    
    # On récupère à la fois les alertes ET le top 3 global
    alerts, closest = matcher.predict_attack(log_suspect, threshold=0.6)
    
    print("\n--- TOP 3 DES TECHNIQUES LES PLUS PROCHES (Pour analyse) ---")
    for c in closest:
        print(f" -> {c['tid']} | Distance : {c['distance']}")
    
    if alerts:
        print("\n🚨 ALERTES DÉCLENCHÉES (Distance < 0.6) 🚨")
        for alert in alerts:
            print(f" -> {alert['tid']} : {alert['name']}")
    else:
        print("\n✅ Aucune alerte : Le vecteur est trop éloigné des modèles connus.")