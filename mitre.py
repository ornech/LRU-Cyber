import requests
import json
from stix2 import MemoryStore, Filter

def extract_mitre():
    url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    
    print("[1/4] Téléchargement de la base MITRE...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # On extrait uniquement la liste des objets STIX
        stix_objects = data.get('objects', [])
        print(f"      -> Succès : {len(stix_objects)} objets STIX récupérés.")
    except Exception as e:
        print(f"      [!] Erreur lors du téléchargement : {e}")
        return

    print("[2/4] Initialisation du MemoryStore...")
    # On passe la liste d'objets directement
    src = MemoryStore(stix_data=stix_objects)
    
    print("[3/4] Recherche des techniques (attack-pattern)...")
    # CORRECTION : Utilisation de l'objet Filter au lieu d'un dict
    query_filter = Filter("type", "=", "attack-pattern")
    techniques = src.query([query_filter])
    
    print(f"      -> {len(techniques)} techniques identifiées.")

    print("[4/4] Génération du référentiel CYBER-PATH...")
    cyber_path_library = []

    # On trie pour avoir des résultats cohérents (les plus récentes en premier ou par nom)
    for t in techniques:
        # On ignore les techniques révoquées ou obsolètes
        if getattr(t, 'x_mitre_is_revoked', False) or getattr(t, 'x_mitre_deprecated', False):
            continue

        # Extraction du TID (ex: T1190)
        tid = "Unknown"
        if hasattr(t, 'external_references'):
            for ref in t.external_references:
                if ref.source_name == 'mitre-attack':
                    tid = ref.external_id
                    break
        
        # On ne garde que les vraies techniques
        if tid == "Unknown": continue

        entry = {
            "tid": tid,
            "name": t.name,
            "description": t.description[:200].replace('\n', ' ') + "...",
            "v_vector": [0.5, 0.5, 0.5, 0.5, 0.5], # Squelette à calibrer
            "status": "skeleton"
        }
        cyber_path_library.append(entry)

    # Sauvegarde
    output_file = 'mitre_v1_skeleton.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cyber_path_library, f, indent=4, ensure_ascii=False)
    
    print(f"\n[TERMINÉ] Référentiel sauvegardé : '{output_file}'.")
    print(f"Nombre total de techniques exportées : {len(cyber_path_library)}")

if __name__ == "__main__":
    extract_mitre()