"""
Interface graphique du simulateur (Levy). Seulement l'affichage : la logique se branche avec command=...

Documentation officielle :
    customtkinter : https://customtkinter.tomschimansky.com/documentation/
    matplotlib dans tkinter : https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
    matplotlib (Axes) : https://matplotlib.org/stable/api/axes_api.html
    numpy : https://numpy.org/doc/stable/reference/
    placement grid : https://tkdocs.com/tutorial/grid.html
"""
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

FOND = "#0f1424"   # bleu nuit derrière les astres


def texte(master, contenu: str, taille: int = 13, gras: bool = False) -> ctk.CTkLabel:
    """
    Crée une étiquette de texte.

    CTkLabel : https://customtkinter.tomschimansky.com/documentation/widgets/label
    CTkFont : https://customtkinter.tomschimansky.com/documentation/utility-classes/font

    :param master:
    :param contenu: Texte de l'étiquette
    :param taille: Taille de l'étiquette
    :param gras: Si le texte devrait être en gras, comme pour un titre
    :return: L'étiquette générée
    """
    return ctk.CTkLabel(master, text=contenu, font=ctk.CTkFont(size=taille, weight="bold" if gras else "normal"))


def bouton(master, contenu: str, commande=None, couleur=None) -> ctk.CTkButton:
    """
    Crée un bouton.

    CTkButton : https://customtkinter.tomschimansky.com/documentation/widgets/button

    :param master:
    :param contenu: Texte inscrit sur le bouton
    :param commande: Fonction appelée au clic (None = rien pour l'instant)
    :param couleur: Couleur du bouton
    :return: Le bouton généré
    """

    return ctk.CTkButton(master, text=contenu, command=commande, width=100, fg_color=couleur)


def ligne_de_widgets(widgets) -> None:
    """
    Place les widgets fournis côte à côte, de gauche à droite.

    :param widgets: Les widgets à mettre en ligne
    """
    # grid(row, column) range un widget dans une case d'une grille : https://tkdocs.com/tutorial/grid.html
    for colonne, widget in enumerate(widgets):
        widget.grid(row=0, column=colonne, padx=4, pady=8)


class BarreHaut(ctk.CTkFrame):
    """
    Barre du haut : Ouvrir, Enregistrer, Lancer, puis le fichier ouvert.

    CTkFrame (cadre qui regroupe des widgets) : https://customtkinter.tomschimansky.com/documentation/widgets/frame
    """

    def __init__(self, master, ouvrir=None, enregistrer=None, lancer=None, **kwargs):
        super().__init__(master, **kwargs)
        self.info = texte(self, "Aucun fichier")
        ligne_de_widgets([bouton(self, "Ouvrir un CSV…", ouvrir),
                          bouton(self, "Enregistrer…", enregistrer),
                          bouton(self, "Lancer un projectile…", lancer),
                          self.info])

    def afficher_fichier(self, nom: str, nb_astres: int, nb_projectiles: int):
        # configure change une option d'un widget déjà créé, ici son texte.
        self.info.configure(text=f"{nom} · {nb_astres} astres, {nb_projectiles} projectiles")


class GestionnaireObjets(ctk.CTkScrollableFrame):
    """
    Panneau de gauche : un tableau défilant avec une ligne par astre ou projectile.

    CTkScrollableFrame : https://customtkinter.tomschimansky.com/documentation/widgets/scrollableframe
    """

    COLONNES = ("Actif", "Nom", "Type", "Masse (MT)", "Distance (UA)", "Couleur")

    def __init__(self, master):
        super().__init__(master, width=480, label_text="Objets")
        self.afficher()

    def afficher(self, astres=(), projectiles=()):
        """
        Efface le tableau puis le réécrit.

        :param astres:
        :param projectiles:
        :return:
        """

        # winfo_children = widgets contenus, destroy = les supprimer
        for widget in self.winfo_children():
            widget.destroy()

        for colonne, titre in enumerate(self.COLONNES):
            texte(self, titre, gras=True).grid(row=0, column=colonne, padx=6, sticky="w")

        for ligne, objet in enumerate(list(astres) + list(projectiles), start=1):
            est_astre = objet in astres

            # CTkCheckBox (select = cocher) : https://customtkinter.tomschimansky.com/documentation/widgets/checkbox
            case = ctk.CTkCheckBox(self, text="", width=30)
            if objet.actif:
                case.select()
            case.grid(row=ligne, column=0)

            # np.linalg.norm : longueur du vecteur (x, y), donc distance au centre
            # https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html
            distance = objet.distance if est_astre else np.linalg.norm(objet.pos0)
            valeurs = (objet.nom, "astre" if est_astre else "projectile", f"{objet.masse:.3g}", f"{distance:.2f}")
            for colonne, valeur in enumerate(valeurs, start=1):
                texte(self, valeur).grid(row=ligne, column=colonne, padx=6, sticky="w")
            # Pastille de couleur : une étiquette vide dont fg_color est la couleur de fond
            ctk.CTkLabel(self, text="", width=30, height=16, fg_color=objet.couleur, corner_radius=4
                         ).grid(row=ligne, column=5)


