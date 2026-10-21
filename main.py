import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class GraphiqueFrame(ctk.CTkFrame):
    """
    Le graphique.
    """
    def __init__(self, master, simulateur):
        super().__init__(master=master)
        self.simulateur = simulateur
        self.temps = 0 # TODO: remplacer par qqch qui fait plus de sens

        # Création des composantes MatPlotLib
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def redessiner(self) -> None:
        """
        Redessine le graphique. À appeler lorsqu'une variable change.
        """
        # Réinitialise l'axe
        self.ax.clear()

        # Repeupler le graphique
        # Affichage des astres
        for astre in self.simulateur.astres:
            if astre.actif:
                # Marqueur de position actuelle
                x, y = astre.position(self.temps)
                self.ax.scatter(x, y, astre.taille, astre.couleur)

        # Affichage des Projectiles
        for projectile in self.simulateur.projectiles:
            if projectile.etat == "actif":
                # Marqueur de position actuelle
                x, y = projectile.position(self.simulateur.temps())
                self.ax.scatter(x, y, projectile.taille, projectile.couleur)


        self.canvas.draw_idle()


    def afficher_libre(self):
        """
        Affiche le graphique directement via MatPlotLib. À utiliser seulement dans le bus de déboguer.
        """

        self.redessiner()
        self.fig.show()


class App(ctk.CTk):
    """
    La fenêtre principale du programme. Inclus le graphique et la ligne de temps.
    """

    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Simulation Projectile Cosmique")
        self.minsize(400, 300)
        self.resizable(True, True)

        self.graphique = GraphiqueFrame(master=self)
        self.graphique.grid(row=0, column=0)


if __name__ == "__main__":
    pass  # code d'éxec
