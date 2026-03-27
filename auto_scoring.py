import json

def calculate_dimension(text, keywords, base_score=0.2, weight=0.15):
    """Calcule le score d'une dimension en fonction de l'apparition de mots-clés."""
    score = base_score
    text_lower = text.lower()
    
    for word in keywords:
        if word in text_lower:
            score += weight
            
    # On plafonne le score à 1.0 (Normalisation)
    return min(score, 1.0)

def vectorize_library():
    print("[1/3] Chargement du squelette MITRE...")
    with open('mitre_v1_skeleton.json', 'r', encoding='utf-8') as f:
        library = json.load(f)

    # Dictionnaires de mots-clés (en anglais, car la base MITRE est en anglais)
    kw_d1_target = ['credential', 'password', 'system', 'root', 'admin', 'database', 'token', 'key']
    kw_d2_entropy = ['obfuscate', 'encode', 'base64', 'encrypt', 'hide', 'pack', 'compress', 'steganography']
    kw_d3_freq = ['scan', 'brute force', 'automated', 'beacon', 'continuous', 'flood', 'script']
    kw_d4_intensity = ['execute', 'delete', 'destroy', 'command', 'shell', 'modify', 'write', 'inject']
    kw_d5_rarity = ['bypass', 'custom', 'exploit', 'vulnerability', 'unusual', 'zero-day', 'evade']

    print(f"[2/3] Analyse heuristique de {len(library)} techniques...")
    
    for entry in library:
        # On fusionne le nom et la description pour la recherche
        full_text = entry['name'] + " " + entry['description']
        
        # Recalcul automatique des vecteurs
        v_vector = [
            round(calculate_dimension(full_text, kw_d1_target, base_score=0.3), 2),
            round(calculate_dimension(full_text, kw_d2_entropy, base_score=0.1), 2),
            round(calculate_dimension(full_text, kw_d3_freq, base_score=0.4), 2),
            round(calculate_dimension(full_text, kw_d4_intensity, base_score=0.2), 2),
            round(calculate_dimension(full_text, kw_d5_rarity, base_score=0.3), 2)
        ]
        
        entry['v_vector'] = v_vector
        entry['status'] = "auto_vectorized"

    print("[3/3] Sauvegarde de la bibliothèque finalisée...")
    with open('mitre_v2_vectorized.json', 'w', encoding='utf-8') as f:
        json.dump(library, f, indent=4, ensure_ascii=False)
        
    print("[TERMINÉ] 'mitre_v2_vectorized.json' est prêt !")

if __name__ == "__main__":
    vectorize_library()