import pandas as pd

COLONNES_communes = ["nom", "masse", "couleur", "taille", "rayon", "actif"]
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
    Raises:
        ValueError: Si le fichier ne contient pas les colonnes attendues.
    """
    df = lire_csv(fichier)
    

    
    return df

def validate_csv(df):
    """
    Vérifie le contenu du DataFrame lu dans le CSV.
    Args:
        df (pd.DataFrame): Données lues par _lire_fichier.
    Returns:
        list[str]: Les messages d'erreur trouvés. Une liste vide veut dire
        que le fichier est valide.
    """
    erreurs = []

    # Vérifier que toutes les colonnes attendues sont présentes
    colonnes_manquantes = [col for col in COLONNES_tous if col not in df.columns] # met les colonnes pour lesquelles il n'y a pas de correspondance dans le fichier CSV: je vous invite a bien verifier que les noms de colonnes dans le CSV correspondent exactement à ceux attendus, y compris la casse et les espaces.je suis pas le meilleur pour les compreantion :)
    if colonnes_manquantes:
        erreurs.append(f"le fichier  ne contient pas les colonnes attendues : {colonnes_manquantes}")
        return erreurs  # On peut arrêter la vérification si les colonnes sont manquantes, car c'est une erreur critique!


    #  Vérification des valeurs
    for id, row in df.iterrows():
        if row['nom'] == "":
            erreurs.append(f" la valeur de 'nom' pour l'objet à l'index {id} est vide. Le nom doit être une chaîne de caractères non vide.")
            continue  # On peut arrêter la vérification si le nom est vide, car c'est une erreur critique!

        if not isinstance(row["type"], bool):
            erreurs.append(f" la valeur de 'type' pour l'objet {row['nom']} n'est pas valide : {row['type']}. La valeur doit être un booléen.")

        if not isinstance(row["actif"], bool):
             erreurs.append(f" la valeur de 'actif' pour l'objet {row['nom']} n'est pas valide : {row['actif']}. La valeur doit être un booléen.")

        if row["masse"] <= 0:
            erreurs.append(f" la valeur de 'masse' pour l'objet {row['nom']} n'est pas valide : {row['masse']}. La valeur doit être positive.")

        if row["taille"] <= 0:
            erreurs.append(f" la valeur de 'taille' pour l'objet {row['nom']} n'est pas valide : {row['taille']}. La valeur doit être strictement positive.")

        if row["rayon"] <= 0:
            erreurs.append(f" la valeur de 'rayon' pour l'objet {row['nom']} n'est pas valide : {row['rayon']}. La valeur doit être positive.")

        if row["distance"] < 0:
            erreurs.append(f" la valeur de 'distance' pour l'objet {row['nom']} n'est pas valide : {row['distance']}. La valeur doit être positive.")

        if row["periode"] < 0:
            erreurs.append(f" la valeur de 'periode' pour l'objet {row['nom']} n'est pas valide : {row['periode']}. La valeur doit être positive.")

        if row["temps_apparition"] < 0:
            erreurs.append(f" la valeur de 'temps_apparition' pour l'objet {row['nom']} n'est pas valide : {row['temps_apparition']}. La valeur doit être positive.")

        if row["duree_vie"] < 0:
            erreurs.append(f" la valeur de 'duree_vie' pour l'objet {row['nom']} n'est pas valide : {row['duree_vie']}. La valeur doit être positive.") 

        if row["x0"] < 0:
            erreurs.append(f" la valeur de 'x0' pour l'objet {row['nom']} n'est pas valide : {row['x0']}. La valeur doit être positive.")       

        if row["y0"] < 0:
            erreurs.append(f" la valeur de 'y0' pour l'objet {row['nom']} n'est pas valide : {row['y0']}. La valeur doit être positive.")   
        
        if row["vx0"] < 0:
            erreurs.append(f" la valeur de 'vx0' pour l'objet {row['nom']} n'est pas valide : {row['vx0']}. La valeur doit être positive.") 

        if row["vy0"] < 0:
            erreurs.append(f" la valeur de 'vy0' pour l'objet {row['nom']} n'est pas valide : {row['vy0']}. La valeur doit être positive.")

        if row["parent"] not in df["nom"].values and row["parent"] is not None:
            erreurs.append(f" la valeur de 'parent' pour l'objet {row['nom']} n'est pas valide : {row['parent']}. La valeur doit être le nom d'un autre objet ou None.")

    return erreurs
        
