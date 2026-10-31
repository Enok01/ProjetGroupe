import pandas as pd
import random
from matplotlib.colors import is_color_like, to_hex

from src.astre import AstreFixe, en_booleen  # Levy : pour créer les objets dans charger_csv
from src.projectile import Projectile

COLONNES_communes = ["nom", "masse", "couleur", "taille", "rayon", "actif"]
COLONNES_fixes = ["distance", "periode", "phase", "parent"]
COLONNES_projectiles = ["x0", "y0", "vx0", "vy0", "temps_apparition", "duree_vie"]  # Levy : mêmes noms que dans donnees/systeme_solaire.csv (sinon notre propre fichier était refusé)
COLONNES_tous = ["type"]+COLONNES_communes + COLONNES_fixes + COLONNES_projectiles

def lire_csv(fichier):
    """
    Lit un fichier CSV et regarder si on a des lignes complètement vides pour les enlever.
    Args:
        fichier (str): Chemin vers le fichier CSV.
    Returns:
        pd.DataFrame: une ligne par objet.
    """
    try:
        df = pd.read_csv(fichier)
       
    except FileNotFoundError:
        raise FileNotFoundError(f"le fichier {fichier} n'a pas été trouvé")
    except PermissionError:
        raise PermissionError(f"le fichier {fichier} n'a pas pu être ouvert. Le fichier est peut-être ouvert dans un autre programme, exemple : Excel).")
     
    df = df.dropna(how='all')   # Enlever les lignes complètement vides
    if df.empty:
        raise ValueError(f"le fichier {fichier} ne contient aucune objet")  #verifie qu'il y a au moins un objet dans le fichier
    return df

def couleur_aleatoire(couleurs_utilisees):
    """
    Retourne une couleur au hasard, au format "#rrggbb", qui n'est pas déjà utilisée.

    Args:
        couleurs_utilisees (set[str]): Couleurs déjà prises, au format "#rrggbb".

    Returns:
        str: Une nouvelle couleur.
    """
    while True:
        rouge = random.randint(0, 255)
        vert = random.randint(0, 255)
        bleu = random.randint(0, 255)
        couleur = f"#{rouge:02x}{vert:02x}{bleu:02x}"  #Transforme en hexadécimal. J'en ai besoin parce que c'est ca que matplotlib comprend
        if couleur not in couleurs_utilisees:
            return couleur

        
def corriger_couleurs(df):
    """
    Donne une couleur au hasard aux objets dont la couleur est vide, invalide
    ou déjà utilisée par un objet plus haut dans le fichier.
    **  Je pars du principe que ce qui va avoir dans le tableau est soit le nom ou la couleur (exemple : rouge), ou la valeur en hexadécimal (exemple : #rrggbb). 
    Args:
        df (pd.DataFrame): Données validées.

    Returns:
        pd.DataFrame: Une copie du DataFrame avec des couleurs toutes différentes.
    """
    df = df .copy() # comme ca on ne modifie pas le DataFrame reçu
    couleurs_utilisees = set() #Sert juste à comparer, au cas où on a besoin d'une nouvelle couleur et qu'on ne remet pas la même couleur ou une couleur qui existe déjà. 

    for id, row in df.iterrows():
        couleur = row["couleur"]

        #Pour que tout soit équitable, on va changer les valeurs de couleur en hexadécimal. 
        if isinstance(couleur,str) and is_color_like(couleur.strip()):   # is_color_like va returne un true si c'est une couleur valide de matplotlib
            couleur_hex = to_hex(couleur.strip())
        else:
            couleur_hex = None # car c,est soit une case vide ou une couleur mal ecrit

        if couleur_hex is None or couleur_hex in couleurs_utilisees:
            couleur_hex = couleur_aleatoire(couleurs_utilisees)
            df.at[id, "couleur"]= couleur_hex      # On remplace seulement si nécessaire

        couleurs_utilisees.add(couleur_hex)

    return df

