if __name__ == "__main__":
    from src.graphique import FenetreSimulateur

    fenetre = FenetreSimulateur()
    fenetre.charger("donnees/systeme_solaire.csv")  # remplit aussi fenetre.simulateur
    fenetre.mainloop()
