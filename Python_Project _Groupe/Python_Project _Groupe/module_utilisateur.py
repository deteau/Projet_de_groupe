import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
import shutil
import db_manager 

photos_selectionnees_temp = []

def selectionner_photos_preteur(label_img_widget):
    """
    Permet à l'utilisateur de sélectionner des photos (jusqu'à 3) pour un objet.
    Les photos sont copiées dans le dossier 'images' de l'application.
    Met à jour un widget (label_img_widget) avec les noms des fichiers sélectionnés.
    """
    global photos_selectionnees_temp

    
    photos_selectionnees_temp.clear()

    fichiers = filedialog.askopenfilenames(
        title="Choisir jusqu'à 3 images (PNG, JPG)",
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )

    
    os.makedirs("images", exist_ok=True)

    for f in fichiers:
        if len(photos_selectionnees_temp) < 3:
            nom_fichier = os.path.basename(f) 
            destination_path = os.path.join("images", nom_fichier) 

            try:
                
                shutil.copy(f, destination_path)
                # Ajoute le chemin de destination (relatif au projet) à la liste temporaire.
                photos_selectionnees_temp.append(destination_path)
            except shutil.SameFileError:
                # Si le fichier existe déjà à la destination et est le même, on l'ajoute sans copier.
                photos_selectionnees_temp.append(destination_path)
            except Exception as e:
                # Gère les autres erreurs de copie (permissions, etc.)
                messagebox.showerror("Erreur de copie", f"Impossible de copier l'image {nom_fichier}: {e}")
        else:
            messagebox.showwarning("Limite atteinte", "Vous ne pouvez choisir que 3 images maximum par objet.")
            break # Arrête de traiter d'autres fichiers si la limite est atteinte

    if photos_selectionnees_temp:
        # Met à jour le label de l'interface utilisateur pour montrer les noms des fichiers sélectionnés.
        label_img_widget.configure(text="\n".join(os.path.basename(p) for p in photos_selectionnees_temp))
    else:
        # Si aucune photo n'est sélectionnée ou si la liste est vide.
        label_img_widget.configure(text="Aucune image sélectionnée")

def reset_photos_selectionnees():
    """
    Réinitialise la liste des photos sélectionnées temporairement.
    À appeler après que le formulaire de proposition de matériel a été soumis ou annulé.
    """
    global photos_selectionnees_temp
    photos_selectionnees_temp.clear()

def enregistrer_materiel_preteur(data, on_success_callback, on_fail_callback):
    """
    Valide les données du formulaire de proposition de matériel d'un prêteur
    et les insère dans la base de données via db_manager.
    Retourne True si l'opération est un succès, False sinon.
    """
    # Récupère les données du dictionnaire 'data'
    nom = data.get('nom')
    numero = data.get('numero')
    mail = data.get('mail')
    materiel = data.get('materiel')
    # Les images sont récupérées depuis la liste globale temporaire
    images = photos_selectionnees_temp

    # Validation des champs obligatoires
    if not nom or not numero or not mail or not materiel:
        messagebox.showerror("Erreur de saisie", "Les champs Nom, Numéro, Mail et Nom du Matériel sont obligatoires.")
        return False

    # Préparer les données pour l'insertion dans la base de données.
    # Les champs 'etat_materiel', 'disponibilite', 'contexte' peuvent être par défaut ici
    # ou provenir de l'UI si tu ajoutes des options de sélection pour eux.
    db_data = {
        "nom": nom,
        "numero": numero,
        "mail": mail,
        "materiel": materiel,
        "etat_materiel": data.get('etat_materiel', 'Bon'), 
        "disponibilite": data.get('disponibilite', 'Disponible'), 
        "contexte": data.get('contexte', 'Général'), 
        "images": images # Passe les chemins d'images copiés
    }

    try:
        db_manager.insert_preteur_data(db_data)
        on_success_callback()
        messagebox.showinfo("Succès", "Votre proposition de matériel a été soumise pour approbation.")
        reset_photos_selectionnees() # Réinitialise la liste des photos après une soumission réussie
        return True
    except Exception as e:
        messagebox.showerror("Erreur BDD", f"Erreur lors de l'enregistrement de la proposition: {e}")
        return False

def enregistrer_demande_emprunteur(data):
    """
    Valide les données du formulaire de demande d'emprunt d'un emprunteur
    et les insère dans la base de données via db_manager.
    Retourne True si l'opération est un succès, False sinon.
    """
    nom = data.get('nom')
    numero = data.get('numero')
    mail = data.get('mail')
    objet_id = data.get('objet_id') 
    raison = data.get('raison')

    # Validation des champs obligatoires
    if not nom or not numero or not mail or not objet_id or not raison:
        messagebox.showerror("Erreur de saisie", "Tous les champs sont obligatoires pour la demande d'emprunt.")
        return False

    objet_details = db_manager.get_object_details_by_id(objet_id)
    if not objet_details:
        messagebox.showerror("Erreur", "Objet sélectionné introuvable dans la base de données. Veuillez réessayer.")
        return False

    nom_materiel_demande = objet_details.get('nom_objet', 'Objet Inconnu')

    db_data = {
        "nom": nom,
        "numero": numero,
        "mail": mail,
        "objet_id": objet_id,
        "nom_materiel_demande": nom_materiel_demande,
        "raison": raison
    }

    try:
        db_manager.insert_emprunteur_data(db_data)
        messagebox.showinfo("Succès", "Votre demande d'emprunt a été soumise avec succès.")
        return True
    except Exception as e:
        messagebox.showerror("Erreur BDD", f"Erreur lors de l'enregistrement de la demande: {e}")
        return False

def get_objets_disponibles_for_emprunteur_ui():
    """
    Récupère la liste de tous les objets approuvés et disponibles dans la base de données.
    Cette fonction est appelée par l'interface utilisateur pour afficher les objets
    que les emprunteurs peuvent demander.
    """
    # Appel direct à la fonction de db_manager qui retourne les objets déjà formatés.
    return db_manager.get_all_materiel()