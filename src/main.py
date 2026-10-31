from __future__ import annotations

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from src.simulation import Simulation


class GraphiqueFrame(ctk.CTkFrame):
    """
    Le graphique.
    """

    def __init__(self, master: App, simulateur: Simulation):
        super().__init__(master=master)
        self.master: App = master # Je redéclare pour que l'EDI arrête de me donner des alertes de type
        self.simulateur: Simulation = simulateur

        # Création des composantes MatPlotLib
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    @property
    def temps(self):
        return self.master.temps

    def redessiner(self) -> None:
        """
        Redessine le graphique. À appeler lorsqu'une variable change.
        """
        # Réinitialise l'axe
        self.ax.clear()
        self.ax.set_aspect("equal")
        self.simulateur.recalculer()

        # --- Repeupler le graphique ---
        # Affichage des astres
        for astre in self.simulateur.astres:
            if astre.actif:
                # Marqueur de position actuelle
                x, y = astre.position(self.temps)
                self.ax.scatter(x, y, astre.taille, astre.couleur)

                # Trajectoire
                if astre.periode == 0.0:
                    # L'astre ne se déplace pas, il n'a donc pas de trajectoire.
                    continue
                trajectoire = np.array([astre.position(t) for t in range(int(astre.periode))])
                self.ax.plot(trajectoire[:,0], trajectoire[:,1], color=astre.couleur, marker="")

        # Affichage des Projectiles
        for projectile in self.simulateur.projectiles:
            if projectile.etat == "actif":
                # Marqueur de position actuelle
                x, y = projectile.position(self.temps)
                self.ax.scatter(x, y, projectile.taille, projectile.couleur)

                # Trajectoire
                traj_x = projectile.historique[:, 0]
                traj_y = projectile.historique[:, 1]
                self.ax.plot(traj_x, traj_y, color=projectile.couleur, marker="")

        self.canvas.draw_idle()


class LigneDuTemps(ctk.CTkFrame):
    """
    Une ligne du temps avec un bouton arrêt, jouer/mettre sur pause, avancer au moment-clé prochain, retourner au
    moment-clé précédent.
    """

    def __init__(self, master: App, simulateur: Simulation):
        super().__init__(master=master)
        self.master: App = master # Je redéclare pour que l'EDI arrête de me donner des alertes de type
        self.simulateur: Simulation = simulateur
        self.__taille_boutons = 10  # taille des boutons carrés
        self.__temps = 0
        self.__defil = False # dit sil y a un defilement dans le temps, ou non.
        
        # Création des boutons et de la ligne
        self.stop = ctk.CTkButton(
            master=self,
            text="\u23f9",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__commande_arret
        )
        self.play_pause = ctk.CTkButton(
            master=self,
            text="\u23f5",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__commande_lecture
        )
        self.fforward = ctk.CTkButton(
            master=self,
            text="\u23ed",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__commande_suivant
        )
        self.back = ctk.CTkButton(
            master=self,
            text="\u23ee",
            width=self.__taille_boutons, height=self.__taille_boutons,
            command=self.__commande_precedent
        )
        self.slider = ctk.CTkSlider(
            master=self,
            height=self.__taille_boutons,
            from_=0, to=simulateur.temps_max(),
            command=self.__commande_curseur
        )
        
        # Arranger les widgets
        self.stop.grid(row=0, column=0)
        self.back.grid(row=0, column=1)
        self.play_pause.grid(row=0, column=2)
        self.fforward.grid(row=0, column=3)
        self.slider.grid(row=0, column=4)
        
        self.slider.set(0) # inisialisation du slider (pour qu'il soit au t = 0 au moment du lancement de l'application )

    @property
    def temps(self):
        return self.__temps
    
    @property
    def defil(self):
        return self.__defil
    
    @temps.setter
    def temps(self, valeur):
        self.__temps = valeur
        self.master.graphique.redessiner()
        self.slider.set(valeur)
        
    @defil.setter
    def defil(self, value):
        self.__defil = value

    def __commande_arret(self):
        """Arrête le défilement du temps et revient à t=0."""
        self.temps = 0
        self.__commande_pause()

    def __commande_lecture(self):
        """Fait défiler le temps."""
        if not self.defil and self.temps < self.simulateur.temps_max():
            self.defil = True  
            self.mise_a_jour_lecture()
            self.play_pause.configure(text="\u23f8", command=self.__commande_pause)
        else:
            self.__commande_pause()

    def __commande_pause(self):
        """Met sur pause le défilement du temps."""
        self.defil = False
        self.play_pause.configure(text="\u23f5", command=self.__commande_lecture)

    def __commande_suivant(self):
        """Avance jusqu'au prochain moment-clé."""
        self.temps = self.simulateur.moment_cle_prochain(self.temps)

    def __commande_precedent(self):
        """Retourne au moment-clé précédent."""
        self.temps = self.simulateur.moment_cle_prochain(self.temps, direction = "recule")

    def __commande_curseur(self, value):
        """Met à jour le temps lorsque le slider est utilisé"""
        if self.defil:
            self.__commande_pause()
        self.temps = round(value)
        
    def mise_a_jour_lecture(self):
        """Met à jour le temps à chaque 0.1 seconde"""
        if self.defil and self.temps < self.simulateur.temps_max():
            self.temps += 1
            self.after(100,self.mise_a_jour_lecture)    
        else: 
            self.__commande_pause()

class App(ctk.CTk):
    """
    La fenêtre principale du programme. Inclus le graphique et la ligne de temps.
    """

    def __init__(self):
        super().__init__()

        # Propriétés de la fenêtre
        self.geometry("600x500")
        self.title("Simulation Projectile Cosmique")
        self.minsize(400, 300)
        self.resizable(True, True)

        # NE PAS ENLEVER : Nécéssaire pour assurer que la fermeture de la fenêtre se fait sécuritairement.
        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.protocol()

        # Initialiser la simulation
        self.simulateur = Simulation()

        # Initialiser le graphique et la ligne du temps
        self.graphique = GraphiqueFrame(master=self, simulateur=self.simulateur)  # Besoin de la classe de simu pr ça
        self.graphique.grid(row=0, column=0)
        self.ligne_du_temps = LigneDuTemps(master=self, simulateur=self.simulateur)  # Idem
        self.ligne_du_temps.grid(row=1, column=0, padx=10)

        self.graphique.redessiner()
        

    @property
    def temps(self):
        return self.ligne_du_temps.temps


if __name__ == "__main__":
    from src.astre import AstreFixe
    from src.projectile import Projectile

    app = App()
    app.simulateur.importer("donnees/systeme_solaire.csv")
    app.graphique.redessiner()
    app.mainloop()
