import mysql.connector
import struct
import uuid
from mysql.connector import Error

class CyberPathDB:
    def __init__(self, host='localhost', user='root', password='', database='cyber_path'):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor()
            print("[DB] Connexion réussie à MariaDB.")
        except Error as e:
            print(f"[!] Erreur de connexion : {e}")

    def register_entity(self, entity_id_str):
        """Enregistre un nouvel ID (ex: IP ou empreinte) en format binaire 16 octets."""
        # Conversion du string UUID ou IP en binaire 16 octets
        uid_bin = uuid.uuid5(uuid.NAMESPACE_DNS, entity_id_str).bytes
        
        query = "INSERT IGNORE INTO entities (id_emp) VALUES (%s)"
        self.cursor.execute(query, (uid_bin,))
        self.conn.commit()
        return uid_bin

    def insert_vector(self, uid_bin, vector_list):
        """
        Compresse 5 floats en 20 octets binaires et les insère.
        vector_list: [d1, d2, d3, d4, d5]
        """
        if len(vector_list) != 5:
            raise ValueError("Le vecteur doit contenir exactement 5 dimensions.")

        # Passage en binaire (5 floats = 20 octets)
        binary_data = struct.pack('5f', *vector_list)

        query = "INSERT INTO trajectories (id_emp, vector_data) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (uid_bin, binary_data))
            self.conn.commit()
        except Error as e:
            print(f"[!] Erreur d'insertion : {e}")

    def get_last_trajectories(self, uid_bin, limit=10):
        """Récupère et décompresse les derniers vecteurs d'une entité."""
        query = "SELECT vector_data FROM trajectories WHERE id_emp = %s ORDER BY timestamp DESC LIMIT %s"
        self.cursor.execute(query, (uid_bin, limit))
        
        results = []
        for (bin_data,) in self.cursor.fetchall():
            # Décompression du binaire vers liste de floats
            vector = struct.unpack('5f', bin_data)
            results.append(vector)
        return results

    def close(self):
        self.cursor.close()
        self.conn.close()

# --- EXEMPLE D'UTILISATION ---
if __name__ == "__main__":
    db = CyberPathDB()
    
    # 1. On identifie une machine (ex: par son IP)
    my_id = db.register_entity("192.168.1.50")
    
    # 2. On insère un vecteur simulé (T1059 : d1=0.8, d2=0.9...)
    # Ce vecteur ne prend que 20 octets en base !
    sample_v = [0.8, 0.9, 0.7, 1.0, 0.6]
    db.insert_vector(my_id, sample_v)
    
    # 3. On relit pour vérifier
    history = db.get_last_trajectories(my_id)
    print(f"Dernier vecteur récupéré : {history[0]}")
    
    db.close()