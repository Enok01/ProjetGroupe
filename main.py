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

        # Création des composantes MatPlotLib
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    @property
    def temps(self):
        return self.simulateur.temps()

    def redessiner(self) -> None:
        """
        Redessine le graphique. À appeler lorsqu'une variable change.
        """
        # Réinitialise l'axe
        self.ax.clear()
        self.ax.set_aspect("equal")

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
                x, y = projectile.position(self.temps)
                self.ax.scatter(x, y, projectile.taille, projectile.couleur)

        self.canvas.draw_idle()

    def afficher_libre(self):
        """
        Affiche le graphique directement via MatPlotLib. À utiliser seulement dans le bus de déboguer.
        """

        self.redessiner()
        self.fig.show()


class LigneDuTemps(ctk.CTkFrame):
    """
    Une ligne du temps avec un bouton arrêt, jouer/mettre sur pause, avancer au moment-clé prochain, retourner au
    moment-clé précédent.
    """

    def __init__(self, master: ctk.CTk, simulateur):
        super().__init__(master=master)
        self.simulateur = simulateur
        self.__taille_boutons = 10  # taille des boutons carrés

        # Création des widgets
        self.stop = ctk.CTkButton(
            master=self,
            text="\u23f9",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__cmd_stop
        )
        self.play_pause = ctk.CTkButton(
            master=self,
            text="\u23f5",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__cmd_play
        )
        self.fforward = ctk.CTkButton(
            master=self,
            text="\u23ed",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__cmd_fforward
        )
        self.back = ctk.CTkButton(
            master=self,
            text="\u23ee",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__cmd_back
        )
        self.slider = ctk.CTkSlider(
            master=self,
            height=self.__taille_boutons,
            from_=0,
            to=simulateur.temps_max(),
            command=self.__cmd_slider
        )
        self.stop.grid(row=0, column=0)
        self.play_pause.grid(row=0, column=1)
        self.fforward.grid(row=0, column=2)
        self.back.grid(row=0, column=3)

    def __cmd_stop(self):
        """Arrête le défilement du temps et revient à t=0."""
        pass

    def __cmd_play(self):
        """Fait défiler le temps."""
        self.play_pause.config(text="\u23f8", command=self.__cmd_pause)

    def __cmd_pause(self):
        """Met sur pause le défilement du temps."""
        self.play_pause.config(text="\u23f5", command=self.__cmd_play)

    def __cmd_fforward(self):
        """Avance jusqu'au prochain moment-clé."""
        pass

    def __cmd_back(self):
        """Retourne au moment-clé précédent."""
        pass

    def __cmd_slider(self, value):
        """Met à jour le temps lorsque le slider est utilisé"""
        pass


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

        self.graphique = GraphiqueFrame(master=self, simulateur=None)  # J'ai besoin de la classe de simu pour cet appel
        self.graphique.grid(row=0, column=0)
        self.ligne_du_temps = LigneDuTemps(master=self, simulateur=None)  # Idem


if __name__ == "__main__":
    pass  # code d'éxec