class VueGraphique(ctk.CTkFrame):
    """
    Panneau du centre : le graphique matplotlib dans la fenêtre, avec la barre zoom/déplacement.
    """

    def __init__(self, master):
        super().__init__(master)

        # Figure = la zone de dessin, add_subplot(111) = un seul graphique (Axes) dedans
        # https://matplotlib.org/stable/api/figure_api.html
        self.fig = plt.Figure(figsize=(6, 6), facecolor=FOND)
        self.ax = self.fig.add_subplot(111)

        # FigureCanvasTkAgg met la figure dans tkinter, NavigationToolbar2Tk ajoute les boutons zoom/déplacement
        # https://matplotlib.org/stable/api/backend_tk_api.html
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False).pack(side="bottom", fill="x")

        # pack empile les widgets ; fill="both" et expand=True : le graphique prend toute la place
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.dessiner()

    def dessiner(self, astres=(), projectiles=(), t: float = 0.0):
        """
        Dessine au temps t les orbites et les objets actifs avec leur nom.

        :param astres: Les AstreFixe à afficher
        :param projectiles: Les Projectiles à afficher
        :param t: Le moment auquel on souhaite illustrer le tout.
        """

        ax = self.ax
        ax.clear()

        actifs = [objet for objet in list(astres) + list(projectiles) if objet.actif]

        # Vue carrée qui contient l'objet le plus loin (+10 %)
        limite = 1.1 * max([np.linalg.norm(objet.position(t)) for objet in actifs] + [1])

        # Axes.set : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set.html
        ax.set(xlim=(-limite, limite), ylim=(-limite, limite), aspect="equal", facecolor=FOND,
               title=f"t = {t:.1f} jours", xlabel="x (UA)", ylabel="y (UA)")

        # Texte en gris clair, sinon il est noir sur le fond bleu nuit
        # tick_params : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.tick_params.html
        ax.tick_params(colors="lightgray")
        for etiquette in (ax.title, ax.xaxis.label, ax.yaxis.label):
            etiquette.set_color("lightgray")

        for objet in actifs:
            x, y = objet.position(t)
            if objet in astres and objet.distance > 0:
                # Circle + add_patch : cercle de l'orbite autour du Soleil ou du parent
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Circle.html
                centre = objet.parent.position(t) if objet.parent else (0, 0)
                ax.add_patch(plt.Circle(centre, objet.distance, fill=False, color=objet.couleur, alpha=0.4))
            # np.sqrt : racine carrée, pour que le Soleil (taille 109) ne cache pas tout
            taille = max(8, 20 * np.sqrt(objet.taille)) if objet in astres else 25

            # scatter dessine un point, annotate écrit un texte à côté
            ax.scatter(x, y, taille, objet.couleur, zorder=3)
            ax.annotate(objet.nom, (x, y), xytext=(4, 2), textcoords="offset points", color="white", fontsize=7)
        self.fig.tight_layout()  # laisse la place aux titres des axes
        self.canvas.draw_idle()  # redessine la figure dans la fenêtre dès que possible


class DetailsProjectile(ctk.CTkFrame):
    """
    Panneau de droite : choix d'un projectile, ses informations et le bouton d'export.
    """

    INFOS = ("État", "Cible", "Position (UA)", "Vitesse (UA/j)", "Masse (MT)")

    def __init__(self, master, exporter=None):
        super().__init__(master)

        texte(self, "Projectile", 18, True).grid(row=0, column=0, columnspan=2, padx=12, pady=8, sticky="w")

        # CTkComboBox (liste déroulante) : https://customtkinter.tomschimansky.com/documentation/widgets/combobox
        self.choix = ctk.CTkComboBox(self, values=["Aucun projectile"], state="readonly")
        self.choix.grid(row=1, column=0, columnspan=2, padx=12, sticky="ew")
        self.valeurs = {}  # libellé -> étiquette où écrire la valeur
        for ligne, nom in enumerate(self.INFOS, start=2):
            texte(self, nom).grid(row=ligne, column=0, padx=12, pady=3, sticky="w")
            self.valeurs[nom] = texte(self, "—")
            self.valeurs[nom].grid(row=ligne, column=1, padx=12, sticky="w")

        bouton(self, "Exporter la trajectoire…", exporter
               ).grid(row=len(self.INFOS) + 2, column=0, columnspan=2, padx=12, pady=12)

    def afficher(self, noms=(), infos=None):
        # Remplit la liste des projectiles et les valeurs (« — » si une valeur manque).
        noms = list(noms) or ["Aucun projectile"]
        self.choix.configure(values=noms)
        self.choix.set(noms[0])  # set choisit l'élément affiché
        for nom, etiquette in self.valeurs.items():
            etiquette.configure(text=str((infos or {}).get(nom, "—")))


