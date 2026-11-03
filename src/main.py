from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from src.simulation import Simulation  # placeholder
from src.graphique import BarreHaut
from src.chargeur_csv import charger_csv, sauvegarder #Levy Correction import était mal fait 
from src.physique import calculer_trajectoire
from src.exceptions import HorsSystemeError, TempsMaximumAtteinte


class GraphiqueFrame(ctk.CTkFrame):
    """
    Le graphique.
    """

    def __init__(self, master: App, simulateur: Simulation):
        super().__init__(master=master)
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

        # --- Repeupler le graphique ---
        # Affichage des astres
        for astre in self.simulateur.astres:
            if astre.actif:
                # Marqueur de position actuelle
                x, y = astre.position(self.temps)
                self.ax.scatter(x, y, astre.taille, astre.couleur)

        # Affichage des Projectiles (seulement ceux dont la trajectoire a été calculée par « Lancer projectile »)
        for projectile in self.simulateur.projectiles:
            if projectile.actif and len(projectile.historique) > 1:
                # Marqueur de position actuelle
                x, y = projectile.position(self.temps)
                self.ax.scatter(x, y, projectile.taille, projectile.couleur)

                # Trajectoire
                # Levy : historique[:, 0] prend la colonne 0 (tous les x) du tableau numpy, [:, 1] tous les y
                # https://numpy.org/doc/stable/user/basics.indexing.html
                # Levy : plot relie les points par une ligne : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html
                self.ax.plot(projectile.historique[:, 0], projectile.historique[:, 1], color=projectile.couleur, linewidth=0.8)

        self.canvas.draw_idle()


class LigneDuTemps(ctk.CTkFrame):
    """
    Une ligne du temps avec un bouton arrêt, jouer/mettre sur pause, avancer au moment-clé prochain, retourner au
    moment-clé précédent.
    """

    def __init__(self, master: App, simulateur: Simulation):
        super().__init__(master=master)
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
        self.geometry("600x500")
        self.title("Simulation Projectile Cosmique")
        self.minsize(400, 300)
        self.resizable(True, True)

        # NE PAS ENLEVER : Nécéssaire pour assurer que la fermeture de la fenêtre se fait sécuritairement.
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # Initialise la simulation
        self.simulateur = Simulation()

        # Initialise le graphique et la ligne du temps
        self.graphique = GraphiqueFrame(master=self, simulateur=self.simulateur)  # Besoin de la classe de simu pr ça
        self.graphique.grid(row=0, column=0)
        self.ligne_du_temps = LigneDuTemps(master=self, simulateur=self.simulateur)  # Idem
        self.ligne_du_temps.grid(row=1, column=0, padx=10)

        # Boutons ouvrir CSV, sauvegarder et lancer projectile
        self.barre_outils = BarreHaut(self, self.ouvrir_csv, self.sauvegarder_csv, self.lancer_projectile)
        self.barre_outils.grid(row=2, column=0, pady=4)

        self.graphique.redessiner()
        

    @property
    def temps(self):
        return self.ligne_du_temps.temps

    def ouvrir_csv(self):
        """Demande un fichier CSV et charge ses astres fixes et projectiles dans la simulation (Levy)."""
        # Levy : askopenfilename ouvre la fenêtre « Ouvrir » de Windows et renvoie le chemin choisi ("" si annulé)
        # https://docs.python.org/3/library/dialog.html#tkinter.filedialog.askopenfilename
        chemin = filedialog.askopenfilename(title="Ouvrir un fichier CSV", filetypes=[("Fichiers CSV", "*.csv")])
        if not chemin:
            return
        try:
            self.simulateur.astres, self.simulateur.projectiles = charger_csv(chemin)
        except (OSError, KeyError, ValueError) as erreur:
            # Levy : showerror affiche une petite fenêtre d'erreur : https://docs.python.org/3/library/tkinter.messagebox.html
            messagebox.showerror("Ouvrir CSV", f"Impossible de lire le fichier :\n{erreur}")
            return
        # Levy : configure(to=...) change la valeur maximale du curseur
        # https://customtkinter.tomschimansky.com/documentation/widgets/slider
        self.ligne_du_temps.slider.configure(to=self.simulateur.temps_max())
        self.ligne_du_temps.temps = 0

    def sauvegarder_csv(self):
        """Demande où enregistrer et écrit les astres et projectiles dans un CSV (Levy)."""
        # Levy : asksaveasfilename ouvre la fenêtre « Enregistrer sous » ; defaultextension ajoute .csv si oublié
        # https://docs.python.org/3/library/dialog.html#tkinter.filedialog.asksaveasfilename
        chemin = filedialog.asksaveasfilename(title="Sauvegarder", defaultextension=".csv",
                                              filetypes=[("Fichiers CSV", "*.csv")])
        if not chemin:
            return
        try:
            sauvegarder(self.simulateur, chemin)
        except ValueError as erreur:
            messagebox.showerror("Sauvegarder", f"Impossible d'écrire le fichier :\n{erreur}")

    def lancer_projectile(self):
        """Calcule la trajectoire de chaque projectile actif, puis redessine le graphique (Levy)."""
        # Levy : showinfo affiche une fenêtre d'information : https://docs.python.org/3/library/tkinter.messagebox.html
        if not self.simulateur.astres or not self.simulateur.projectiles:
            messagebox.showinfo("Lancer projectile", "Ouvre d'abord un CSV qui contient des astres et au moins un projectile.")
            return
        for projectile in self.simulateur.projectiles:
            if not projectile.actif:
                continue
            projectile.reinitialiser()
            try:
                projectile.cible = calculer_trajectoire(projectile, self.simulateur.astres, self.simulateur.dt, projectile.duree_vie)
                projectile.etat = "collision"
            except HorsSystemeError:
                projectile.etat = "hors systeme"
            except TempsMaximumAtteinte:
                projectile.etat = "expire"
        self.graphique.redessiner()


if __name__ == "__main__":
    # Levy : lance la nouvelle interface de graphique.py (l'ancienne fenêtre App reste dans ce fichier)
    from src.graphique import FenetreSimulateur

    fenetre = FenetreSimulateur()
    fenetre.charger("donnees/systeme_solaire.csv")  # remplit aussi fenetre.simulateur
    fenetre.mainloop()
