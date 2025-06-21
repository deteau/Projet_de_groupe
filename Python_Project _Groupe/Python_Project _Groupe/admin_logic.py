
import tkinter.messagebox as messagebox

from db_manager import (
    check_admin_password,
    update_admin_password,
    get_pending_demandes,
    get_historique_prets
)
import sqlite3
import db_manager
import datetime

DEFAULT_ADMIN_PASSWORD = "admin_password" 
HASH_ALGORITHM = "sha256" 

def valider_admin_login(password_entry, success_callback, fail_callback):
    """
    Valide le mot de passe de l'administrateur.
    Appelle success_callback en cas de succès, ou fail_callback en cas d'échec.
    Utilise messagebox pour les retours utilisateurs.
    """
    username = 'admin' 

    if check_admin_password(username, password_entry):
        messagebox.showinfo("Connexion", "Connexion administrateur réussie !")
        success_callback() 
    else:
        messagebox.showerror("Erreur de connexion", "Mot de passe incorrect.")
        fail_callback() 



import db_manager
import tkinter.messagebox as messagebox

def approuver_demande_admin(demande_id, demande_type, refresh_callback=None):
    try:
        if db_manager.approve_demande(demande_id, demande_type):
            messagebox.showinfo("Succès", "Demande approuvée avec succès.")
            if refresh_callback:
                refresh_callback() 
        else:
            messagebox.showerror("Erreur", "La demande n'a pas pu être approuvée.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de l'approbation: {e}")

def refuser_demande_admin(demande_id, demande_type, refresh_callback=None): 
    try:
        if db_manager.reject_demande(demande_id, demande_type):
            messagebox.showinfo("Succès", "Demande refusée avec succès.")
            if refresh_callback:
                refresh_callback() 
        else:
            messagebox.showerror("Erreur", "La demande n'a pas pu être refusée.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec du refus: {e}")

def valider_changement_mdp_admin(old_pass, new_pass, confirm_pass, window_to_close=None):
    """
    Valide et effectue le changement de mot de passe admin.
    Utilise messagebox pour les retours utilisateurs.
    """
    if not old_pass or not new_pass or not confirm_pass:
        messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
        return False

    if new_pass != confirm_pass:
        messagebox.showerror("Erreur", "Le nouveau mot de passe et sa confirmation ne correspondent pas.")
        return False

    if old_pass == new_pass:
        messagebox.showerror("Erreur", "Le nouveau mot de passe ne peut pas être identique à l'ancien.")
        return False

    username = 'admin' 
    if update_admin_password(username, old_pass, new_pass):
        messagebox.showinfo("Succès", "Mot de passe mis à jour avec succès.")

        return True
    else:
        messagebox.showerror("Erreur", "Ancien mot de passe incorrect.")
        return False


def get_pending_demandes_for_admin():
    """Récupère les demandes en attente pour le tableau de bord admin."""
    return get_pending_demandes()

def get_historique_for_admin():
    """Récupère l'historique complet pour le tableau de bord admin."""
    return get_historique_prets()

