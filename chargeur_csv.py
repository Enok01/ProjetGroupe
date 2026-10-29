import pandas as pd

COLONNES_communes = ["nom", "masse", "couleur", "taille", "rayon", "actif"]  #couleur rgb 
COLONNES_fixes = ["distance", "periode", "phase", "parent"]
COLONNES_projectiles = ["x0", "y0", "vx0", "vy0", "temps_apparition", "duree_vie"]
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
    Charge un fichier CSV et retourne un DataFrame avec les colonnes attendues.
    Args:
        fichier (str): Chemin vers le fichier CSV.
    Returns:
        pd.DataFrame: DataFrame contenant les données du CSV.

    """
    df = lire_csv(fichier)
    erreurs = validate_csv(df)
    
    if erreurs:
        raise ValueError("\n".join(erreurs))

    
    return df

def validate_csv(df):
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

        if str(row["type"]).lower() not in ("true", "false"): #On ne sait pas si le type va être écrit comme un booléen ou un texte en minuscule, donc on transforme en minuscule pour être sûr 
            erreurs.append(f" la valeur de 'type' pour l'objet {row['nom']} n'est pas valide : {row['type']}. La valeur doit être un booléen.")
            continue # Erreur critique! sans type on ne sais pas Quelle colonne vérifier. 

        if str(row["actif"]).lower() not in ("true", "false"): # Même raison que plus tôt 
             erreurs.append(f" la valeur de 'actif' pour l'objet {row['nom']} n'est pas valide : {row['actif']}. La valeur doit être un booléen.")

        est_fixe:bool = str(row["type"]).lower() == "true" 

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
                erreurs.append(f" la valeur de 'temps_apparition' pour l'objet {row['nom']} n'est pas valide : {row['temps_apparition']}. La valeur doit être positive.")

            if valeurs["duree_vie"] <= 0:
                erreurs.append(f" la valeur de 'duree_vie' pour l'objet {row['nom']} n'est pas valide : {row['duree_vie']}. La valeur doit être positive.") 



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
            "type": "true",
            "nom": astre.nom,
            "masse": astre.masse,
            "couleur": astre.couleur,
            "taille": astre.taille,
            "rayon": astre.rayon,
            "actif": str(astre.actif).lower,
            "distance": astre.distance,
            "periode": astre.periode,
            "phase": astre.phase,
            "parent": astre.parent.nom 
        })

    for projectile in sim.projectiles:
        
        x, y, vx, vy = projectile.historique[0]
        lignes.append({
            "type": "false",
            "nom": projectile.nom,
            "masse": projectile.masse,
            "couleur": projectile.couleur,
            "taille": projectile.taille,
            "rayon": projectile.rayon,
            "actif": str(projectile.actif).lower,
            "x0": x,
            "y0": y,
            "vx0": vx,
            "vy0": vy,
            "temps_apparition": projectile.temps_apparition,
            "duree_vie": projectile.duree_vie,
        })

    df = pd.DataFrame(lignes, columns=COLONNES_tous)

    