def charger_csv(fichier):
    """
    Charge un fichier CSV, le vérifie et crée les objets de la simulation.
    Args:
        fichier (str): Chemin vers le fichier CSV.
    Returns:
        tuple: (liste des AstreFixe, liste des Projectile).

    """
    df = lire_csv(fichier)
    erreurs = valider_csv(df)

    if erreurs:
        raise ValueError("\n".join(erreurs))

    df = corriger_couleurs(df)  # Levy : on garde la correction des couleurs de Demba avant de créer les objets
    # Levy : on renvoie des objets au lieu du DataFrame, sinon la simulation ne peut rien en faire
    astres, projectiles, parents = [], [], []
    # Levy : iterrows parcourt le tableau ligne par ligne et donne (index, ligne)
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html
    for _, row in df.iterrows():
        if str(row["type"]).strip().lower() == "astrefixe":
            astres.append(AstreFixe.depuis_ligne(row))
            parents.append(row["parent"])
        else:
            projectiles.append(Projectile(str(row["nom"]).strip(), row["masse"], str(row["couleur"]).strip(), row["taille"], row["rayon"],
                                          (row["x0"], row["y0"]), (row["vx0"], row["vy0"]),
                                          float(row["temps_apparition"]), float(row["duree_vie"]), en_booleen(row["actif"])))

    # Levy : relie chaque lune à son parent (valider_csv a déjà vérifié que le parent existe)
    par_nom = {astre.nom: astre for astre in astres}
    for astre, parent in zip(astres, parents):
        # Levy : pd.isna est vrai pour une case vide (NaN) : https://pandas.pydata.org/docs/reference/api/pandas.isna.html
        if not pd.isna(parent):
            astre.parent = par_nom[str(parent).strip()]
    return astres, projectiles

def valider_csv(df):
    """
    Vérifie le contenu du DataFrame lu dans le CSV.
    Args:
        df (pd.DataFrame): Données lues par _lire_fichier.
    Returns:
        list[str]: Les messages d'erreur trouvés. Une liste vide veut dire
        que le fichier est valide.
    Raises:
        ValueError: Si le fichier ne peut pas être lu ou contient des erreurs.
    """
    erreurs = []

    # Vérifier que toutes les colonnes attendues sont présentes
    colonnes_manquantes = [col for col in COLONNES_tous if col not in df.columns] # met les colonnes pour lesquelles il n'y a pas de correspondance dans le fichier CSV: je vous invite a bien verifier que les noms de colonnes dans le CSV correspondent exactement à ceux attendus, y compris la casse et les espaces.je suis pas le meilleur pour les compreantion :)
    if colonnes_manquantes:
        erreurs.append(f"le fichier  ne contient pas les colonnes attendues : {colonnes_manquantes}")
        return erreurs  # On peut arrêter la vérification si les colonnes sont manquantes, car c'est une erreur critique!


    #  Vérification des valeurs
    for id, row in df.iterrows():
        if pd.isna(row["nom"]):
            erreurs.append(f" la valeur de 'nom' pour l'objet à l'index {id} est vide. Le nom doit être une chaîne de caractères non vide.")  
            continue  # On peut arrêter la vérification si le nom est vide, car c'est une erreur critique!

        if str(row["type"]).strip() not in ("AstreFixe", "Projectile"): # Le type doit être le nom d'une des deux classes. strip() enlève les espaces autour
            erreurs.append(f" la valeur de 'type' pour l'objet {row['nom']} n'est pas valide : {row['type']}. La valeur doit être AstreFixe ou Projectile.")
            continue # Erreur critique! sans type on ne sais pas Quelle colonne vérifier.

        if str(row["actif"]).lower() not in ("true", "false"): #On ne sait pas si le type va être écrit comme un booléen ou un texte en minuscule, donc on transforme en minuscule pour être sûr 
             erreurs.append(f" la valeur de 'actif' pour l'objet {row['nom']} n'est pas valide : {row['actif']}. La valeur doit être un booléen.")

        est_fixe:bool = str(row["type"]).strip() == "AstreFixe"

        # on va départager les colonne avec les nb ce qu'on a besoin de vérifier en fonction de si c'est fixe ou pas. 
        
        colonnes_nombres = ["masse", "taille", "rayon"]
        if est_fixe:
            colonnes_nombres += ["distance", "periode", "phase"]
        else:
            colonnes_nombres += ["temps_apparition", "duree_vie", "x0", "y0", "vx0", "vy0"]
        
        
        valeurs = {}  # les valeurs converties en nombres
        nombre_invalide = False
        for col in colonnes_nombres:
            valeurs[col] = pd.to_numeric(row[col], errors="coerce")  # https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html ex: si c'est "abc" ou une case vide sa devin NaN
            if pd.isna(valeurs[col]):
                erreurs.append(f" la valeur de '{col}' pour l'objet {row['nom']} n'est pas valide : {row[col]}. La valeur doit être un nombre.")
                nombre_invalide = True
        if nombre_invalide:

            continue  # On peut arrêter la vérification, car c'est une erreur critique qui va engendrer beaucoup d'autres erreurs!
      


        if valeurs["masse"] <= 0:
            erreurs.append(f" la valeur de 'masse' pour l'objet {row['nom']} n'est pas valide : {row['masse']}. La valeur doit être positive.")

        if valeurs["taille"] <= 0:
            erreurs.append(f" la valeur de 'taille' pour l'objet {row['nom']} n'est pas valide : {row['taille']}. La valeur doit être strictement positive.")

        if valeurs["rayon"] <= 0:
            erreurs.append(f" la valeur de 'rayon' pour l'objet {row['nom']} n'est pas valide : {row['rayon']}. La valeur doit être positive.")

        
        if est_fixe:
            if valeurs["distance"] < 0:
                erreurs.append(f" la valeur de 'distance' pour l'objet {row['nom']} n'est pas valide : {row['distance']}. La valeur doit être positive.")

            if valeurs["periode"] < 0:
                erreurs.append(f" la valeur de 'periode' pour l'objet {row['nom']} n'est pas valide : {row['periode']}. La valeur doit être positive.")

        else:
            if valeurs["temps_apparition"] < 0:
                erreurs.append(f" la valeur de 'temps_apparition' pour l'objet {row['nom']} n'est pas valide : {row["temps_apparition"]}. La valeur doit être positive.")

            if valeurs["duree_vie"] <= 0:
                erreurs.append(f" la valeur de 'duree_vie' pour l'objet {row['nom']} n'est pas valide : {row["duree_vie"]}. La valeur doit être positive.")



        if row["parent"] not in df["nom"].values and not pd.isna(row["parent"]):
            erreurs.append(f" la valeur de 'parent' pour l'objet {row['nom']} n'est pas valide : {row['parent']}. La valeur doit être le nom d'un autre objet ou None.")

        #couleur 
    return erreurs


