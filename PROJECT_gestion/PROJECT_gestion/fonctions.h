#ifndef FONCTION_H
#define FONCTION_H

#define MAX_PRODUITS 100
#define TAILLE_NOM 50

typedef struct {
    int id;
    char nom[TAILLE_NOM];
    int quantite;
} Produit;

// Déclarations des fonctions
void ajouterProduit(Produit stock[], int *nombreProduits);
void modifierProduit(Produit stock[], int nombreProduits);
void supprimerProduit(Produit stock[], int *nombreProduits);
void afficherProduits(Produit stock[], int nombreProduits);
void rechercherProduit(Produit stock[], int nombreProduits);
void sauvegarderFichier(Produit stock[], int nombreProduits);
void chargerProduit(Produit stock[], int *nombreProduits);

#endif
