import customtkinter as ctk

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