def sauvegarder(sim, fichier):
    """
    Sauvegarde la configuration de la simulation dans un fichier CSV,
    au même format que le fichier d'entrée, pour pouvoir le recharger.

    Args:
        sim (Simulation): La simulation à sauvegarder.
        fichier (str):  chemin où écrire le fichier.

    Raises:
        ValueError: Si le fichier ne peut pas être écrit.
    """

    lignes = []

    for astre in sim.astres:  # Je suppose qu'il y a un self.astres = [] dans la classe simulation. 
        lignes.append({
            "type": "AstreFixe",
            "nom": astre.nom,
            "masse": astre.masse,
            "couleur": astre.couleur,
            "taille": astre.taille,
            "rayon": astre.rayon,
            "actif": str(astre.actif).lower(),
            "distance": astre.distance,
            "periode": astre.periode,
            "phase": astre.phase,
            "parent": astre.parent.nom if astre.parent is not None else None # On ne veut pas de conflit s'il n'y a pas de parents. 
        })

    for projectile in sim.projectiles:
        
        x, y, vx, vy = projectile.historique[0]
        lignes.append({
            "type": "Projectile",
            "nom": projectile.nom,
            "masse": projectile.masse,
            "couleur": projectile.couleur,
            "taille": projectile.taille,
            "rayon": projectile.rayon,
            "actif": str(projectile.actif).lower(),
            "x0": x,
            "y0": y,
            "vx0": vx,
            "vy0": vy,
            "temps_apparition": projectile.temps_apparition,
            "duree_vie": projectile.duree_vie,
        })

    df = pd.DataFrame(lignes, columns=COLONNES_tous)

    try:
        df.to_csv(fichier, index=False)
    except PermissionError:
        raise ValueError(f"Impossible d'écrire dans « {fichier} ». il est peut-être ouvert dans un autre programme.")
    except OSError:
          raise ValueError(f"Impossible de créer le fichier « {fichier} ». Vérifiez que le dossier existe.")

    
