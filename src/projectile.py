"""
ce module contient la classe Projectile qui représente un projectile,
 le projectile garde seulement son état et son historique 

"""
import numpy as np

from src.astre import Astre
from src.exceptions import DebutHistorique, FinHistorique


class Projectile(Astre):
    def __init__(self,nom, masse, couleur, taille, rayon,pos0,
                  vit0,temps_apparition, duree_vie, actif=True):
        """_summary_

        Args:
            nom (_type_): _description_
            masse (_type_): _description_
            couleur (_type_): _description_
            taille (_type_): _description_
            rayon (_type_): _description_
            pos0 (_type_): _description_
            vit0 (_type_): _description_
            temps_apparition (_type_): _description_
            duree_vie (_type_): _description_
            actif (bool, optional): _description_. Defaults to True.
        """        

        super().__init__(nom, masse, couleur, taille, rayon, actif)
        self.pos0 = np.array(pos0, dtype=float)  # Position initiale du projectile, liste de coordonnées [x, y]
        self.vit0 = np.array(vit0, dtype=float)  # Vitesse initiale du projectile, liste de coordonnées [vx, vy]
        self.temps_apparition = temps_apparition  # Temps d'apparition du projectile : question a poser...
        self.duree_vie = duree_vie  # Durée de vie du projectile: question a poser...

        self.historique = np.array([[*self.pos0, *self.vit0]]) # Liste pour stocker l'historique des positions du projectile : unpacking de pos0 et vit0 pour créer un tableau 2D avec les coordonnées et vitesses initiales par rappre a un N
        self.etat = "actif"   # État du projectile : peut être actif ou inactif, mais obligatoirement actifs sa création, question a poser...: Que faire si on réinitialise mais que il avait été désactivé par le gestionnaire d'objets ?
        self.cible = None  # Cible du projectile?: question a poser...

    def reinitialiser(self):
            """
             hypothèses: lors de la réinitialisation on recommence la simulation depuis 
             le début, donc je vais supprimer l'historique, remettre son état à l'état de base 
             et la cible (je sais toujours pas le ça à quoi) mais on va la réinitialiser 
             parce qu'elle peut changer, les autres paramètres ne peuvent pas changer,
             donc on n'a pas besoin de le réinitialiser 
            """

            self.historique = np.array([[*self.pos0, *self.vit0]])  # on oublie les pas calculés
            self.etat = "actif"  # Réinitialiser l'état à actif
            self.cible = None  # Réinitialiser la cible à None

    def ajouter_etat(self, pos, vit):
            """
            Ajoute un nouvel état du projectile à l'historique.
                Args:
                    position (list): Position actuelle du projectile [x, y].
                    vitesse (list): Vitesse actuelle du projectile [vx, vy].
                """

            nouvelle_ligne = np.array([[*pos, *vit]])  # Créer une nouvelle ligne avec la position et la vitesse
            self.historique = np.vstack((self.historique, nouvelle_ligne))  # Ajouter la ligne à l'historique

            """ 
                est ce que je dois mettre à jour l'état du projectile en fonction de la durée de vie?
                ou la simulation va gérer ça? je pense que c'est la simulation qui va gérer ça, 
                donc je ne vais pas le faire ici:C’est la Simulation qui compare le temps actuel à t_apparition  + duree_vie, 
                qui met etat = "expire" et qui arrête ensuite d’appeler ajouter_etat
                
                """

    def position(self, t):
        """
        Calcule la position du projectile à un instant donné t.

        Args:
            t (float): Temps de la simulation, en jours (1 pas = 1 journée)

        Returns:
            np.array: Position du projectile à l'instant t.
        """
        try:
            return self.etat_a(t)[:2]  # Retourne seulement les coordonnées x et y de l'état complet à l'instant t
        except DebutHistorique as e:
            raise DebutHistorique(str(e))
        except FinHistorique as e:
            raise FinHistorique(str(e))


    def etat_a(self, pas):
                """
                Retourne l'état complet du projectile à un pas donné de la simulation.

                Args:
                pas (int): Pas de la simulation (1 pas = 1 journée).

                Returns:
                np.ndarray: [x, y, vx, vy]. Retourne l'état au pas demandé
                Raises:
                    DebutHistorique: Si le pas est avant l'apparition du projectile.
                    FinHistorique: Si le pas dépasse les pas déjà calculés.        
                """
                if pas < self.temps_apparition:
                    raise DebutHistorique("Le projectile n'a pas encore été créé")  # Retourne l'état initial avant l'apparition
                
                ligne = int(pas - self.temps_apparition)  # Nombre de pas depuis l'apparition

                if ligne < len(self.historique):
                    return self.historique[ligne]  # Retourne ligne conplete
                raise FinHistorique("Le projectile ne s'est pas rendu là")  # Retourne le dernier état connu si le pas dépasse les pas calculés
