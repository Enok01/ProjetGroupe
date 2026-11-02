from src.astre import AstreFixe
from src.chargeur_csv import charger_csv
from src.projectile import Projectile
from src.physique import calculer_trajectoire
from src.exceptions import *


class Simulation:
    """Contient la liste des astres et projectiles, et génère leurs trajectoires via physique_Kepler"""
    def __init__(self):
        self.astres: list[AstreFixe] = []
        self.projectiles: list[Projectile] = []
        self.dt = 0.1
        self.moments_cle: list[int] = []

    @property
    def astres_et_projectiles(self):
        return self.astres, self.projectiles

    def temps_max(self, padt=50):
        """
        :param padt: Ajoute un peu de temps après la disparition du dernier projectile.
        :return: Le temps maximal de la ligne du temps
        """
        t_max = 0
        if self.projectiles:
            for projectile in self.projectiles:
                temps_mort = projectile.temps_apparition + projectile.duree_vie
                if temps_mort > t_max:
                    t_max = temps_mort
        return t_max + padt

    def moment_cle_prochain(self, t: int, direction: str = "avancer") -> int:
        """
        Trouve le moment-clé qui suit ou précède le

        :param t: Le temps à relativiser
        :param direction: Soit "avancer" ou "reculer", décide quelle direction on souhaite regarder
        :return: L'indice de temps du moment-clé, ou t lui-même si l'indice est à l'extrémité de la ligne du temps.
        :exception ValueError: Si le temps fourni est négatif ou plus grand que le temps maximal de la simulation
                               OU Si la direction fournie est invalide.
        """
        if t < 0 or t > self.temps_max():
            raise ValueError("Le temps spécifié est hors des limites de la simulation.")

        print(self.moments_cle)
        if self.moments_cle[len(self.moments_cle) - 1] <= t <= self.temps_max():
            return self.temps_max()
        elif direction == "avancer":
            moments_pertinents = [mc for mc in self.moments_cle if mc > t]  # Trouve tous les mc qui sont après t
            if moments_pertinents:
                return moments_pertinents[0]  # Le premier mc plus grand que t est celui qui le suit
            else:
                return t
        elif direction == "reculer":
            moments_pertinents = [mc for mc in self.moments_cle if mc < t]  # Trouve tous les mc qui sont avant t
            if moments_pertinents:
                return moments_pertinents[-1]  # Le dernier mc plus petit que t est celui qui le précède
            else:
                return t
        else:
            raise ValueError

    def ajouter_moment_cle(self, t: int):
        if t >= self.temps_max():
            raise ValueError("Le temps spécifié est hors des limites de la simulation.\n"
                             + "temps_max = " + str(self.temps_max()) + "\n"
                             + "t = " + str(t))

        self.moments_cle.append(t)
        self.moments_cle.sort()

    def recalculer(self):
        for projectile in self.projectiles:
            if projectile.actif:
                try:
                    projectile.cible = calculer_trajectoire(projectile, self.astres, self.dt, self.temps_max())
                    if projectile.cible is not None:
                        projectile.etat = "expire"
                except TempsMaximumAtteinte:
                    projectile.etat = "expire"
                except HorsSystemeError:
                    print(f"Le projectile {projectile.nom} est sorti du système!"
                          f"Portez attention aux valeurs de vit0_x et vit0_y, elles sont en UA/jour.")
                    projectile.etat = "hors systeme"
                finally:
                    self.ajouter_moment_cle(len(projectile.historique[:, 0]) - 1)

    def importer(self, fichier):
        astres, projectiles = charger_csv(fichier)
        self.astres = astres.copy()
        self.projectiles = projectiles.copy()
