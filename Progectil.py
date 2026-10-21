"""
ce module contient la classe Projectile qui représente un projectile,
 le projectile garde seulement son état et son historique 

"""
import numpy as np

from astre import Astre

class Projectile(Astre):
    def __init__(self,nom, masse, couleur, taille, rayon,pos0,
                  vit0,temps_apparition, duree_vie, actif=True):

        super().__init__(nom, masse, couleur, taille, rayon, actif)
        self.pos0 = np.array(pos0, dtype=float)  # Position initiale du projectile, liste de coordonnées [x, y]
        self.vit0 = np.array(vit0, dtype=float)  # Vitesse initiale du projectile, liste de coordonnées [vx, vy]
        self.temps_apparition = temps_apparition  # Temps d'apparition du projectile : question a poser...
        self.duree_vie = duree_vie  # Durée de vie du projectile: question a poser...

        self.historique = np.array([[*self.pos0, *self.vit0]]) # Liste pour stocker l'historique des positions du projectile : unpacking de pos0 et vit0 pour créer un tableau 2D avec les coordonnées et vitesses initiales par rappre a un N
        self.etat = "actif"   # État du projectile : peut être actif ou inactif, mais obligatoirement actifs sa création 
        self.cible = None  # Cible du projectile?: question a poser...

        
        

