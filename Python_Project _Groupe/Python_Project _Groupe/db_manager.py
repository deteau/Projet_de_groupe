
import sqlite3

import datetime  # Ajouté pour gérer les dates

DB_NAME = "gestion_materiel.db"


def init_db():
    """
    Initialise la base de données, crée les tables si elles n'existent pas,
    et insère l'administrateur par défaut.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table des prêteurs (materiel qu'ils proposent)
    # Ajout de 'date_proposition' pour l'historique et le suivi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preteurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_prenom TEXT NOT NULL,
            numero TEXT,
            mail TEXT,
            nom_materiel TEXT NOT NULL,
            etat_materiel TEXT DEFAULT 'Bon', -- Valeur par défaut
            disponibilite TEXT DEFAULT 'Disponible', -- 'Disponible', 'Emprunté', 'En attente'
            contexte TEXT DEFAULT 'Autre', -- Catégorie de l'objet (ex: 'Outil', 'Livre', 'Électronique')
            image_paths TEXT, -- Chemins d'images séparés par des virgules
            approuve INTEGER DEFAULT 0, -- 0: En attente, 1: Approuvé (pour la proposition de matériel)
            date_proposition TEXT DEFAULT CURRENT_TIMESTAMP -- Date de la proposition
        )
    """)

    # Table des emprunteurs (leurs demandes d'emprunt)
    # 'statut' peut être 'En attente', 'Approuvé', 'Refusé'
    # 'date_emprunt_effective' et 'date_retour_prevue' seront mises à jour lors de l'approbation
    # 'date_retour_reelle' sera mise à jour lors du retour effectif
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emprunteurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_prenom TEXT NOT NULL,
            numero TEXT,
            mail TEXT,
            id_materiel_demande INTEGER NOT NULL, -- ID de l'objet du prêteur demandé
            nom_materiel_demande TEXT NOT NULL,
            raison_demande TEXT,
            date_demande TEXT DEFAULT CURRENT_TIMESTAMP, -- Date de la soumission de la demande
            statut TEXT DEFAULT 'En attente',
            date_emprunt_effective TEXT, -- Date à laquelle l'emprunt a été validé par l'admin
            date_retour_prevue TEXT,    -- Date de retour prévue
            date_retour_reelle TEXT,    -- Date de retour réelle
            FOREIGN KEY (id_materiel_demande) REFERENCES preteurs(id)
        )
    """)

    # Table des administrateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Insérer l'admin par défaut si n'existe pas
    # ATTENTION : En production, 'admin123' devrait être un hachage sécurisé (ex: bcrypt)
    cursor.execute("INSERT OR IGNORE INTO admins (username, password_hash) VALUES (?, ?)", ('admin', 'admin123'))

    conn.commit()
    conn.close()


def insert_preteur_data(data):
    """
    Insère les données d'un prêteur (proposition de matériel).
    Initialise 'approuve' à 0 (en attente) et 'disponibilite' à 'Disponible' (une fois approuvé).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    image_paths_str = ','.join(data.get('images', [])) if data.get('images') else ''

    # Les valeurs par défaut sont déjà définies dans le CREATE TABLE.
    # Ici, on utilise data.get pour prendre les valeurs si elles sont fournies,
    # sinon les valeurs par défaut de la DB s'appliqueront si le champ est omis (moins courant en INSERT)
    # ou si on les passe explicitement ici (plus sûr pour le contrôle applicatif).
    etat_materiel = data.get('etat_materiel', 'Bon')
    disponibilite = data.get('disponibilite', 'Disponible')
    contexte = data.get('contexte', 'Autre')

    # La date de proposition est gérée par CURRENT_TIMESTAMP par défaut dans la DB, pas besoin de la passer ici.
    cursor.execute("""
        INSERT INTO preteurs (nom_prenom, numero, mail, nom_materiel, etat_materiel, disponibilite, contexte, image_paths, approuve)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['nom'], data['numero'], data['mail'], data['materiel'],
          etat_materiel, disponibilite, contexte, image_paths_str, 0))  # approuve = 0 par défaut
    conn.commit()
    conn.close()


def insert_emprunteur_data(data):
    """
    Insère une demande d'emprunteur.
    Le statut par défaut est 'En attente'.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # On insère l'ID et le nom de l'objet demandé
    cursor.execute("""
        INSERT INTO emprunteurs (nom_prenom, numero, mail, id_materiel_demande, nom_materiel_demande, raison_demande, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data['nom'], data['numero'], data['mail'], data['objet_id'], data['nom_materiel_demande'], data['raison'],
          'En attente'))
    conn.commit()
    conn.close()


def check_admin_password(username, password):
    """Vérifie le mot de passe d'un administrateur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == password:  # Comparaison directe (À REMPLACER PAR HASHING EN PROD)
        return True
    return False


def update_admin_password(username, old_password, new_password):
    """Met à jour le mot de passe d'un administrateur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result and result[0] == old_password:  # Vérification de l'ancien mot de passe
        cursor.execute("UPDATE admins SET password_hash = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def get_all_materiel():
    """
    Récupère tous les objets (matériel) des prêteurs qui sont approuvés (approuve=1)
    et dont la disponibilité est 'Disponible'.
    Formate les données pour l'affichage dans l'interface utilisateur.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Sélectionne les objets approuvés et disponibles pour l'emprunt
    cursor.execute("""
        SELECT id, nom_materiel, nom_prenom, disponibilite, etat_materiel, contexte, image_paths
        FROM preteurs
        WHERE approuve = 1 AND disponibilite = 'Disponible'
    """)
    objets = cursor.fetchall()
    conn.close()

    formatted_objets = []
    for obj in objets:
        formatted_objets.append({
            "id": obj['id'],
            "nom_objet": obj['nom_materiel'],
            "proprietaire_nom": obj['nom_prenom'],
            "statut": obj['disponibilite'],
            "etat": obj['etat_materiel'],
            "contexte": obj['contexte'],
            "image_paths": obj['image_paths'].split(',') if obj['image_paths'] else []
        })
    return formatted_objets


def get_object_details_by_id(object_id):
    """
    Récupère les détails complets d'un objet par son ID depuis la table des prêteurs.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nom_materiel, etat_materiel, disponibilite, nom_prenom, numero, mail, contexte, image_paths FROM preteurs WHERE id = ?",
        (object_id,))
    details = cursor.fetchone()
    conn.close()
    if details:
        return {
            "id": details['id'],
            "nom_objet": details['nom_materiel'],
            "etat": details['etat_materiel'],
            "disponibilite": details['disponibilite'],
            "proprietaire_nom": details['nom_prenom'],
            "proprietaire_numero": details['numero'],  
            "mail_proprietaire": details['mail'],
            "categorie": details['contexte'],
            "image_paths": details['image_paths'].split(',') if details['image_paths'] else []
        }
    return None


def get_pending_demandes():
    """
    Récupère toutes les demandes en attente d'approbation :
    - Les nouvelles propositions de matériel (preteurs.approuve = 0)
    - Les demandes d'emprunt (emprunteurs.statut = 'En attente')
    Retourne une liste unifiée de dictionnaires.
    """

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    combined_requests = []

    # Demandes de prêteurs non approuvées (nouvel objet proposé)
    cursor.execute("""
        SELECT id, nom_prenom, nom_materiel, date_proposition, 'preteur' AS type
        FROM preteurs WHERE approuve = 0 
    """)
    preteurs_requests = cursor.fetchall()

    for r in preteurs_requests:
        combined_requests.append({
            "id": r['id'],
            "type": r['type'],  # 'preteur'
            "nom_demandeur": r['nom_prenom'],
            "nom_objet_demande": r['nom_materiel'],
            "statut": "En attente (Proposition)",  # Statut fixe pour les propositions de prêteurs
            "raison_demande": "Proposition de nouveau matériel.",
            "date_demande": r['date_proposition']
        })
    cursor.execute("""
            SELECT e.id, e.nom_prenom AS nom_emprunteur, p.nom_materiel AS nom_objet_demande,
                   e.raison_demande, e.date_demande, e.statut, 'emprunteur' AS type
            FROM emprunteurs e
            JOIN preteurs p ON e.id_materiel_demande = p.id
            WHERE e.statut = 'En attente'
        """)
    emprunteurs_requests = cursor.fetchall()

    for r in emprunteurs_requests:
        combined_requests.append({
            "id": r['id'],
            "type": r['type'],  
            "nom_demandeur": r['nom_emprunteur'],
            "nom_objet_demande": r['nom_objet_demande'],
            "raison_demande": r['raison_demande'],
            "date_demande": r['date_demande'],
            "statut": r['statut']  
        })
    conn.close()
    return combined_requests




def get_historique_prets():
    """
    Récupère l'historique complet des transactions :
    - Matériel proposé et approuvé (approuve = 1)
    - Demandes d'emprunt approuvées ou refusées.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Historique des propositions de matériel approuvées par les prêteurs
    # Ces sont des objets qui ont été ajoutés et sont disponibles/empruntés
    cursor.execute("""
        SELECT id, nom_prenom AS proprietaire_nom, nom_materiel AS nom_objet,
               etat_materiel, disponibilite AS statut_objet, contexte,
               'Proposition Matériel Approuvée' AS type_enregistrement,
               date_proposition,
               NULL AS emprunteur_nom, NULL AS raison_emprunt,
               NULL AS date_emprunt_effective, NULL AS date_retour_prevue, NULL AS date_retour_reelle
        FROM preteurs
        WHERE approuve = 1
    """)
    approved_preteurs_history = cursor.fetchall()

    # Historique des demandes d'emprunt (approuvées ou refusées)
    cursor.execute("""
        SELECT e.id, p.nom_materiel AS nom_objet, p.nom_prenom AS proprietaire_nom,
               e.nom_prenom AS emprunteur_nom, e.raison_demande AS raison_emprunt,
               e.date_demande AS date_demande_soumission, e.statut AS statut_demande,
               e.date_emprunt_effective, e.date_retour_prevue, e.date_retour_reelle,
               'Demande Emprunt Traitée' AS type_enregistrement
        FROM emprunteurs e
        JOIN preteurs p ON e.id_materiel_demande = p.id
        WHERE e.statut IN ('Approuvé', 'Refusé')
    """)
    processed_emprunteurs_history = cursor.fetchall()
    conn.close()

    combined_history = []
    # Convertir Row objects en dictionnaires pour faciliter la manipulation
    for r in approved_preteurs_history:
        combined_history.append(dict(r))
    for r in processed_emprunteurs_history:
        combined_history.append(dict(r))

    # Retourne l'historique combiné
    return combined_history


def approve_request(request_id, request_type):
    """
    Approuve une demande basée sur son type (prêteur ou emprunteur).
    Met à jour les statuts dans les tables appropriées.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    if request_type == 'preteur':
        # Marque la proposition de matériel comme approuvée
        cursor.execute("UPDATE preteurs SET approuve = 1, disponibilite = 'Disponible' WHERE id = ?", (request_id,))
    elif request_type == 'emprunteur':
        # Marque la demande d'emprunt comme approuvée
        # Enregistre la date effective de l'emprunt et une date de retour prévue (ex: +7 jours)
        date_retour_prevue = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute(
            "UPDATE emprunteurs SET statut = 'Approuvé', date_emprunt_effective = ?, date_retour_prevue = ? WHERE id = ?",
            (current_date, date_retour_prevue, request_id))

        # Change la disponibilité de l'objet du prêteur à 'Emprunté'
        cursor.execute("SELECT id_materiel_demande FROM emprunteurs WHERE id = ?", (request_id,))
        materiel_id = cursor.fetchone()
        if materiel_id:
            cursor.execute("UPDATE preteurs SET disponibilite = 'Emprunté' WHERE id = ?", (materiel_id[0],))
    conn.commit()
    conn.close()


def refuse_request(request_id, request_type):
    """
    Refuse une demande basée sur son type (prêteur ou emprunteur).
    Pour les prêteurs, la demande reste non approuvée. Pour les emprunteurs, le statut est 'Refusé'.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if request_type == 'preteur':
        # Pour une demande de prêteur refusée, l'état 'approuve = 0' suffit.
        # On peut potentiellement ajouter un champ 'statut_demande' ('Refusée', 'En attente')
        # à la table 'preteurs' pour une meilleure traçabilité, mais pour l'instant, on laisse ainsi.
        pass  # La demande reste simplement non approuvée (approuve = 0)
    elif request_type == 'emprunteur':
        # Marque la demande d'emprunt comme refusée
        cursor.execute("UPDATE emprunteurs SET statut = 'Refusé' WHERE id = ?", (request_id,))
        # Si une demande d'emprunt est refusée, l'objet reste 'Disponible' (pas de changement de statut pour le matériel)
    conn.commit()
    conn.close()


# NOUVELLE FONCTION : Marquer un objet comme retourné
def mark_object_returned(emprunteur_id, materiel_id):
    """
    Marque une demande d'emprunt comme 'Retourné' et met à jour la disponibilité de l'objet.
    Nécessite l'ID de l'enregistrement d'emprunt et l'ID du matériel.
    Cette fonction serait appelée depuis l'interface admin pour gérer les retours.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Mettre à jour le statut de la demande d'emprunt et la date de retour réelle
    cursor.execute("UPDATE emprunteurs SET statut = 'Retourné', date_retour_reelle = ? WHERE id = ?",
                   (current_date, emprunteur_id))

    # Rendre l'objet de nouveau 'Disponible'
    cursor.execute("UPDATE preteurs SET disponibilite = 'Disponible' WHERE id = ?", (materiel_id,))

    conn.commit()
    conn.close()

def get_materiel_id_from_emprunteur_request(emprunteur_req_id):
    """
    Récupère l'ID du matériel associé à une demande d'emprunteur spécifique.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_materiel_demande FROM emprunteurs WHERE id = ?", (emprunteur_req_id,))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()


# Initialisation de la base de données au lancement du script
if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès.")

    