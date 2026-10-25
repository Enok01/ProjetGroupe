from projectile import Projectile 
from astre import AstreFixe 

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
        _tuple_ (new_pos, new_vit) : 
            _new_pos_ -> _nouvelle position x et y du projectille (en UA)_
            
            _new_vit_ -> _nouvelle vitesse x et y du projectille (en UA/j)_
    """ 
    
    ax, ay = 0, 0

    for astre in liste_astre:
        
        astre_position = astre.position(t)
        
        dx = astre_position[0] - pos[0]
        dy = astre_position[1] - pos[1]
        
        
        # cree des vecteurs unitere
        distance = np.sqrt(dx**2 + dy**2)
        ux = dx / distance 
        uy = dy / distance
        
        

        # Calcule la acceleration avec l'equation Fg = Gm1m2/d**2 et a = F/m2
        a = (G * JOUR_EN_S**2 * MT_EN_KG / UA_EN_M ** 3) * astre.masse / distance**2
        
        if astre.nom == "Soleil" and (distance - 1) < 0.001:
            print("acceleration solaire =", a)
        
        ax += a * ux
        ay += a * uy
        #print(
        #            "t=", t,
        #            "r=", distance,
        #            "a=", a
        #)
        
    # Calcule nouvelle vitesse et la nouvelle position 
    new_vx, new_vy = v[0] + dt * ax, v[1] + dt * ay
    new_pos_x, new_pos_y = pos[0] + v[0] * dt + 0.5 * ax * dt**2, pos[1] + v[1] * dt + 0.5 * ay * dt**2

    return (new_pos_x, new_pos_y), (new_vx, new_vy)


def creer_liste_pos_vit_du_projectile(p: Projectile, liste_astre: list[AstreFixe], dt: float, t_final: float) -> AstreFixe:
    """_Creer la liste dans _historique_ du projectile mis en parametre__

    Args:
        p (Projectile): _Projectille utiliser_
        liste_astre (list[AstreFixe]): _tout les astres fixes_
        dt (float): _pas de temps (en jour)_
        t_final (float): _temps final pour le projectile (en jour)_

    Returns:
        AstreFixe : _l'astre fixe toucher ou, sil na rien toucher, None_
    """ 
    
    
    # determine la longueur maximal
    d = {astre:astre.distance for astre in liste_astre}
    astre_loin = max(d, key=d.get)
    distance_max = astre_loin.distance + 2 * astre_loin.rayon


    vx, vy = astre_loin.vitesse(0)
    
    vitesse = np.sqrt(vx**2 + vy**2)
    
    
    
    temps_max = distance_max/vitesse if True else 0
    distance_max
    print(distance_max,'chose \n')
    

    # distance max 
    # temps max t*2
    
    
     
    # creer une liste de position uqe le projectile a fait
    pos = p.pos0
    vit = p.vit0
    t = 0

    for _ in range(int(t_final//dt) + (0 if t_final%dt != 0 else + 1)):
        
        

        new_pos, new_vit = prochaine_pos_vit(pos, liste_astre, dt, t, vit)
        #print("distance terre =",
        #    np.sqrt(
        #     (pos[0]-terre.position(t)[0])**2 +
        #     (pos[1]-terre.position(t)[1])**2
        # ), ", position -> ", pos)
        
        contacte = est_en_contacte(pos, new_pos, liste_astre, t)
        
        if contacte != None:
            return contacte
        # ajoute la position a la liste
        p.ajouter_etat(new_pos, new_vit)
        
        pos, vit = new_pos, new_vit
        t += dt
    return None
        

def est_en_contacte(pos: list[float],new_pos: list[float], liste_astre: list[AstreFixe], t: float) -> AstreFixe:
    """_verifi s'il est en contact ou non_

    Args:
        pos (list[float]): _la position x et y du projectille au moment presedant (en UA)_
        new_pos (list[float]): _la nouvelle position x et y du projectille maintenent (en UA)_
        liste_astre (list[AstreFixe]): _tout les astres fixes_
        t (float): _temps rendu (en jour)_

    Returns:
        AstreFixe: _L'astre toucher ou None s'il ne touche rien_
    """         
    
    # trouvons la fonction y = ax + b qui relis _pos_ et _new_pos_
    
    a = (new_pos[1] - pos[1]) / (new_pos[0] - pos[0])
    b = new_pos[1] - a * new_pos[0]
    
    
    for astre in liste_astre:
        
        
        astre_position = astre.position(t)
        
        # 1- trouvons l'equation du cercle pour lastre                   -> (x - astre.position(t)[0])**2 + (y - astre.position(t)[1] )**2 = r**2
        # 2- ensuite nous allons remplacer le y dans lequation
        # du cercle pour la fonction du des deux point                -> (x - astre.position(t)[0])**2 + (ax + b - astre.position(t)[1] )**2 = r**2
        # 3- avec des simplifications, nous avons                   -> (a**2 + 1)*x**2 + (2*a*b)*x + b**2 - r**2 = 0 
        # 4- Par la formule quadratique (b**2 -4*a*c)                             ->''';';'lk'kzsjdf;zlk ERROR !!!!!!!!! delta = (2*a*b)**2 - 4 * (a**2 + 1) * (b**2 - r**2)
        
        A = #a faire sur tablette!!
        
        B = 
        
        C = 
        
        
        delta = (2*a*b) **2 - 4*(a**2 +1)*(b**2-astre.rayon**2)!!!!!!
        
        
        if delta < 0:
            continue
        
        # 5- par la formule quadratique                             ->  (x = (-b +_ sqrt(delta)) / (2*a))
        x1, x2 = float((-b + np.sqrt(delta)) / (2*a)), float((-b - np.sqrt(delta)) / (2*a))
        
        # 6- par lequation des deux point                            -> (y = ax + b)
        y1, y2 = float(a*x1 + b), float(a*x2 + b)
        
        xmax = pos[0] if pos[0] >= new_pos[0] else new_pos[0]
        xmin = pos[0] if pos[0] < new_pos[0] else new_pos[0]
        ymax = pos[1] if pos[1] >= new_pos[1] else new_pos[1]
        ymin = pos[1] if pos[1] < new_pos[1] else new_pos[1]
    
        condition1 = ( xmin < x1 and x1 <= xmax) and (ymin < y1 and y1 <= ymax)
        condition2 = ( xmin < x2 and x2 <= xmax) and (ymin < y2 and y2 <= ymax)
        
        print(condition1, ' et ' , condition2)
    
        if condition1 or condition2:
            return astre
        
        
        
        
        
        
        
        # a partir de lequation dun cercle (x**2 + y**2 = r**2) trouvons 
        
        
        
        
        
        
        
        
        
        
        # determine le rayon a la deux de la distance entre lastre et le projectile avec pytagore
        #distance_entre_eux2 = (pos[0] - astre_position[0]) ** 2 + (pos[1] - astre_position[1]) ** 2
        #rayon_astre2 = astre.rayon ** 2     
        
        #if distance_entre_eux2 < rayon_astre2:
        #    return astre 
    return None












import numpy as np


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
    vit0=[-1,0],
    temps_apparition=0,
    duree_vie=1000
)


## cree les listes
impact = creer_liste_pos_vit_du_projectile(
    projectile,
    [soleil, terre],
    dt=0.05,
    t_final=400
)

print("\n------- RESULTAT --------")

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

y_terre = [terre.position(i)[1] for i in range(int(366))] 

x_soleil = [soleil.position(i)[0] for i in range(int(366))] 

y_soleil = [soleil.position(i)[1] for i in range(int(366))] 

plt.plot(x,y, 'o--', color = 'm', label= projectile.nom)

plt.plot(x_terre, y_terre, "o-.", color = 'g', label= terre.nom)
plt.plot(x_soleil, y_soleil, "o-.", color ='y', label= soleil.nom)
plt.legend()

plt.show()
