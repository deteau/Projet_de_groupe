#include <stdio.h>
#include <string.h>
#include "fonctions.h"

void chargerProduit(Produit stock[], int *nombreProduits) {
    FILE *f = fopen("stock.txt", "r");
    if (f == NULL) {
        printf("Aucun fichier trouve ou erreur d'ouverture du fichier.\n");
        return;
    }

    while (fscanf(f, "%d;%49[^;];%d\n", &stock[*nombreProduits].id, stock[*nombreProduits].nom, &stock[*nombreProduits].quantite) != EOF) 
    {
        (*nombreProduits)++;  // On incrémente la valeur pointée
        if (*nombreProduits >= MAX_PRODUITS) {
            printf("Stock plein, impossible de charger plus de produits.\n");
            break;
        }
    }

    fclose(f);
    printf("Produits charges depuis 'stock.txt'.\n");
}


void ajouterProduit(Produit stock[], int *nombreProduits) {
    if (*nombreProduits >= MAX_PRODUITS) {
        printf("Stock plein !\n");
        return;
    }
    Produit p;
    printf("Entrer l'ID du produit : ");
    scanf("%d", &p.id);
    printf("Entrer le nom du produit : ");
    scanf(" %[^\n]", p.nom);
    printf("Entrer la quantite : ");
    scanf("%d", &p.quantite);

    stock[*nombreProduits] = p;
    (*nombreProduits)++;
    printf("Produit ajoute avec succes.\n");
}

void afficherProduits(Produit stock[], int nombreProduits) {
    if (nombreProduits == 0) {
        printf("Aucun produit dans le stock.\n");
        return;
    }
    printf("\nListe des produits :\n");
    for (int i = 0; i < nombreProduits; i++) {
        printf("ID: %d | Nom: %s | Quantite: %d\n",
               stock[i].id, stock[i].nom, stock[i].quantite);
    }
}

void modifierProduit(Produit stock[], int nombreProduits) {
    int id, trouve = 0;
    printf("Entrer l'ID du produit a modifier : ");
    scanf("%d", &id);
    for (int i = 0; i < nombreProduits; i++) {
        if (stock[i].id == id) {
            printf("Entrer le nouveau nom : ");
            scanf(" %[^\n]", stock[i].nom);
            printf("Entrer la nouvelle quantite : ");
            scanf("%d", &stock[i].quantite);
            printf("Produit modifie.\n");
            trouve = 1;
            break;
        }
    }
    if (!trouve) {
        printf("Produit non trouve.\n");
    }
}

void supprimerProduit(Produit stock[], int *nombreProduits) {
    int id, trouve = 0;
    printf("Entrer l'ID du produit a supprimer : ");
    scanf("%d", &id);
    for (int i = 0; i < *nombreProduits; i++) {
        if (stock[i].id == id) {
            for (int j = i; j < *nombreProduits - 1; j++) {
                stock[j] = stock[j + 1];
            }
            (*nombreProduits)--;
            printf("Produit supprime.\n");
            trouve = 1;
            break;
        }
    }
    if (!trouve) {
        printf("Produit non trouve.\n");
    }
}

void rechercherProduit(Produit stock[], int nombreProduits) {
    int choix;
    printf("Rechercher par : 1.ID  2.Nom\n");
    scanf("%d", &choix);
    if (choix == 1) {
        int id, trouve = 0;
        printf("Entrer l'ID : ");
        scanf("%d", &id);
        for (int i = 0; i < nombreProduits; i++) {
            if (stock[i].id == id) {
                printf("ID: %d | Nom: %s | Quantite: %d\n",
                       stock[i].id, stock[i].nom, stock[i].quantite);
                trouve = 1;
                break;
            }
        }
        if (!trouve) printf("Produit non trouve.\n");
    } else if (choix == 2) {
        char nom[TAILLE_NOM];
        int trouve = 0;
        printf("Entrer le nom : ");
        scanf(" %[^\n]", nom);
        for (int i = 0; i < nombreProduits; i++) {
            if (strcmp(stock[i].nom, nom) == 0) {
                printf("ID: %d | Nom: %s | Quantite: %d\n",
                       stock[i].id, stock[i].nom, stock[i].quantite);
                trouve = 1;
            }
        }
        if (!trouve) printf("Produit non trouve.\n");
    } else {
        printf("Choix invalide.\n");
    }
}

void sauvegarderFichier(Produit stock[], int nombreProduits) {
    FILE *f = fopen("stock.txt", "w");
    if (!f) {
        printf("Erreur d'ouverture du fichier.\n");
        return;
    }
    for (int i = 0; i < nombreProduits; i++) {
        fprintf(f, "%d;%s;%d\n", stock[i].id, stock[i].nom, stock[i].quantite);
    }
    fclose(f);
    printf("Donnees sauvegardees dans stock.txt\n");
}
