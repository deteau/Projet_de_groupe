import sys
import os
import customtkinter

import tkinter.messagebox as messagebox 

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


from UI_interface import AppUI
import module_utilisateur 
import admin_logic
import db_manager


if __name__ == "__main__":
    
    db_manager.init_db()

    
    customtkinter.set_appearance_mode("System") 
    customtkinter.set_default_color_theme("blue")  

    
    root = customtkinter.CTk()
    root.geometry("1000x600")
    root.title("Application de Gestion de Matériel (Prêt et Emprunt)")

    
    ui_instance = AppUI(root)

    
    commands = {
        "ouvrir_admin_login": lambda: ui_instance.afficher_page("admin_login"),
        "retour_accueil": lambda: ui_instance.afficher_page("accueil"),
        "ouvrir_users_choix": lambda: ui_instance.afficher_page("users_choix"),
        "ouvrir_formulaire_preteur": lambda: ui_instance.afficher_page("form_preteur"),
        "retour_users_choix": lambda: ui_instance.afficher_page("users_choix"),
        "valider_preteur_form": lambda: module_utilisateur.enregistrer_materiel_preteur(
            ui_instance.get_form_data("preteur"),
            lambda: (
                ui_instance.clear_form_data("preteur"),
                ui_instance.afficher_page("accueil"),
                messagebox.showinfo("Succès", "Votre proposition de matériel a été soumise avec succès et est en attente d'approbation.")
            ),
            lambda msg: messagebox.showerror("Erreur", f"Échec de la soumission: {msg}")
        ),
        "ouvrir_emprunteur_selection": lambda: ui_instance.afficher_page("emprunteur_selection"),
        "select_emprunteur_item": lambda item_id: ui_instance.update_emprunteur_details_page(item_id),# CORRIGÉ: Appelle la mise à jour des détails

        "retour_emprunteur_selection": lambda: (
            ui_instance.clear_form_data("emprunteur"), # Vide le formulaire de détails de l'emprunteur au retour
            ui_instance.afficher_page("emprunteur_selection")
        ),
        "valider_emprunteur_form": lambda data, success_cb, error_cb: module_utilisateur.enregistrer_demande_emprunteur(data),

        "ouvrir_historique_admin": lambda: (
            print("DEBUG_BUTTON_CLICK: 'Historique' button clicked. Calling create_historique_admin_page."),
            ui_instance.create_historique_admin_page()),
        
        "ouvrir_approbation_admin": lambda: ui_instance.create_approbation_admin_page(commands),
        
        "approuver_demande_admin_callback": lambda demande_id, demande_type, window_ref: admin_logic.approuver_demande_admin(demande_id, demande_type, window_ref),
        "refuser_demande_admin_callback": lambda demande_id, demande_type, window_ref: admin_logic.refuser_demande_admin(demande_id, demande_type, window_ref),

        "ouvrir_changement_mdp_admin": lambda: ui_instance.create_changement_mdp_admin_page(), 
        
        "ouvrir_admin_dashboard": lambda: ui_instance.afficher_page("admin_dashboard"),
    }

   
    ui_instance.commands_ref = commands

    
    ui_instance.setup_gui_elements(commands)

   
    root.mainloop()