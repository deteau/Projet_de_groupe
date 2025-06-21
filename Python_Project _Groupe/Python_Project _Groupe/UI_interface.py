import customtkinter
from PIL import Image
import os  # Pour les chemins d'images
import sqlite3


import module_utilisateur
import admin_logic
import db_manager
import tkinter.messagebox as messagebox  


class AppUI:
    def __init__(self, master):
        self.master = master
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

       
        self.current_frame = None 
        self.pages = {}  

        
        self.selected_materiel_nom = None  

        self.emprunteur_selected_object_id = None  
        self.COULEUR_BOUTON = "#2B689C"
        self.COULEUR_VALIDATION = "#32CD32"
        self.COULEUR_RETOUR = "#FF4500"
        self.COULEUR_REFUS = "#CC0000" 


        self.commands_ref = None  

        
        self.preteur_label_img = None
        self.preteur_nom_entry = None
        self.preteur_num_entry = None
        self.preteur_mail_entry = None
        self.preteur_objet_entry = None
        
        self.preteur_etat_materiel_optionmenu = None
        self.preteur_contexte_optionmenu = None

        self.emprunteur_selected_contexte = customtkinter.StringVar(value="Tous les objets")
        self.emprunteur_search_entry = None
        self.emprunteur_listbox = None
        self.emprunteur_nom_entry = None 
        self.emprunteur_num_entry = None
        self.emprunteur_mail_entry = None
        self.emprunteur_raison_text = None
        self.emprunteur_objet_details_text = None

        self.admin_password_entry = None  
        self.admin_approbation_window = None
        self.admin_historique_window = None
        self.admin_change_mdp_window = None

        
        try:
           
            self.admin_icon = customtkinter.CTkImage(light_image=Image.open(os.path.join("images", "Icon_admin.png")),
                                                     size=(200, 200))
            self.user_icon = customtkinter.CTkImage(
                light_image=Image.open(os.path.join("images", "Icon_utilisateur.png")), size=(200, 200))
        except FileNotFoundError as e:
            messagebox.showerror("Erreur de fichier",
                                 f"Impossible de charger une icône : {e}.\nVérifiez le dossier 'images' et les noms de fichiers.")
            self.admin_icon = None
            self.user_icon = None
            
            print(f"ERREUR CRITIQUE DE FICHIER IMAGE : {e}")
            print(
                "Vérifiez que le dossier 'images' est au même niveau que main.py et que les noms de fichiers sont corrects.")


    def setup_gui_elements(self, commands):
        """Configure tous les cadres et widgets de l'interface."""
        self.commands_ref = commands

        
        self._setup_accueil_page(commands)
        self._setup_admin_login_page(commands)
        self._setup_admin_dashboard_page(commands)
        self._setup_users_choix_page(commands)
        self._setup_formulaire_preteur_page(commands)
        self._setup_emprunteur_selection_page(commands)
        self._setup_formulaire_emprunteur_details_page(commands)

        # Afficher la page d'accueil au démarrage
        self.afficher_page("accueil")

    def afficher_page(self, page_key):
        """Affiche la page spécifiée et cache les autres."""
        if self.current_frame:
            self.current_frame.pack_forget()

        target_frame = self.pages.get(page_key)
        if target_frame:
            target_frame.pack(fill="both", expand=True)
            self.current_frame = target_frame

            # Logique spécifique à la page quand elle est affichée
            if page_key == "form_preteur":
                # Réinitialise les photos sélectionnées et le label d'image du prêteur
                module_utilisateur.reset_photos_selectionnees()
                if self.preteur_label_img:
                    self.preteur_label_img.configure(text="Aucune image", image=None)
                # Vide aussi les champs du formulaire prêteur
                self.clear_form_data("preteur")
            elif page_key == "emprunteur_selection":
                # S'assurer que la liste des objets est rafraîchie lors de l'affichage de la page
                self._update_emprunteur_listbox()
                self.emprunteur_search_entry.delete(0, customtkinter.END)  # Vide le champ de recherche
                self.emprunteur_selected_contexte.set("Tous les objets")  # Réinitialise le filtre
            elif page_key == "admin_dashboard":
                # Assurez-vous que le champ de mot de passe de connexion est effacé
                if self.admin_password_entry:
                    self.admin_password_entry.delete(0, customtkinter.END)

    def _setup_accueil_page(self, commands):
        """Configure la page d'accueil avec les options Prêteur/Emprunteur/Admin."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["accueil"] = page
        page.grid_rowconfigure((0, 1, 2, 3), weight=1)
        page.grid_columnconfigure((0, 1, 2), weight=1)

        button_frame = customtkinter.CTkFrame(page, corner_radius=10)
        button_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        button_frame.grid_rowconfigure((0, 1, 2), weight=1)
        button_frame.grid_columnconfigure(0, weight=1)

        admin_label = customtkinter.CTkLabel(button_frame, text="Admin", image=self.admin_icon,
                                             compound="top", font=customtkinter.CTkFont(size=20, weight="bold"))
        admin_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        admin_label.bind("<Button-1>", lambda event: commands["ouvrir_admin_login"]())
        admin_label.configure(cursor="hand2")

        preteur_label = customtkinter.CTkLabel(button_frame, text="Utilisateur", image=self.user_icon,
                                               compound="top", font=customtkinter.CTkFont(size=20, weight="bold"))
        preteur_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        preteur_label.bind("<Button-1>", lambda event: commands["ouvrir_users_choix"]())
        preteur_label.configure(cursor="hand2")

        quit_button = customtkinter.CTkButton(page, text="Quitter l'application",
                                              command=self.master.destroy,
                                              fg_color=self.COULEUR_RETOUR, hover_color="#CC3300")
        quit_button.grid(row=2, column=1, pady=10, padx=20, sticky="ew")

    def _setup_admin_login_page(self, commands):
        """Configure la page de connexion de l'administrateur."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["admin_login"] = page
        page.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        page.grid_columnconfigure((0, 1, 2), weight=1)

        login_frame = customtkinter.CTkFrame(page, corner_radius=10)
        login_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        login_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        login_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(login_frame, text="Connexion Administrateur",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        self.admin_password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Mot de passe Admin", show="*")
        self.admin_password_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        
        customtkinter.CTkButton(login_frame, text="Se connecter",
                                command=lambda: admin_logic.valider_admin_login(
                                    self.admin_password_entry.get(),
                                    self.commands_ref["ouvrir_admin_dashboard"],
                                    
                                    lambda: self.admin_password_entry.delete(0, customtkinter.END)
                                ),
                                fg_color=self.COULEUR_VALIDATION, hover_color="#8BD4AF").grid(row=2, column=0, padx=20,
                                                                                              pady=10, sticky="ew")

        customtkinter.CTkButton(login_frame, text="Retour",
                                command=commands["retour_accueil"],
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=3, column=0, padx=20,
                                                                                          pady=5, sticky="ew")

    def _setup_admin_dashboard_page(self, commands):
        """Configure la page du tableau de bord administrateur."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["admin_dashboard"] = page
        page.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        page.grid_columnconfigure((0, 1, 2), weight=1)

        dashboard_frame = customtkinter.CTkFrame(page, corner_radius=10)
        dashboard_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        dashboard_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        dashboard_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(dashboard_frame, text="Tableau de Bord Admin",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        customtkinter.CTkButton(dashboard_frame, text="Approuver Demandes",
                                command=commands["ouvrir_approbation_admin"],
                                fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF").grid(row=1, column=0, padx=20,
                                                                                          pady=10, sticky="ew")

        customtkinter.CTkButton(dashboard_frame, text="Historique des Prêts",
                                command=commands["ouvrir_historique_admin"],
                                fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF").grid(row=2, column=0, padx=20,
                                                                                          pady=10, sticky="ew")

        customtkinter.CTkButton(dashboard_frame, text="Changer Mot de Passe Admin",
                                command=commands["ouvrir_changement_mdp_admin"],
                                fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF").grid(row=3, column=0, padx=20,
                                                                                          pady=10, sticky="ew")

        customtkinter.CTkButton(dashboard_frame, text="Déconnexion",
                                command=commands["retour_accueil"],
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=4, column=0, padx=20,
                                                                                          pady=5, sticky="ew")

    def _setup_users_choix_page(self, commands):
        """Configure la page de choix pour l'utilisateur (Prêteur ou Emprunteur)."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["users_choix"] = page
        page.grid_rowconfigure((0, 1, 2, 3), weight=1)
        page.grid_columnconfigure((0, 1, 2), weight=1)

        choix_frame = customtkinter.CTkFrame(page, corner_radius=10)
        choix_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        choix_frame.grid_rowconfigure((0, 1, 2), weight=1)
        choix_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(choix_frame, text="Vous êtes...",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        customtkinter.CTkButton(choix_frame, text="Un Prêteur",
                                command=commands["ouvrir_formulaire_preteur"],
                                fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF").grid(row=1, column=0, padx=20,
                                                                                          pady=10, sticky="ew")

        customtkinter.CTkButton(choix_frame, text="Un Emprunteur",
                                command=commands["ouvrir_emprunteur_selection"],
                                fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF").grid(row=2, column=0, padx=20,
                                                                                          pady=10, sticky="ew")

        customtkinter.CTkButton(page, text="Retour",
                                command=commands["retour_accueil"],
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=2, column=1, padx=20,
                                                                                          pady=10, sticky="ew")

    def _setup_formulaire_preteur_page(self, commands):
        """Configure la page du formulaire de prêteur."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["form_preteur"] = page
        page.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1) 
        page.grid_columnconfigure((0, 1, 2), weight=1)

        form_frame = customtkinter.CTkFrame(page, corner_radius=10)
        form_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        form_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)  
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(form_frame, text="Formulaire Prêteur",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2,
                                                                                        pady=10)

        customtkinter.CTkLabel(form_frame, text="Nom:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.preteur_nom_entry = customtkinter.CTkEntry(form_frame, placeholder_text="Votre nom")
        self.preteur_nom_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(form_frame, text="Numéro:", anchor="w").grid(row=2, column=0, padx=10, pady=5,
                                                                            sticky="ew")
        self.preteur_num_entry = customtkinter.CTkEntry(form_frame, placeholder_text="Votre numéro de téléphone")
        self.preteur_num_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(form_frame, text="Mail:", anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.preteur_mail_entry = customtkinter.CTkEntry(form_frame, placeholder_text="Votre adresse email")
        self.preteur_mail_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(form_frame, text="Objet:", anchor="w").grid(row=4, column=0, padx=10, pady=5,
                                                                           sticky="ew")
        self.preteur_objet_entry = customtkinter.CTkEntry(form_frame, placeholder_text="Nom de l'objet prêté")
        self.preteur_objet_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # NOUVEAU : Champ pour l'état du matériel
        customtkinter.CTkLabel(form_frame, text="État Matériel:", anchor="w").grid(row=5, column=0, padx=10, pady=5,
                                                                                   sticky="ew")
        self.preteur_etat_materiel_optionmenu = customtkinter.CTkOptionMenu(form_frame,
                                                                            values=["Neuf", "Très bon", "Bon", "Usé",
                                                                                    "Détérioré"])
        self.preteur_etat_materiel_optionmenu.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.preteur_etat_materiel_optionmenu.set("Bon")  # Valeur par défaut

        # NOUVEAU : Champ pour le contexte/catégorie du matériel
        customtkinter.CTkLabel(form_frame, text="Catégorie:", anchor="w").grid(row=6, column=0, padx=10, pady=5,
                                                                               sticky="ew")
        self.preteur_contexte_optionmenu = customtkinter.CTkOptionMenu(form_frame,
                                                                       values=["Outil", "Livre", "Électronique",
                                                                               "Vêtement", "Autre"])
        self.preteur_contexte_optionmenu.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        self.preteur_contexte_optionmenu.set("Autre")  # Valeur par défaut

        customtkinter.CTkButton(form_frame, text="Sélectionner Image(s)",
                                command=lambda: module_utilisateur.selectionner_photos_preteur(self.preteur_label_img),
                               
                                fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF").grid(row=7, column=0, padx=10,
                                                                                          pady=10, sticky="ew")
        self.preteur_label_img = customtkinter.CTkLabel(form_frame, text="Aucune image", bg_color="gray")
        self.preteur_label_img.grid(row=7, column=1, padx=10, pady=10, sticky="nsew")

        customtkinter.CTkButton(form_frame, text="Soumettre",
                                command=commands["valider_preteur_form"],
                                fg_color=self.COULEUR_VALIDATION, hover_color="#8BD4AF").grid(row=8, column=0, padx=10,
                                                                                              pady=10, sticky="ew")

        customtkinter.CTkButton(form_frame, text="Retour",
                                command=commands["retour_users_choix"],
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=8, column=1, padx=10,
                                                                                          pady=10, sticky="ew")

    def _setup_emprunteur_selection_page(self, commands):
        """Configure la page de sélection de l'objet pour l'emprunteur."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["emprunteur_selection"] = page
        page.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        page.grid_columnconfigure((0, 1, 2), weight=1)

        selection_frame = customtkinter.CTkFrame(page, corner_radius=10)
        selection_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        selection_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        selection_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(selection_frame, text="Sélectionnez l'objet à emprunter",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

       
        search_frame = customtkinter.CTkFrame(selection_frame)
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        search_frame.grid_columnconfigure((0, 1), weight=1)

        self.emprunteur_search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Rechercher un objet...")
        self.emprunteur_search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.emprunteur_search_entry.bind("<KeyRelease>", lambda event: self._update_emprunteur_listbox())

        
        contexte_options = ["Tous les objets", "Disponibles", "Empruntés"]  
        self.emprunteur_selected_contexte = customtkinter.StringVar(value="Tous les objets")  
        contexte_menu = customtkinter.CTkOptionMenu(search_frame, variable=self.emprunteur_selected_contexte,
                                                    values=contexte_options,
                                                    command=lambda choice: self._update_emprunteur_listbox())
        contexte_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Liste des objets disponibles
        self.emprunteur_listbox = customtkinter.CTkScrollableFrame(selection_frame, height=200)
        self.emprunteur_listbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.emprunteur_listbox.grid_columnconfigure(0, weight=1)

        # Bouton Retour
        customtkinter.CTkButton(page, text="Retour",
                                command=commands["retour_users_choix"],
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=2, column=1, padx=20,
                                                                                          pady=10, sticky="ew")



    def _update_emprunteur_listbox(self):
        """Met à jour la liste des objets disponibles pour l'emprunteur en fonction de la recherche et du filtre."""
        # Vide la liste existante
        for widget in self.emprunteur_listbox.winfo_children():
            widget.destroy()

        search_term = self.emprunteur_search_entry.get().lower()
        selected_status_filter = self.emprunteur_selected_contexte.get()  # Renommé pour plus de clarté

        
        objets = db_manager.get_all_materiel()

        filtered_objets = []
        for obj in objets:
            # bug du au fait que je n'avais pas fait appel a la cle statut
            obj_status = obj.get("statut", "N/A")
            # Filtrer par statut de disponibilité (Disponibles, Empruntés, Tous)
            if selected_status_filter == "Disponibles" and obj_status != "Disponible":
                continue
            if selected_status_filter == "Empruntés" and obj_status != "Emprunté":
                continue
           
            if search_term and \
                    search_term not in obj.get("nom_objet", "").lower() and \
                    search_term not in obj.get("proprietaire_nom", "").lower():
                continue

            filtered_objets.append(obj)

        if not filtered_objets:
            customtkinter.CTkLabel(self.emprunteur_listbox, text="Aucun objet trouvé avec ces critères.").pack(
                pady=5)
            return

        for obj in filtered_objets:
            obj_frame = customtkinter.CTkFrame(self.emprunteur_listbox, fg_color="transparent")
            obj_frame.pack(fill="x", padx=5, pady=2)
            obj_frame.grid_columnconfigure((0, 1), weight=1)

            obj_id = obj.get("id")
            nom_objet = obj.get("nom_objet", "N/A")
            proprietaire = obj.get("proprietaire_nom", "N/A")
            disponibilite = obj.get("statut", "N/A")  

            customtkinter.CTkLabel(obj_frame, text=f"Objet: {nom_objet}",
                                   font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5)
            customtkinter.CTkLabel(obj_frame, text=f"Propriétaire: {proprietaire}").grid(row=1, column=0, sticky="w",
                                                                                         padx=5)
            customtkinter.CTkLabel(obj_frame, text=f"Statut: {disponibilite}",
                                   text_color=("green" if disponibilite == "Disponible" else "orange")).grid(row=2,
                                                                                                             column=0,
                                                                                                             sticky="w",
                                                                                                             padx=5)  # Ajout de couleur

           
            if disponibilite == "Disponible":
                select_button = customtkinter.CTkButton(obj_frame, text="Sélectionner",
                                                        command=lambda item_id=obj_id: self.commands_ref[
                                                            "select_emprunteur_item"](item_id),
                                                        fg_color=self.COULEUR_BOUTON, hover_color="#4F8BBF")
            else:
                select_button = customtkinter.CTkButton(obj_frame, text="Indisponible", state="disabled",
                                                        fg_color="gray",
                                                        hover_color="gray")  
            select_button.grid(row=1, column=1, rowspan=2, padx=5, sticky="e")

    def _setup_formulaire_emprunteur_details_page(self, commands):
        """Configure la page de détails et de soumission pour l'emprunteur."""
        page = customtkinter.CTkFrame(self.master)
        self.pages["form_emprunteur_details"] = page
        page.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        page.grid_columnconfigure((0, 1, 2), weight=1)

        details_frame = customtkinter.CTkFrame(page, corner_radius=10)
        details_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        details_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(details_frame, text="Détails Emprunteur & Demande", 
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0,
                                                                                        columnspan=2, pady=10)

        
        self.emprunteur_objet_details_text = customtkinter.CTkTextbox(details_frame, height=120,
                                                                      wrap="word")  
        self.emprunteur_objet_details_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.emprunteur_objet_details_text.insert("0.0", "Détails de l'objet: (Sélectionnez un objet d'abord)")
        self.emprunteur_objet_details_text.configure(state="disabled") 

        customtkinter.CTkLabel(details_frame, text="Votre Nom:", anchor="w").grid(row=2, column=0, padx=10, pady=5,
                                                                                  sticky="ew")
        self.emprunteur_nom_entry = customtkinter.CTkEntry(details_frame, placeholder_text="Votre nom")
        self.emprunteur_nom_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(details_frame, text="Votre Numéro:", anchor="w").grid(row=3, column=0, padx=10,
                                                                                     pady=5, sticky="ew")
        self.emprunteur_num_entry = customtkinter.CTkEntry(details_frame,
                                                           placeholder_text="Votre numéro de téléphone")
        self.emprunteur_num_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(details_frame, text="Votre Mail:", anchor="w").grid(row=4, column=0, padx=10, pady=5,
                                                                                   sticky="ew")
        self.emprunteur_mail_entry = customtkinter.CTkEntry(details_frame, placeholder_text="Votre adresse email")
        self.emprunteur_mail_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkLabel(details_frame, text="Raison de l'emprunt:", anchor="w").grid(row=5, column=0,
                                                                                            padx=10, pady=5,
                                                                                            sticky="ew")
        self.emprunteur_raison_text = customtkinter.CTkTextbox(details_frame, height=80, wrap="word")
        self.emprunteur_raison_text.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        customtkinter.CTkButton(details_frame, text="Soumettre Demande",

                                command=self._submit_emprunteur_request,
                                fg_color=self.COULEUR_VALIDATION, hover_color="#8BD4AF").grid(row=6, column=0,
                                                                                              padx=10, pady=10,
                                                                                              sticky="ew")

        customtkinter.CTkButton(details_frame, text="Retour",
                                command=commands["retour_emprunteur_selection"],
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=6, column=1, padx=10,
                                                                                          pady=10, sticky="ew")



    def get_form_data(self, form_type):
        """Récupère les données des formulaires spécifiés."""
        if form_type == "preteur":
            return {
                "nom": self.preteur_nom_entry.get(),
                "numero": self.preteur_num_entry.get(),
                "mail": self.preteur_mail_entry.get(),
                "materiel": self.preteur_objet_entry.get(),
                "etat_materiel": self.preteur_etat_materiel_optionmenu.get(), 
                "contexte": self.preteur_contexte_optionmenu.get(), 
                "images": module_utilisateur.photos_selectionnees_temp.copy()
            }
        elif form_type == "emprunteur":
            ret_data= {
                "nom": self.emprunteur_nom_entry.get() .strip(),
                "numero": self.emprunteur_num_entry.get() .strip(),
                "mail": self.emprunteur_mail_entry.get() .strip(),
                "objet_id": self.emprunteur_selected_object_id ,
                "nom_materiel_demande": self.selected_materiel_nom ,
                "raison": self.emprunteur_raison_text.get("1.0", "end-1c").strip()
            }
        print(f"DEBUG_GET_FORM_DATA: Valeurs retournées par get_form_data (emprunteur): {ret_data}")
        return ret_data

    def clear_form_data(self, form_type):
        print(f"DEBUG_CLEAR_FORM: clear_form_data appelée pour type: {form_type}")
        """Vide les champs du formulaire spécifié."""
        if form_type == "preteur":
            self.preteur_nom_entry.delete(0, customtkinter.END)
            self.preteur_num_entry.delete(0, customtkinter.END)
            self.preteur_mail_entry.delete(0, customtkinter.END)
            self.preteur_objet_entry.delete(0, customtkinter.END)
            self.preteur_etat_materiel_optionmenu.set("Bon")  
            self.preteur_contexte_optionmenu.set("Autre")  
            module_utilisateur.reset_photos_selectionnees()
            if self.preteur_label_img:
                self.preteur_label_img.configure(text="Aucune image", image=None)
        elif form_type == "emprunteur":
            if self.emprunteur_nom_entry:
                self.emprunteur_nom_entry.delete(0, customtkinter.END)
            if self.emprunteur_num_entry:
                self.emprunteur_num_entry.delete(0, customtkinter.END)
            if self.emprunteur_mail_entry:
                self.emprunteur_mail_entry.delete(0, customtkinter.END)
            if self.emprunteur_raison_text:
                self.emprunteur_raison_text.delete("1.0", customtkinter.END)

            print(f"DEBUG_CLEAR_FORM: self.emprunteur_selected_object_id APRÈS clear_form_data: {self.emprunteur_selected_object_id}")
            if self.emprunteur_objet_details_text:
                self.emprunteur_objet_details_text.configure(state="normal")
                self.emprunteur_objet_details_text.delete("1.0", customtkinter.END)
                self.emprunteur_objet_details_text.insert("0.0", "Détails de l'objet: (Sélectionnez un objet d'abord)")
                self.emprunteur_objet_details_text.configure(state="disabled")
        print(f"DEBUG_CLEAR_FORM: Fin clear_form_data pour {form_type}.")
   
    def create_historique_admin_page(self):
        print("DEBUG_CREATE_PAGE: create_historique_admin_page function entered.")
        page_name ="admin_historique_page"

        if page_name in self.pages and self.pages[page_name].winfo_exists():
            print(f"DEBUG_CREATE_PAGE: Page '{page_name}' already exists. Refreshing and displaying.")


            self.refresh_historique_data(self.pages[page_name].history_frame, page_name)
            self.afficher_page(page_name)

            return
        print(f"DEBUG_CREATE_PAGE: Page '{page_name}' does not exist or window is gone. Creating new page.")

        historique_page = customtkinter.CTkFrame(self.master)
        historique_page.grid_columnconfigure(0, weight=1)  

        customtkinter.CTkLabel(historique_page, text="Historique Complet",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10, sticky="n")

        history_frame = customtkinter.CTkScrollableFrame(historique_page, width=850, height=550)
        history_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        history_frame.grid_columnconfigure(0, weight=1)
        historique_page.history_frame = history_frame
        self.refresh_historique_data(history_frame, page_name)
        print("DEBUG_BOUTON_RETOUR: Attempting to create 'Retour au tableau de bord Admin' button.")
        customtkinter.CTkButton(historique_page, text="Retour au tableau de bord Admin",
                                command=lambda: self.afficher_page("admin_dashboard"),
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=2, column=0, pady=10, sticky="s")
        print("DEBUG_BOUTON_RETOUR: 'Retour au tableau de bord Admin' button created and packed.")
        print(f"DEBUG_CREATE_PAGE: Page '{page_name}' created and added to self.pages.")
        self.pages[page_name] = historique_page
        self.afficher_page(page_name)
        print(f"DEBUG_CREATE_PAGE: display_page called for '{page_name}'.")

        


    def _handle_object_returned(self, emprunteur_id, materiel_id, current_page_name):
        """Gère le marquage d'un objet comme retourné et rafraîchit la page d'historique."""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment marquer cet objet comme retourné ?"):
            try:
                db_manager.mark_object_returned(emprunteur_id, materiel_id)
                messagebox.showinfo("Succès", "Objet marqué comme retourné et sa disponibilité mise à jour.")

                
                if current_page_name == "admin_historique_page" and current_page_name in self.pages:
                    
                    self.refresh_historique_data(self.pages[current_page_name].history_frame, current_page_name)

                self._update_emprunteur_listbox()  
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'opération: {e}")

    def create_approbation_admin_page(self, commands):
        """
        Crée et affiche la page d'approbation des demandes pour l'administrateur.
        Ceci remplace l'ancienne fenêtre CTkToplevel par une page CTkFrame.
        """
        page_name = "admin_approbation_page"
        print(f"DEBUG_CREATE_PAGE: Entrée dans create_approbation_admin_page pour '{page_name}'.")

        
        if page_name in self.pages and self.pages[page_name].winfo_exists():
            print(f"DEBUG_CREATE_PAGE: La page '{page_name}' existe déjà. Rafraîchissement et affichage.")
            self.refresh_approbation_data(self.pages[page_name].demandes_frame) 
            self.afficher_page(page_name)  
            return

        print(f"DEBUG_CREATE_PAGE: La page '{page_name}' n'existe pas. Création de la nouvelle page.")
        approbation_page = customtkinter.CTkFrame(self.master)

        
        approbation_page.grid_rowconfigure(0, weight=0) 
        approbation_page.grid_rowconfigure(1, weight=1) 
        approbation_page.grid_rowconfigure(2, weight=0)  
        approbation_page.grid_columnconfigure(0, weight=1) 

        
        customtkinter.CTkLabel(approbation_page, text="Demandes en Attente d'Approbation",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10,
                                                                                        sticky="n")

        
        demandes_frame = customtkinter.CTkScrollableFrame(approbation_page, width=700, height=400)
        demandes_frame.grid(row=1, column=0, pady=10, padx=20,
                            sticky="nsew") 
        demandes_frame.grid_columnconfigure(0, weight=1)  

       
        approbation_page.demandes_frame = demandes_frame

        # Appel initial pour peupler le cadre défilant avec les demandes en attente
        # refresh_approbation_data est maintenant une méthode de AppUI
        self.refresh_approbation_data(demandes_frame)

        # Bouton de retour - utilisation de grid
        customtkinter.CTkButton(approbation_page, text="Retour au tableau de bord Admin",
                                command=lambda: self.afficher_page("admin_dashboard"),
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").grid(row=2, column=0, pady=10,
                                                                                          sticky="s")

        # Ajouter la page nouvellement créée au dictionnaire des pages et l'afficher
        print(f"DEBUG_CREATE_PAGE: Page '{page_name}' créée et ajoutée à self.pages.")
        self.pages[page_name] = approbation_page
        self.afficher_page(page_name)  # Ceci masquera la page précédente et affichera celle-ci
        print(f"DEBUG_CREATE_PAGE: display_page appelée pour '{page_name}'.")

    def create_changement_mdp_admin_page(self):
        """
        Crée et affiche la page de changement de mot de passe admin.
        Ceci remplace l'ancienne fenêtre CTkToplevel.
        """
        page_name = "admin_changement_mdp_page"
        print(f"DEBUG_CREATE_PAGE: Entrée dans create_changement_mdp_admin_page pour '{page_name}'.")

        # Si la page existe déjà, on l'affiche simplement
        if page_name in self.pages and self.pages[page_name].winfo_exists():
            print(f"DEBUG_CREATE_PAGE: La page '{page_name}' existe déjà. Affichage.")
            self.afficher_page(page_name)

            if hasattr(self.pages[page_name], 'old_pass_entry'):
                self.pages[page_name].old_pass_entry.delete(0, customtkinter.END)
                self.pages[page_name].new_pass_entry.delete(0, customtkinter.END)
                self.pages[page_name].confirm_pass_entry.delete(0, customtkinter.END)
            return

        #
        print(f"DEBUG_CREATE_PAGE: La page '{page_name}' n'existe pas. Création de la nouvelle page.")

        changement_mdp_page = customtkinter.CTkFrame(self.master)


        customtkinter.CTkLabel(changement_mdp_page, text="Changer le Mot de Passe Admin",
                               font=customtkinter.CTkFont(size=18, weight="bold")).pack(pady=10)

        old_pass_entry = customtkinter.CTkEntry(changement_mdp_page, placeholder_text="Ancien mot de passe", show="*")
        old_pass_entry.pack(pady=5, padx=20, fill="x")

        new_pass_entry = customtkinter.CTkEntry(changement_mdp_page, placeholder_text="Nouveau mot de passe", show="*")
        new_pass_entry.pack(pady=5, padx=20, fill="x")

        confirm_pass_entry = customtkinter.CTkEntry(changement_mdp_page,
                                                    placeholder_text="Confirmer nouveau mot de passe", show="*")
        confirm_pass_entry.pack(pady=5, padx=20, fill="x")


        changement_mdp_page.old_pass_entry = old_pass_entry
        changement_mdp_page.new_pass_entry = new_pass_entry
        changement_mdp_page.confirm_pass_entry = confirm_pass_entry


        customtkinter.CTkButton(changement_mdp_page, text="Changer",
                                command=lambda: admin_logic.valider_changement_mdp_admin(
                                    old_pass_entry.get(),
                                    new_pass_entry.get(),
                                    confirm_pass_entry.get(),

                                    changement_mdp_page
                                ),
                                fg_color=self.COULEUR_VALIDATION, hover_color="#8BD4AF").pack(pady=10)

        #
        customtkinter.CTkButton(changement_mdp_page, text="Retour au tableau de bord Admin",
                                command=lambda: self.afficher_page("admin_dashboard"),
                                fg_color=self.COULEUR_RETOUR, hover_color="#CC3300").pack(pady=5)

        print(f"DEBUG_CREATE_PAGE: Page '{page_name}' créée et ajoutée à self.pages.")
        self.pages[page_name] = changement_mdp_page
        self.afficher_page(page_name)  
        print(f"DEBUG_CREATE_PAGE: display_page called for '{page_name}'.")



    def update_emprunteur_details_page(self, object_id):
        print(f"DEBUG_UPDATE_DETAILS: update_emprunteur_details_page appelée avec object_id: {object_id}")
        """
        Met à jour les détails de l'objet sur la page de soumission de demande d'emprunt.
        Appelé après qu'un objet a été sélectionné dans la liste des objets disponibles.
        """

        object_details = db_manager.get_object_details_by_id(object_id)
        if object_details:
            details_text = (
                f"Nom de l'objet: {object_details.get('nom_objet', 'N/A')}\n"
                f"État: {object_details.get('etat', 'N/A')}\n"
                f"Disponibilité: {object_details.get('disponibilite', 'N/A')}\n"
                f"Propriétaire: {object_details.get('proprietaire_nom', 'N/A')}\n"
                f"Contact Propriétaire: {object_details.get('mail_proprietaire', 'N/A')} / {object_details.get('proprietaire_numero', 'N/A')}\n"
                f"Catégorie: {object_details.get('categorie', 'N/A')}"
            )

            
            if self.emprunteur_objet_details_text:
                self.emprunteur_objet_details_text.configure(state="normal")
                self.emprunteur_objet_details_text.delete("1.0", customtkinter.END)
                self.emprunteur_objet_details_text.insert("0.0", details_text)
                self.emprunteur_objet_details_text.configure(state="disabled")
            else:
                # Debugging: S'il n'est pas initialisé, affiche un message d'erreur
                print(
                    "ERREUR: self.emprunteur_objet_details_text n'est pas initialisé dans update_emprunteur_details_page.")
                messagebox.showerror("Erreur UI", "Le champ d'affichage des détails de l'objet est manquant.")

        else:
            
            if self.emprunteur_objet_details_text:
                self.emprunteur_objet_details_text.configure(state="normal")
                self.emprunteur_objet_details_text.delete("1.0", customtkinter.END)
                self.emprunteur_objet_details_text.insert("0.0", "Détails de l'objet introuvables.")
                self.emprunteur_objet_details_text.configure(state="disabled")
            messagebox.showerror("Erreur", "Détails de l'objet non disponibles pour l'affichage.")


        self.afficher_page("form_emprunteur_details")  
        print(f"DEBUG_UPDATE_DETAILS: Page form_emprunteur_details affichée.")

    def refresh_historique_data(self, frame, page_name):
        """
        Rafraîchit le contenu du cadre d'historique de l'administrateur.
        Ceci est une méthode de la classe AppUI.
        'frame' est le CTkScrollableFrame où les enregistrements sont affichés.
        'page_name' est le nom de la page pour le rafraîchissement après une action.
        """
        for widget in frame.winfo_children():
            widget.destroy()  # Vide le contenu actuel du scrollable frame

        historique_data = db_manager.get_historique_prets()  # Récupère les données à jour

        if not historique_data:
            customtkinter.CTkLabel(frame, text="Aucun historique disponible.").pack(pady=20)
        else:
            for i, record in enumerate(historique_data):
                frame_record = customtkinter.CTkFrame(frame,
                                                      fg_color="transparent")  # Cadre transparent pour chaque enregistrement
                frame_record.pack(fill="x", pady=5, padx=5)
                frame_record.grid_columnconfigure((0, 1), weight=1) 

                # Informations de l'enregistrement (utiliser les clés normalisées de db_manager.get_historique_prets())
                type_rec = record.get('type_enregistrement', 'N/A')
                nom_objet = record.get('nom_objet', 'N/A')
                proprietaire = record.get('proprietaire_nom', 'N/A')
                emprunteur = record.get('emprunteur_nom', 'N/A')
                date_demande_soumission = record.get('date_demande_soumission', 'N/A')
                date_emprunt_effective = record.get('date_emprunt_effective', 'N/A')
                date_retour_prevue = record.get('date_retour_prevue', 'N/A')
                date_retour_reelle = record.get('date_retour_reelle', 'N/A')
                statut_demande = record.get('statut_demande', 'N/A')
                statut_objet = record.get('statut_objet', 'N/A')
                raison_emprunt = record.get('raison_emprunt', 'N/A')

                
                customtkinter.CTkLabel(frame_record, text=f"Type: {type_rec}",
                                       font=customtkinter.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w",
                                                                                       padx=5, columnspan=2)
                customtkinter.CTkLabel(frame_record, text=f"Objet: {nom_objet}").grid(row=1, column=0, sticky="w",
                                                                                      padx=5)
                customtkinter.CTkLabel(frame_record, text=f"Propriétaire: {proprietaire}").grid(row=2, column=0,
                                                                                                sticky="w", padx=5)

                if type_rec == 'Demande Emprunt Traitée':
                    customtkinter.CTkLabel(frame_record, text=f"Emprunteur: {emprunteur}").grid(row=3, column=0,
                                                                                                sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record, text=f"Demande soumise: {date_demande_soumission}").grid(
                        row=4, column=0, sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record,
                                           text=f"Emprunt Effectif: {date_emprunt_effective if date_emprunt_effective else 'N/A'}").grid(
                        row=5, column=0, sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record,
                                           text=f"Retour Prévu: {date_retour_prevue if date_retour_prevue else 'N/A'}").grid(
                        row=6, column=0, sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record,
                                           text=f"Retour Réel: {date_retour_reelle if date_retour_reelle else 'N/A'}").grid(
                        row=7, column=0, sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record, text=f"Statut Demande: {statut_demande}", text_color=(
                        "green" if statut_demande == "Approuvé" else "red" if statut_demande == "Refusé" else "orange")).grid(
                        row=8, column=0, sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record, text=f"Raison: {raison_emprunt[:70]}...").grid(row=9,
                                                                                                        column=0,
                                                                                                        sticky="w",
                                                                                                        padx=5)

                    
                    if statut_demande == "Approuvé" and not date_retour_reelle:
                        
                        try:
                            materiel_id = db_manager.get_materiel_id_from_emprunteur_request(record['id'])
                        except AttributeError:
                            print(
                                "ERREUR: db_manager.get_materiel_id_from_emprunteur_request n'est pas défini. Assurez-vous de l'ajouter à db_manager.py")
                            materiel_id = None  # Empêche l'affichage du bouton si la fonction manque

                        if materiel_id:
                            customtkinter.CTkButton(frame_record, text="Marquer comme retourné",
                                                    command=lambda emp_id=record['id'],
                                                                   mat_id=materiel_id: self._handle_object_returned(
                                                        emp_id, mat_id, page_name),
                                                    
                                                    fg_color=self.COULEUR_VALIDATION, hover_color="#8BD4AF").grid(
                                row=8, column=1, padx=5, sticky="e")
                elif type_rec == 'Proposition Matériel Approuvée':
                    
                    customtkinter.CTkLabel(frame_record, text=f"Statut Objet: {statut_objet}",
                                           text_color=("green" if statut_objet == "Disponible" else "orange")).grid(
                        row=3, column=0, sticky="w", padx=5)
                    customtkinter.CTkLabel(frame_record,
                                           text=f"Date Proposition: {record.get('date_proposition', 'N/A')}").grid(
                        row=4, column=0, sticky="w", padx=5)

    def refresh_approbation_data(self, frame): 
        """
        Rafraîchit le contenu du cadre d'approbation des demandes.
        'frame' est le CTkScrollableFrame où les demandes sont affichées.
        """
        print("DEBUG_REFRESH_APPROBATION: Rafraîchissement des données d'approbation.")
        for widget in frame.winfo_children():
            widget.destroy()  # Vider le contenu actuel

        demandes = db_manager.get_pending_demandes()  # Récupérer les demandes à jour

        if not demandes:
            customtkinter.CTkLabel(frame, text="Aucune demande en attente d'approbation.").pack(pady=20)
        else:
            for i, demande in enumerate(demandes):
                demande_id = demande.get("id")
                demande_type = demande.get("type")

                frame_demande = customtkinter.CTkFrame(frame, fg_color="transparent")
                frame_demande.pack(fill="x", pady=5,
                                   padx=5)  
                frame_demande.grid_columnconfigure(0, weight=3)
                frame_demande.grid_columnconfigure(1, weight=1)

                info_text = (
                    f"Type: {demande_type.capitalize()}\n"
                    f"Demandeur: {demande.get('nom_demandeur', 'N/A')}\n"
                    f"Objet: {demande.get('nom_objet_demande', 'N/A')}\n"
                    f"Raison: {demande.get('raison_demande', 'N/A')}\n"
                    f"Date: {demande.get('date_demande', 'N/A')}\n"
                    f"Statut: {demande.get('statut', 'N/A')}"
                )
                customtkinter.CTkLabel(frame_demande, text=info_text, justify="left").grid(row=0, column=0, padx=10,
                                                                                           pady=5, sticky="w")

                button_frame = customtkinter.CTkFrame(frame_demande, fg_color="transparent")
                button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
                button_frame.grid_rowconfigure((0, 1), weight=1)
                button_frame.grid_columnconfigure(0, weight=1)

                
                customtkinter.CTkButton(button_frame, text="Approuver",
                                        command=lambda did=demande_id, dtype=demande_type:
                                        admin_logic.approuver_demande_admin(did, dtype,
                                                                            lambda: self.refresh_approbation_data(
                                                                                frame)),
                                        fg_color=self.COULEUR_VALIDATION, hover_color="#8BD4AF").grid(row=0,
                                                                                                      column=0,
                                                                                                      pady=5,
                                                                                                      sticky="ew")

    def select_emprunteur_item(self, materiel_id):
        """
        Gère la sélection d'un matériel pour une demande d'emprunt.
        Stocke l'ID et le nom du matériel, met à jour les détails sur la page de demande,
        et navigue vers cette page.
        """
        print(f"DEBUG_SELECT_ITEM: select_emprunteur_item appelée avec materiel_id: {materiel_id}")
        self.emprunteur_selected_object_id = materiel_id # Stocke l'ID
        print(f"DEBUG_SELECT_ITEM: self.emprunteur_selected_object_id DANS select_emprunteur_item: {self.emprunteur_selected_object_id}")
        materiel_details = db_manager.get_object_details_by_id(materiel_id)
        if materiel_details:
            self.selected_materiel_nom = materiel_details['nom_objet']  # Stocke le nom
            print(
                f"DEBUG_SELECT_ITEM: self.selected_materiel_nom DANS select_emprunteur_item: {self.selected_materiel_nom}")

            # Mettre à jour la page de détails avec les informations de l'objet
            # Cette fonction va aussi afficher la page "form_emprunteur_details"
            self.update_emprunteur_details_page(materiel_id)

            # Vider les champs d'entrée de l'emprunteur pour la nouvelle demande
            self.clear_form_data("emprunteur")

        else:
            print("DEBUG_SELECT_ITEM: Materiel details not found.")
            messagebox.showerror("Erreur", "Matériel sélectionné introuvable.")
            self.emprunteur_selected_object_id = None  # Réinitialiser au cas où
            self.selected_materiel_nom = None
        print(f"DEBUG_SELECT_ITEM: Fin de select_emprunteur_item. Final ID: {self.emprunteur_selected_object_id}, Final Nom: {self.selected_materiel_nom}")

    def _submit_emprunteur_request(self):
        print("DEBUG_SUBMIT_REQUEST: _submit_emprunteur_request appelée.")

        """
        Collecte les données du formulaire de demande d'emprunt, effectue une validation de base,
        et appelle la commande externe pour enregistrer la demande de prêt.
        """
        form_data = self.get_form_data("emprunteur")  # Utilise la méthode existante pour récupérer les données
        print(f"DEBUG_SUBMIT_REQUEST: form_data reçu pour validation: {form_data}")

        # Validation de base
        if not all([form_data.get("nom"), form_data.get("numero"),
                    form_data.get("mail"), form_data.get("raison"),
                    form_data.get("objet_id")]):
            print("DEBUG_SUBMIT_REQUEST: Erreur: Champs de texte manquants.")
            messagebox.showerror("Erreur de validation", "Veuillez remplir tous les champs et sélectionner un objet.")
            return

        # Appel de la commande externe définie dans main.py
        # Passe les données collectées et les fonctions de rappel (callbacks)
        if form_data.get("objet_id") is None:
            print("DEBUG_SUBMIT_REQUEST: Erreur: objet_id est None.")
            messagebox.showerror("Erreur de validation",
                                 "Veuillez sélectionner un objet avant de soumettre la demande.")
            return

        if form_data.get("nom_materiel_demande") is None:
            print("DEBUG_SUBMIT_REQUEST: Erreur: nom_materiel_demande est None.")
            messagebox.showerror("Erreur de validation", "Le nom du matériel sélectionné est manquant.")
            return

        print("DEBUG_SUBMIT_REQUEST: Validation des champs passée.")

            # Appel de la commande externe définie dans main.py
        result=self.commands_ref["valider_emprunteur_form"](
            form_data,
            self._on_demande_emprunt_success,
            self._on_demande_emprunt_error
        )
        if result:  # Si enregistrer_demande_emprunteur retourne True
            self.clear_form_data("emprunteur")
            self.afficher_page("accueil")  # Ou la page de confirmation souhaitée

    def _on_demande_emprunt_success(self, msg):
        """Callback pour une soumission de demande de prêt réussie."""
        messagebox.showinfo("Succès", msg)
        # Réinitialise les données du matériel sélectionné dans l'instance de l'UI
        self.selected_materiel_id = None
        self.selected_materiel_nom = None
        # Efface les champs du formulaire et l'affichage des détails de l'objet
        self.clear_form_data("emprunteur")
        if self.emprunteur_objet_details_text:
            self.emprunteur_objet_details_text.configure(state="normal")
            self.emprunteur_objet_details_text.delete("1.0", customtkinter.END)
            self.emprunteur_objet_details_text.insert("0.0", "Détails de l'objet: (Sélectionnez un objet d'abord)")
            self.emprunteur_objet_details_text.configure(state="disabled")

        
        self.afficher_page("emprunteur_selection")

    def _on_demande_emprunt_error(self, msg):
        """Callback pour une soumission de demande de prêt échouée."""
        messagebox.showerror("Erreur", f"Échec de la soumission: {msg}")
