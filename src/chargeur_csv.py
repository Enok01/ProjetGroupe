import pandas as pd

from src.astre import AstreFixe, en_booleen  # Levy : pour créer les objets dans charger_csv
from src.projectile import Projectile

COLONNES_communes = ["nom", "masse", "couleur", "taille", "rayon", "actif"]  #couleur rgb
COLONNES_fixes = ["distance", "periode", "phase", "parent"]
COLONNES_projectiles = ["x0", "y0", "vx0", "vy0", "temps d'apparition", "durree de vie"]  # Levy : mêmes noms que dans donnees/systeme_solaire.csv (sinon notre propre fichier était refusé)
APPARITION, DUREE = COLONNES_projectiles[4], COLONNES_projectiles[5]  # Levy : noms écrits une seule fois, utilisés plus bas
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
        raise ValueError(f"le fichier {fichier} n'a pas été trouvé")
    except PermissionError:
        raise ValueError(f"le fichier {fichier} n'a pas pu être ouvert. Le fichier est peut-être ouvert dans un autre programme, exemple : Excel).")
     
    df = df.dropna(how='all')   # Enlever les lignes complètement vides
    if df.empty:
        raise ValueError(f"le fichier {fichier} ne contient aucune objet")  #verifie qu'il y a au moins un objet dans le fichier
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
                                          float(row[APPARITION]), float(row[DUREE]), en_booleen(row["actif"])))

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

        if str(row["type"]).strip().lower() not in ("astrefixe", "projectile"): # Levy : le CSV écrit AstreFixe ou Projectile, pas true/false
            erreurs.append(f" la valeur de 'type' pour l'objet {row['nom']} n'est pas valide : {row['type']}. La valeur doit être AstreFixe ou Projectile.")
            continue # Erreur critique! sans type on ne sais pas Quelle colonne vérifier. 

        if str(row["actif"]).lower() not in ("true", "false"): # Même raison que plus tôt 
             erreurs.append(f" la valeur de 'actif' pour l'objet {row['nom']} n'est pas valide : {row['actif']}. La valeur doit être un booléen.")

        est_fixe:bool = str(row["type"]).strip().lower() == "astrefixe"  # Levy : même raison que pour le type

        # on va départager les colonne avec les nb ce qu'on a besoin de vérifier en fonction de si c'est fixe ou pas. 
        
        colonnes_nombres = ["masse", "taille", "rayon"]
        if est_fixe:
            colonnes_nombres += ["distance", "periode", "phase"]
        else:
            colonnes_nombres += [APPARITION, DUREE, "x0", "y0", "vx0", "vy0"]  # Levy : noms des colonnes du CSV
        
        
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
            if valeurs[APPARITION] < 0:  # Levy : noms des colonnes du CSV
                erreurs.append(f" la valeur de '{APPARITION}' pour l'objet {row['nom']} n'est pas valide : {row[APPARITION]}. La valeur doit être positive.")

            if valeurs[DUREE] <= 0:  # Levy : noms des colonnes du CSV
                erreurs.append(f" la valeur de '{DUREE}' pour l'objet {row['nom']} n'est pas valide : {row[DUREE]}. La valeur doit être positive.")



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
            "type": "AstreFixe",  # Levy : même valeur que dans le CSV lu
            "nom": astre.nom,
            "masse": astre.masse,
            "couleur": astre.couleur,
            "taille": astre.taille,
            "rayon": astre.rayon,
            "actif": str(astre.actif).lower(),  # Levy : il manquait () pour appeler lower
            "distance": astre.distance,
            "periode": astre.periode,
            "phase": astre.phase,
            "parent": astre.parent.nom if astre.parent else ""  # Levy : plantait pour un astre sans parent
        })

    for projectile in sim.projectiles:
        
        x, y, vx, vy = projectile.historique[0]
        lignes.append({
            "type": "Projectile",  # Levy : même valeur que dans le CSV lu
            "nom": projectile.nom,
            "masse": projectile.masse,
            "couleur": projectile.couleur,
            "taille": projectile.taille,
            "rayon": projectile.rayon,
            "actif": str(projectile.actif).lower(),  # Levy : il manquait () pour appeler lower
            "x0": x,
            "y0": y,
            "vx0": vx,
            "vy0": vy,
            APPARITION: projectile.temps_apparition,  # Levy : noms des colonnes du CSV
            DUREE: projectile.duree_vie,
        })

    df = pd.DataFrame(lignes, columns=COLONNES_tous)
    try:
        df.to_csv(fichier, index=False)  # Levy : le fichier n'était jamais écrit
        # Levy : to_csv écrit le tableau dans un fichier, index=False évite une colonne de numéros en plus
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
    except OSError:
        raise ValueError(f"le fichier {fichier} n'a pas pu être écrit.")  # Levy : comme annoncé dans la docstring
