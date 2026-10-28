from projectile import Projectile 
from astre import AstreFixe 
from exceptions import (HorsSystemeError, TempsMaximumAtteinte)

import numpy as np

import matplotlib.pyplot as plt

G = 6.67430e-11
MT_EN_KG = 5.9722e24
JOUR_EN_S = 86400
UA_EN_M = 149507870700

def prochaine_pos_vit(pos: list[float], liste_astre: list[AstreFixe], dt: float, t:float, v: list[float]) -> tuple[tuple]: 
    """_Calcule la prochaine vitesse que aura le projectile ainsi que sa prochaine position_
    
    Args:
        pos (list[float]): _la position x et y du projectille à ce moment (en UA)_
        liste_astre (list[AstreFixe]): _liste qui contien tout les astres fixes du systeme_
        dt (float): _pas de temps (en j)_
        t (float): _temps rendu (en j)_
        v (list[float]): _vitesse x et y du projectille (en UA/j)_
    
    Returns:
        _tuple_ (new_pos, new_vit, dt_moment) : 
            _new_pos_ -> _nouvelle position x et y du projectille (en UA)_
            
            _new_vit_ -> _nouvelle vitesse x et y du projectille (en UA/j)_
            
            
    """ 
    #_dt_moment_ -> _le pas selon la distance de lastre la plus proche et le projectile et lacceleration (en j)_
    
    
    a = np.array([0.0, 0.0])
    
    astres_position_masse = [[astre.position(t), astre.masse] for astre in liste_astre]

    for astre_position_masse in astres_position_masse:
        
        astre_position = astre_position_masse[0]
        astre_masse = astre_position_masse[1]
        
        vecteur_astre_projectile = astre_position - pos  
        
        distance = np.linalg.norm(vecteur_astre_projectile) 
        if distance < 1e-12: # Pour eviter les divisions par 0
            continue
        
        # cree des vecteurs unitaire
        vect_unitaire = vecteur_astre_projectile / distance
        
        # Calcule la acceleration avec l'equation Fg = Gm1m2/d**2 et a = F/m1, qui combiner ensemble : G * m2/d**2 
        a_astre = (G * JOUR_EN_S**2 * MT_EN_KG / UA_EN_M ** 3) *  astre_masse/ distance**2
        a += vect_unitaire * a_astre
        
    # Calcule nouvelle vitesse et la nouvelle position 
    new_v = v + dt * a 
    new_pos = pos + v*dt + 0.5*a*dt**2 
    
    return new_pos, new_v 


def creer_liste_pos_vit_du_projectile(p: Projectile, liste_astre: list[AstreFixe], dt: float = 0.01, temps_maximum: int = 3650 ) -> AstreFixe:
    """_Cree la trajectoire du projectile en calculant sa position et sa vitesse sous les graviter des astre du systeme.
        Les etats calculer sont enregistrer dans l'historique du projectile._

    Args:
        p (Projectile): _Projectille utiliser_
        liste_astre (list[AstreFixe]): _Toutes les astres fixes_
        dt (float, optional): _pas de temps entre les positions (en jour)_. Defaults to 0.01 (recomander pour la presision).
        nombre_diteration_max (int, optional): _nombre de position calculer maximum_. Defaults est de 3650 jour (10 ans).

    Returns:
        AstreFixe: _l'astre fixe toucher ou, sil na rien toucher, None_
    """ 
    
    # determine la longueur maximal pour arreter la creation de la liste
    DISTANCE_MAX_AJOUTER = 2
    astre_loin = max(liste_astre, key= lambda astre: astre.distance)
    distance_max = astre_loin.distance + DISTANCE_MAX_AJOUTER
    
    # creer une liste de position uqe le projectile a fait
    pos = p.pos0
    vit = p.vit0
    t = 0 # en jour
    nombre_diteration_max = int(temps_maximum * 1/dt)
    
    for i in range(nombre_diteration_max):
        
        new_pos, new_vit = prochaine_pos_vit(pos, liste_astre, dt, t, vit)  # , dt_moment
        
        t += dt
        contacte, new_pos = est_en_contacte(pos, new_pos, p, liste_astre, t)
        
        if contacte != None:
            p.ajouter_etat(new_pos, new_vit) # TODO #temporaire 
            return contacte
        
        if np.linalg.norm(new_pos) > distance_max:    
            raise HorsSystemeError('Le projectile est hors du systeme.')
        
        NB_ITERATIONS_ENREGISTREMENT = int(1/dt)
        
        if i%NB_ITERATIONS_ENREGISTREMENT == 0:
            p.ajouter_etat(new_pos, new_vit)
        
        
        pos, vit = new_pos, new_vit
        
    raise TempsMaximumAtteinte('Le nombre')
        

