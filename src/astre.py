"""
Classes des objets de la simulation (Levy) : Astre (classe abstraite) et AstreFixe (orbite circulaire).

Documentation officielle :
    numpy : https://numpy.org/doc/stable/reference/
    classes abstraites (abc) : https://docs.python.org/3/library/abc.html
    pandas Series.get (lecture d'une ligne du CSV) : https://pandas.pydata.org/docs/reference/api/pandas.Series.get.html
"""

"""_summary_

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
"""
from abc import ABC, abstractmethod

import numpy as np

#Constante gravitationnelle convertie dans les unités du programme : UA³ / (masse terrestre · jour²) ≈ 8,888e-10
G_SI = 6.67430e-11          # m³ / (kg · s²)
MT_EN_KG = 5.9722e24        # masse terrestre en kg
JOUR_EN_S = 86400.0         # jour en secondes
UA_EN_M = 149597870700.0    # unité astronomique en mètres
G = G_SI * MT_EN_KG * JOUR_EN_S ** 2 / UA_EN_M ** 3


def en_booleen(valeur) -> bool:
    """_summary_

    Args:
        valeur (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        bool: _description_
    """
    #Convertit la valeur « actif » du CSV ou d'un formulaire en booléen.
    #Attention : bool("false") vaut True en Python, d'où cette fonction.
    #np.bool_ : le type booléen de numpy, que pandas donne quand il lit true/false dans le CSV
    #https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.bool
    if isinstance(valeur, (bool, np.bool_)):
        return bool(valeur)
    texte = str(valeur).strip().lower()
    if texte in ("true", "vrai", "oui", "1", "1.0"):
        return True
    if texte in ("false", "faux", "non", "0", "0.0"):
        return False
    raise ValueError(f"« {valeur} » n'est pas une valeur valide pour actif (attendu true ou false)")


class Astre(ABC):
    
    #Classe abstraite commune aux astres fixes et aux projectiles.
    """
    Attributs :
        nom : nom unique de l'objet.
        masse : masse en masses terrestres (Terre = 1), comme dans systeme_solaire.csv.
        couleur : couleur d'affichage dans le graphique matplotlib (ex. "orange" ou "#FDB813").
        taille : taille d'affichage (rayon relatif à celui de la Terre dans le CSV).
        rayon : rayon de collision en UA.
        actif : un objet inactif n'attire pas et n'est pas simulé.
    """

    #Constructeur de la classe Astre
    def __init__(self, nom: str, masse: float, couleur: str, taille: float, rayon: float, actif: bool = True):
        self.nom = nom
        self.couleur = couleur
        self.actif = en_booleen(actif)
        #Les valeurs numériques peuvent venir du CSV ou d'un formulaire : on vérifie leur conversion
        try:
            self.masse = float(masse)
            self.taille = float(taille)
            self.rayon = float(rayon)
        except (TypeError, ValueError):
            raise ValueError(f"Astre « {nom} » : masse, taille et rayon doivent être des nombres") from None
        if self.masse < 0 or self.rayon < 0 or self.taille <= 0:
            raise ValueError(f"Astre « {nom} » : masse et rayon doivent être positifs, taille strictement positive")

    @abstractmethod
    def position(self, t: float) -> np.ndarray:
        #Renvoie la position (x, y) en UA au temps t (jours), tableau numpy de forme (2,).
        pass

    def distance_a(self, point, t: float) -> float:
        """_summary_

        Args:
            point (_type_): _description_
            t (float): _description_

        Returns:
            float: _description_
        """
        #Distance en UA entre le centre de l'objet au temps t et un point (x, y).
        #np.asarray transforme le point (liste ou tuple) en tableau numpy pour pouvoir soustraire
        #https://numpy.org/doc/stable/reference/generated/numpy.asarray.html
        #np.linalg.norm donne la longueur du vecteur : racine(dx² + dy²)
        #https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html
        return float(np.linalg.norm(np.asarray(point, dtype=float) - self.position(t)))

    def contient(self, point, t: float) -> bool:
        #Vrai si le point (x, y) est à l'intérieur du rayon de collision au temps t (sert à détecter les collisions).
        return self.distance_a(point, t) < self.rayon

    def acceleration_sur(self, point, t: float) -> np.ndarray:
        """_summary_

        Args:
            point (_type_): _description_
            t (float): _description_

        Returns:
            np.ndarray: _description_
        """
        #Accélération gravitationnelle (UA/jour²) que l'objet exerce sur un point (x, y) au temps t :
        #a = G * M * (r_astre - r) / ||r_astre - r||³. Un objet inactif ou sans masse n'attire pas.
        if not self.actif or self.masse == 0:
            #np.zeros(2) : le vecteur nul [0, 0] : https://numpy.org/doc/stable/reference/generated/numpy.zeros.html
            return np.zeros(2)
        ecart = self.position(t) - np.asarray(point, dtype=float)
        distance = np.linalg.norm(ecart)
        if distance == 0:
            #Point au centre exact : la force n'est pas définie, on renvoie zéro pour éviter la division par 0
            return np.zeros(2)
        return G * self.masse * ecart / distance ** 3

    def __str__(self):
        return f"Astre(nom={self.nom}, masse={self.masse}, couleur={self.couleur}, taille={self.taille}, rayon={self.rayon}, actif={self.actif})"