class BarreControle(ctk.CTkFrame):
    """
    Barre du bas : réinitialiser, reculer, jouer, arrêter, avancer, le pas dt et le temps actuel.
    """

    def __init__(self, master):
        super().__init__(master)

        # CTkEntry (case où l'on écrit) : https://customtkinter.tomschimansky.com/documentation/widgets/entry
        self.dt = ctk.CTkEntry(self, width=60)
        self.dt.insert(0, "0.5")  # texte de départ

        # Boutons rangés par nom pour brancher la logique plus tard, ex. barre.boutons["jouer"].configure(command=...)
        self.boutons = {
            "reinitialiser": bouton(self, "Réinitialiser"),
            "reculer": bouton(self, "◀ Reculer"),
            "jouer": bouton(self, "▶ Jouer", couleur="#2e8b57"),
            "arreter": bouton(self, "■ Arrêter", couleur="#c0392b"),
            "avancer": bouton(self, "Avancer ▶")
        }
        self.temps = texte(self, "", gras=True)
        ligne_de_widgets(list(self.boutons.values()) + [texte(self, "dt (jours)"), self.dt, self.temps])
        self.afficher_temps(0)

    def afficher_temps(self, t: float):
        self.temps.configure(text=f"t = {t:.1f} jours")


class FenetreSimulateur(ctk.CTk):
    """
    Fenêtre complète : barre du haut, objets à gauche, graphique au centre, projectile à droite, contrôles en bas.
    CTk (fenêtre principale) : https://customtkinter.tomschimansky.com/documentation/windows/window
    """

    def __init__(self):
        super().__init__()
        self.title("Simulateur de projectiles spatiaux")
        self.geometry("1400x800")
        self.protocol("WM_DELETE_WINDOW", self.quit)  # NE PAS ENLEVER : ferme proprement la fenêtre

        self.barre_haut = BarreHaut(self)
        self.gestionnaire = GestionnaireObjets(self)
        self.vue = VueGraphique(self)
        self.details = DetailsProjectile(self)
        self.barre_controle = BarreControle(self)

        # sticky="nsew" : le panneau s'étire dans sa case ; columnspan=3 : la barre prend les 3 colonnes
        self.barre_haut.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=4)
        for colonne, panneau in enumerate((self.gestionnaire, self.vue, self.details)):
            panneau.grid(row=1, column=colonne, sticky="nsew", padx=4, pady=4)
        self.barre_controle.grid(row=2, column=0, columnspan=3, sticky="ew", padx=8, pady=4)

        # weight=1 : la ligne 1 et la colonne 1 (le graphique) grandissent avec la fenêtre
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def afficher(self, astres=(), projectiles=(), nom_fichier: str = "Aucun fichier", t: float = 0.0):
        """
        Remplit tous les panneaux avec les objets donnés.

        :param astres: Les astres fixes à afficher
        :param projectiles: Les projectiles à afficher
        :param nom_fichier: Nom du fichier
        :param t: Le temps courant
        """
        self.barre_haut.afficher_fichier(nom_fichier, len(astres), len(projectiles))
        self.gestionnaire.afficher(astres, projectiles)
        self.vue.dessiner(astres, projectiles, t)
        infos = {"État": projectiles[0].etat, "Masse (MT)": f"{projectiles[0].masse:g}"} if projectiles else None
        self.details.afficher([projectile.nom for projectile in projectiles], infos)
        self.barre_controle.afficher_temps(t)


# Aperçu de l'interface : « python -m src.graphique » depuis la racine du projet
if __name__ == "__main__":
    from src.chargeur_csv import charger_csv

    fenetre = FenetreSimulateur()
    fenetre.afficher(*charger_csv("../donnees/systeme_solaire.csv"), "systeme_solaire.csv")
    fenetre.mainloop()
