class Astre:
    #Constructeur de la classe Astre
    def __init__(self, nom, masse, couleur, taille, rayon, actif):
        self.nom = nom
        self.masse = masse
        self.couleur = couleur
        self.rayon = rayon
        self.actif = actif
    
    def __str__(self):
        return f"Astre(nom={self.nom}, masse={self.masse}, couleur={self.couleur}, taille={self.taille}, rayon={self.rayon}, actif={self.actif})"

    