def est_en_contacte(pos: list[float], new_pos: list[float], p: Projectile,  liste_astre: list[AstreFixe], t: float) -> AstreFixe:
    """_Verifi s'il est en contact ou non en calculant si la trajectoire des deux points ont des points avec lastre le plus proche_

    Args:
        pos (list[float]): _la position x et y du projectille au moment presedant (en UA)_
        new_pos (list[float]): _la nouvelle position x et y du projectille maintenent (en UA)_
        p (Prokectile): _projectile utiliser_
        liste_astre (list[AstreFixe]): _tout les astres fixes_
        t (float): _temps rendu (en jour)_

    Returns:
        AstreFixe, (x, y): _L'astre toucher et la position ou elle a toucher ou None s'il ne touche rien_
    """         
    
    # Trouver l'astre le plus proche du projectile
    #astre_proche = min(liste_astre, key= lambda astre: np.linalg.norm(astre.position(t) - new_pos)) 
    distance_min = float('inf')
    astre_proche = None
    astre_position = None 
    
    for astre in liste_astre:
        pos_astre = astre.position(t)
        dx, dy = pos_astre - pos
        d2 = dx*dx + dy*dy
        
        if d2<distance_min:
            distance_min = d2
            astre_proche = astre
            astre_position = pos_astre
    
    
    rayon_max = astre_proche.rayon + p.rayon
    
    
    if abs(new_pos[0] - pos[0]) < 1e-12:       # si division par 0
        return None, new_pos
    
    # trouvons la fonction f(x) = ax + b qui relis _pos_ et _new_pos_
    a = (new_pos[1] - pos[1]) / (new_pos[0] - pos[0])
    b = pos[1] - a * pos[0]    
    
        
    # 1- trouvons l'equation du cercle pour lastre                      -> (x - astre_position[0])**2 + (y - astre_position[1] )**2 = r**2
    # 2- ensuite nous allons remplacer le y dans lequation
    # du cercle pour la fct f(x)                                        -> (x - astre_position[0])**2 + (ax + b - astre_position[1] )**2 = r**2
    # 3- avec des simplifications, nous avons                           -> (1+a**2)*x**2 + (2*a*b - 2*astre_position[0] - 2*a*astre_position[1])*x + (astre_position[0]**2 + astre_position[1]**2 + b**2 - 2*b*astre_position[1] - r**2) = 0
    A = 1 + a**2        
    B = 2*a*b - 2*astre_position[0] - 2*a*astre_position[1]
    C = astre_position[0]**2 + astre_position[1]**2 + b**2 - 2*b*astre_position[1] - rayon_max**2
        
    # 4- Par la formule du discriminant                                 -> discriminant = B**2 - 4AC
    discriminant = (B)**2 - 4*(A)*(C)
    
    # Les tangences produisent parfois des faux positifs
    # à cause des trajectoires quasi verticales.
    if discriminant <= 0:
        return None, new_pos

    # 5- par la formule quadratique                                     ->  (x = (-B +_ sqrt(discriminant)) / (2*A))
    x1, x2 = float((-B + np.sqrt(discriminant)) / (2*A)), float((-B - np.sqrt(discriminant)) / (2*A))
        
    # 6- par lequation f(x)                                             -> (f(x) = ax + b)
    y1, y2 = float(a*x1 + b), float(a*x2 + b)    

    # 7- Calcule le rectangle englobant du segment [pos, new_pos].
    # Une intersection avec le cercle n'est valide que si elle
    # se trouve à l'intérieur de ces bornes.
    xmax, xmin = max(pos[0], new_pos[0]), min(pos[0], new_pos[0]) #(pos[0], new_pos[0]) if pos[0] >= new_pos[0] else (new_pos[0], pos[0])
    ymax, ymin = max(pos[1], new_pos[1]), min(pos[1], new_pos[1]) # if pos[1] >= new_pos[1] else (new_pos[1], pos[1])
        
    # 8- regarde si le point passant a f(x) et lequation du cercle est entre les deux positions _pos_ et _new_pos_
    condition1 = max(xmin, min(x1, xmax)) == x1 and max(ymin, min(y1, ymax)) == y1
    condition2 = max(xmin, min(x2, xmax)) == x2 and max(ymin, min(y2, ymax)) == y2
    
    if condition1:
        return astre_proche, (x1, y1)
                
    elif condition2:
        return astre_proche, (x2, y2) # pourrais update la derniere position # TODO sa se peux que non car le temps doit etre pile :(
    
    
    
    
    # a partir de lequation dun cercle (x**2 + y**2 = r**2) trouvons 
    
    
    
    # determine le rayon a la deux de la distance entre lastre et le projectile avec pytagore
    #distance_entre_eux2 = (pos[0] - astre_position[0]) ** 2 + (pos[1] - astre_position[1]) ** 2
    #rayon_astre2 = rayon_contacte ** 2     
    
    #if distance_entre_eux2 < rayon_astre2:
    #    return astre 
    return None, new_pos











