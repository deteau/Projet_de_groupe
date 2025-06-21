#include <stdio.h>
#include "fonctions.h"

int main() {
    Produit stock[MAX_PRODUITS];
    int nombreProduits = 0;
    int choix;
    chargerProduit(stock, &nombreProduits);

    do {
        printf("\n===== SYSTEME DE GESTION DES STOCKS =====\n");
        printf("1. Ajouter un produit\n");
        printf("2. Modifier un produit\n");
        printf("3. Supprimer un produit\n");
        printf("4. Afficher les produits\n");
        printf("5. Rechercher un produit\n");
        printf("6. Sauvegarder dans un fichier\n");
        printf("0. Quitter\n");
        printf("Choisir une option : ");
        scanf("%d", &choix);

        switch (choix) {
            case 1: ajouterProduit(stock, &nombreProduits);
				break;
            case 2: modifierProduit(stock, nombreProduits); 
				break;
            case 3: supprimerProduit(stock, &nombreProduits); 
				break;
            case 4: afficherProduits(stock, nombreProduits); 
				break;
            case 5: rechercherProduit(stock, nombreProduits); 
				break;
            case 6: sauvegarderFichier(stock, nombreProduits); 
				break;
            case 0: printf("Fermeture du programme.\n"); 
				break;
            default: printf("Option invalide.\n");
        }

    } while (choix != 0);

    return 0;
}
