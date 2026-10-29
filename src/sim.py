from src.astre import AstreFixe
from src.projectile import Projectile
from src.physique import calculer_trajectoire


class Simulation:
    """Contient la liste des astres et projectiles, et génère leurs trajectoires via physique_Kepler"""
    def __init__(self):
        self.astres: list[AstreFixe] = []
        self.projectiles: list[Projectile] = []
        self.dt = 0.1

    def temps_max(self, padt=100):
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

    def recalculer(self):
        for projectile in self.projectiles:
            projectile.historique = calculer_trajectoire(projectile, self.astres, self.dt, self.temps_max())

    def importer(self, path: str):
        # TODO: Implémenter la méthode à Demba
        pass
