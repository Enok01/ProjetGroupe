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
    
    # Vérifier que toutes les colonnes attendues sont présentes
    colonnes_manquantes = [col for col in COLONNES_tous if col not in df.columns] # met les colonnes pour lesquelles il n'y a pas de correspondance dans le fichier CSV: je vous invite a bien verifier que les noms de colonnes dans le CSV correspondent exactement à ceux attendus, y compris la casse et les espaces.je suis pas le meilleur pour les compreantion :)
    if colonnes_manquantes:
        raise ValueError(f"le fichier {fichier} ne contient pas les colonnes attendues : {colonnes_manquantes}")
    
    return df