# Creation des astres
soleil = AstreFixe(
    nom="Soleil",
    masse=333000,
    couleur="jaune",
    taille=20,
    rayon=0.005,
    distance=0,
    periode=0
)

terre = AstreFixe(
    nom="Terre",
    masse=1,
    couleur="bleu",
    taille=8,
    rayon=0.00005,
    distance=1.0,
    periode=365.25
)

# ==========================
# Position de départ
# ==========================

pos_terre = terre.position(0)

# Décale le projectile juste en dehors de la Terre
direction = pos_terre / np.linalg.norm(pos_terre)

pos_depart = pos_terre + direction * terre.rayon * 2
vit_terre = -terre.vitesse(0)

# Projectil
projectile = Projectile(
    nom="Meteor",
    masse=0.001,
    couleur="red",
    taille=3,
    rayon=0.00001,
    pos0=pos_depart,
    vit0=[0.01,0.01],
    temps_apparition=0,
    duree_vie=1000
)

impact = None

## cree les listes
'''import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
'''

try:
    impact = creer_liste_pos_vit_du_projectile(
        projectile,
        [soleil, terre],
    )
except:
    print("ok")
'''
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(20)  # les 20 fonctions les plus coûteuses
'''
if impact is None:
    print("aucun impact")
else:
    print(f"impact sur : {impact.nom}")

print(f"nombre detats : {len(projectile.historique)}")

print("\netat initial :")
print(projectile.historique[0])

print("\netat final :")
print(projectile.historique[-1])


x = [position[0] for position in projectile.historique]
y = [position[1] for position in projectile.historique]

x_terre = [terre.position(i)[0] for i in range(int(366))] 

x_rond = []
for pos in x_terre:
    x_rond.extend([pos, pos + terre.rayon, pos, pos - terre.rayon])
y_terre = [terre.position(i)[1] for i in range(int(366))] 

y_rond = []
for pos in y_terre:
    y_rond.extend([pos + terre.rayon, pos, pos - terre.rayon, pos])


x_soleil = [soleil.position(i)[0] for i in range(int(366))] 

y_soleil = [soleil.position(i)[1] for i in range(int(366))] 

plt.plot(x,y, 'o--', color = 'm', label= projectile.nom)

plt.plot(x_rond, y_rond, 'o')

plt.plot(x_terre, y_terre, "o-.", color = 'g', label= terre.nom)
plt.plot(x_soleil, y_soleil, "o-.", color ='y', label= soleil.nom)
plt.legend()

plt.show()

