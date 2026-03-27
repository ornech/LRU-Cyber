import json
from mitreattack.stix20 import MitreAttackData

def update_library_with_official_data():
    # 1. Charger les données STIX du MITRE (à télécharger au préalable ou via URL)
    # wget https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
    url = "enterprise-attack.json"
    mitre_data = MitreAttackData(url)

    print("[1/2] Récupération des techniques via la lib officielle...")
    techniques = mitre_data.get_techniques()
    
    cyber_path_library = []

    for t in techniques:
        # On récupère le TID (ex: T1059)
        tid = mitre_data.get_attack_id(t.id)
        
        # On récupère les tactiques associées (Initial Access, Persistence, etc.)
        tactics = [phase.tactic_name for phase in t.kill_chain_phases] if hasattr(t, 'kill_chain_phases') else []

        entry = {
            "tid": tid,
            "name": t.name,
            "description": t.description[:300] + "...",
            "tactics": tactics,
            "v_vector": [0.5, 0.5, 0.5, 0.5, 0.5], # Sera peuplé par auto_scoring.py
            "status": "official_stix"
        }
        cyber_path_library.append(entry)

    with open('mitre_v2_skeleton.json', 'w', encoding='utf-8') as f:
        json.dump(cyber_path_library, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Terminé : {len(cyber_path_library)} techniques importées proprement.")

if __name__ == "__main__":
    update_library_with_official_data()