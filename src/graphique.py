import customtkinter as ctk
import numpy as np

#Icônes unicode des boutons de la ligne du temps
ARRET = "⏹"
LECTURE = "⏵"
PAUSE = "⏸"
SUIVANT = "⏭"
PRECEDENT = "⏮"


class Bouton(ctk.CTkButton):
    #Bouton carré avec une icône et la commande appelée au clic.
    """
    Attributs :
        icone : texte affiché sur le bouton (une des icônes ci-dessus).
        commande : fonction appelée au clic.
        taille : largeur et hauteur du bouton en pixels.
    """

    #Constructeur de la classe Bouton
    def __init__(self, master, icone: str, commande, taille: int = 10):
        super().__init__(master=master, text=icone, width=taille, height=taille, command=commande)

    def changer(self, icone: str, commande):
        #Change l'icône et la commande, par exemple pour passer de lecture à pause.
        self.configure(text=icone, command=commande)


class LibelleTemps(ctk.CTkLabel):
    #Texte « Jour N » affiché à côté de la ligne du temps.

    #Constructeur de la classe LibelleTemps
    def __init__(self, master, temps: float = 0):
        super().__init__(master=master, text="")
        self.afficher(temps)

    def afficher(self, temps: float):
        #Met à jour le texte avec le temps en jours (arrondi à l'unité).
        self.configure(text=f"Jour {int(round(temps))}")


def taille_affichage(taille: float, minimum: float = 5, maximum: float = 300) -> float:
    #Convertit la taille du CSV (rayon relatif à la Terre) en surface de point pour scatter.
    #Échelle logarithmique : le Soleil (109) et Mercure (0,38) restent visibles tous les deux.
    taille_log = np.log10(max(taille, 0.01))      # entre -2 et environ 2,04 pour le Soleil
    fraction = (taille_log + 2) / 4.1             # ramène l'intervalle entre 0 et 1
    return minimum + (maximum - minimum) * min(max(fraction, 0), 1)


def limites_axes(astres, marge: float = 0.1) -> float:
    #Demi-largeur de la vue en UA : orbite la plus éloignée (parent compris) plus une marge de 10 %.
    #Sert à fixer ax.set_xlim(-l, l) et ax.set_ylim(-l, l) pour que la vue ne saute pas à chaque image.
    plus_loin = 0.0
    for astre in astres:
        distance = astre.distance
        parent = astre.parent
        while parent is not None:
            distance += parent.distance
            parent = parent.parent
        plus_loin = max(plus_loin, distance)
    return (plus_loin or 1.0) * (1 + marge)


def tracer_orbite(ax, astre, t: float, points: int = 100):
    #Trace en pointillé le cercle de l'orbite de l'astre autour de son centre au temps t (le Soleil ou son parent).
    if astre.distance == 0:
        return
    centre = np.zeros(2) if astre.parent is None else astre.parent.position(t)
    angles = np.linspace(0, 2 * np.pi, points)
    x = centre[0] + astre.distance * np.cos(angles)
    y = centre[1] + astre.distance * np.sin(angles)
    ax.plot(x, y, linestyle=":", linewidth=0.8, color=astre.couleur, alpha=0.6)


class PanneauAstres(ctk.CTkScrollableFrame):
    #Tableau défilant qui affiche chaque astre fixe et ses caractéristiques.
    """
    Colonnes : couleur, nom, masse (masses terrestres), rayon (UA), distance (UA),
    période (jours), phase (degrés), parent et actif.
    """

    COLONNES = ("", "Nom", "Masse (MT)", "Rayon (UA)", "Distance (UA)", "Période (j)", "Phase (°)", "Parent", "Actif")

    #Constructeur de la classe PanneauAstres
    def __init__(self, master, astres=(), **kwargs):
        super().__init__(master=master, label_text="Astres fixes", **kwargs)
        self.afficher(astres)

    def afficher(self, astres):
        #Efface le tableau puis écrit une ligne d'en-tête et une ligne par astre.
        for widget in self.winfo_children():
            widget.destroy()
        for colonne, titre in enumerate(self.COLONNES):
            ctk.CTkLabel(self, text=titre, font=ctk.CTkFont(weight="bold")).grid(row=0, column=colonne, padx=6, sticky="w")
        for ligne, astre in enumerate(astres, start=1):
            ctk.CTkLabel(self, text="", width=14, height=14, fg_color=astre.couleur, corner_radius=7).grid(row=ligne, column=0, padx=6)
            valeurs = (astre.nom, f"{astre.masse:g}", f"{astre.rayon:.3g}", f"{astre.distance:g}", f"{astre.periode:g}",
                       f"{astre.phase:g}", astre.parent.nom if astre.parent else "—", "oui" if astre.actif else "non")
            for colonne, valeur in enumerate(valeurs, start=1):
                ctk.CTkLabel(self, text=valeur).grid(row=ligne, column=colonne, padx=6, sticky="w")