class AstreFixe(Astre):
    #Astre en orbite circulaire autour du centre (0, 0) ou autour de son parent (lune).
    """
    Attributs :
        distance : rayon de l'orbite en UA (0 = immobile au centre, comme le Soleil).
        periode : période de révolution en jours (0 = immobile).
        phase : angle de l'astre à t = 0, en degrés (comme dans systeme_solaire.csv).
        parent : astre autour duquel il tourne, ou None pour le centre.
    """

    #Constructeur de la classe AstreFixe
    def __init__(self, nom: str, masse: float, couleur: str, taille: float, rayon: float, actif: bool = True,
                 distance: float = 0.0, periode: float = 0.0, phase: float = 0.0, parent=None):
        """_summary_

        Args:
            nom (str): _description_
            masse (float): _description_
            couleur (str): _description_
            taille (float): _description_
            rayon (float): _description_
            actif (bool, optional): _description_. Defaults to True.
            distance (float, optional): _description_. Defaults to 0.0.
            periode (float, optional): _description_. Defaults to 0.0.
            phase (float, optional): _description_. Defaults to 0.0.
            parent (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        super().__init__(nom, masse, couleur, taille, rayon, actif)
        try:
            self.distance = float(distance)
            self.periode = float(periode)
            self.phase = float(phase)
        except (TypeError, ValueError):
            raise ValueError(f"AstreFixe « {nom} » : distance, période et phase doivent être des nombres") from None
        if self.distance < 0 or self.periode < 0:
            raise ValueError(f"AstreFixe « {nom} » : distance et période doivent être positives")
        if parent is self:
            raise ValueError(f"AstreFixe « {nom} » ne peut pas être son propre parent")
        self.parent = parent

    def _temps(self, t) -> float:
        #Convertit le temps en nombre de jours, avec un message clair si t n'est pas un nombre.
        try:
            return float(t)
        except (TypeError, ValueError):
            raise ValueError(f"AstreFixe « {self.nom} » : le temps doit être un nombre de jours, reçu {t!r}") from None

    def _angle(self, t: float) -> float:
        #Angle en radians au temps t : theta = 2*pi*t/T + phase (l'angle reste égal à la phase si T = 0).
        #La phase est donnée en degrés, on la convertit en radians pour cos et sin.
        t = self._temps(t)
        #np.radians convertit des degrés en radians : https://numpy.org/doc/stable/reference/generated/numpy.radians.html
        #np.pi vaut 3.14159... : https://numpy.org/doc/stable/reference/constants.html
        phase = np.radians(self.phase)
        if self.periode > 0:
            return 2 * np.pi * t / self.periode + phase
        return phase

    def position(self, t: float) -> np.ndarray:
        #Position r(t) = centre + d * (cos(theta), sin(theta)), le centre étant (0, 0) ou le parent.
        theta = self._angle(t)
        centre = np.zeros(2) if self.parent is None else self.parent.position(t)
        #np.array crée le vecteur [x, y] ; np.cos et np.sin prennent un angle en radians
        #https://numpy.org/doc/stable/reference/generated/numpy.array.html
        #https://numpy.org/doc/stable/reference/generated/numpy.cos.html
        return centre + self.distance * np.array([np.cos(theta), np.sin(theta)])

    def vitesse(self, t: float) -> np.ndarray:
        #Vitesse en UA/jour, dérivée de la position : v(t) = (2*pi/T) * d * (-sin(theta), cos(theta)).
        v_parent = np.zeros(2) if self.parent is None else self.parent.vitesse(t)
        if self.periode <= 0 or self.distance == 0:
            return v_parent
        theta = self._angle(t)
        return v_parent + (2 * np.pi / self.periode) * self.distance * np.array([-np.sin(theta), np.cos(theta)])

    @classmethod
    def depuis_ligne(cls, ligne):
        #Crée un AstreFixe à partir d'une ligne du CSV (dictionnaire ou ligne pandas).
        #Les cases vides valent la valeur par défaut ; le parent (lune) est relié ensuite par le chargeur CSV.
        try:
            nom = str(ligne["nom"]).strip()
        except (KeyError, TypeError):
            raise ValueError("Ligne CSV invalide : la colonne « nom » est manquante") from None

        def nombre(cle, defaut=0.0):
            #ligne.get(cle, defaut) : la valeur de la colonne, ou defaut si la colonne n'existe pas
            #(marche pour un dictionnaire et pour une ligne pandas) : https://pandas.pydata.org/docs/reference/api/pandas.Series.get.html
            valeur = ligne.get(cle, defaut)
            if valeur is None or str(valeur).strip() == "":
                return defaut
            try:
                valeur = float(valeur)
            except (TypeError, ValueError):
                raise ValueError(f"Astre « {nom} », colonne « {cle} » : « {valeur} » n'est pas un nombre") from None
            #np.isnan : vrai si la valeur est NaN, ce que pandas met dans une case vide du CSV
            #https://numpy.org/doc/stable/reference/generated/numpy.isnan.html
            return defaut if np.isnan(valeur) else valeur

        return cls(
            nom=nom,
            masse=nombre("masse"),
            couleur=str(ligne.get("couleur") or "#FFFFFF").strip(),
            taille=nombre("taille", 5.0),
            rayon=nombre("rayon"),
            actif=en_booleen(ligne.get("actif", True)),
            distance=nombre("distance"),
            periode=nombre("periode"),
            phase=nombre("phase"),
        )

    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return f"AstreFixe(nom={self.nom}, masse={self.masse}, distance={self.distance}, periode={self.periode}, phase={self.phase}, actif={self.actif})"
