from Projectile import Projectile 
from Astre_Fixe import Astre_Fixe

G = 6.67430e-11
MT_EN_KG = 5.9722e24
JOUR_EN_S = 86400
UA_EN_KM = 149507870700

from math import sin, cos, tanh, radians 

def prochaine_pos_vit_du_projectile(pos_projectile: list[float], dt: float, vitesse_proj: list[float], liste_astre: list[Astre_Fixe]): 
    """_Calcule la prochaine vitesse que aura le projectile ainsi que sa prochaine position_
    
    Args:
        pos_projectile (list[float]): _la position x et y du projectille à ce moment (en UA)_
        dt (float): _pas de temps (en j)_
        vitesse_proj (list[float]): _vitesse x et y du projectille (en UA/j)_
        liste_astre (list[Astre_Fixe]): _liste qui contien tout les astres fixes du systeme_
    
    Returns:
        _types_ (new_pos, new_vit) : 
            _new_pos_ -> _nouvelle position x et y du projectille (en UA)_
            
            _new_vit_ -> _nouvelle vitesse x et y du projectille (en UA/j)_
    """ 
    
    ax, ay = 0,0

    for astre in liste_astre:
        distance_entre_eux = (pos_projectile[0] - astre.position[0], pos_projectile[1] - astre.position[1])
        
        # Trouve l'angle entre l'astre et le projectille
        angle_rad = 0 if distance_entre_eux[1] < 0 else radians(180)
        if not distance_entre_eux[0] == 0:
            angle_rad = radians(tanh(distance_entre_eux[1] / distance_entre_eux[0]))    

        # Calcule la acceleration avec l'equation Fg = Gm1m2/d**2 et a = F/m2
        a = -(G * JOUR_EN_S * MT_EN_KG / UA_EN_KM) * astre.masse / ((distance_entre_eux[0])**2 + (distance_entre_eux[1])**2)
        ax, ay += a*cos(angle_rad), a*sin(angle_rad) 
    
    # Calcule nouvelle vitesse et la nouvelle position 
    new_vx, new_vy = vitesse_proj[0] + dt * ax, vitesse_proj[1] + dt * ay
    new_pos_x, new_pos_y = pos_projectile[0] + vitesse_proj[0] * dt + 0.5 * ax * dt**2, pos_projectile[1] + vitesse_proj[0] * dt + 0.5 * ay * dt**2

    return (new_pos_x, new_pos_y), (new_vx, new_vy)



###
###### a continuer 
###
def creer_liste_position_du_projectile(proj: Projectile, liste_astre: list[Astre_Fixe], dt: float, t_final: float):
    # creer une liste de position uqe le projectile a fait
    pos = proj.pos0
    vit = proj.vit0

    liste_position = [pos]
    for _ in range(t_final//dt + (0 if t_final%dt != 0 else + 1)):       
        
        if est_en_contacte(pos, liste_astre) != None:
            
            return # retourne letat je pense et que c la fin 
            
        pos, vit = prochaine_pos_vit_du_projectile(pos, dt, vit, liste_astre)
        




def est_en_contacte(pos: list[float], liste_astre: list[Astre_Fixe]):
    
    """_verifi s'il est en contact ou non_

    Returns:
        _type_: _l'index de lastre toucher ou None sil y ne a pas_
    """    
    
    """ _ return l'index de lastre toucher ou None sil y ne a pas_ """
    for index_astre in range(len(liste_astre)):
        
        astre = liste_astre[index_astre]
        
        # determine le rayon a la deux de la distance entre lastre et le projectile avec pytagore
        distance_entre_eux = (pos[0] - astre.position[0]) ** 2 + (pos[1] - astre.position[1]) ** 2
        rayon_astre = astre.rayon[0] ** 2 + astre.rayon[1]** 2    
        
        if distance_entre_eux < rayon_astre:
            return index_astre ## devrais renvoyer lastre toucher
    return None


###
###### surement a delete
###

def force_g_kelper(projectile: Projectile, astre_Fixe: Astre_Fixe):  
    """ Calcule la force entre le projectile et lastre fixe donnee avec l'equation Fg = Gm1m2/d**2

    Args:
        projectile (Projectile): l'objet projectile lancer
        astre_Fixe (Astre_Fixe): 

    Returns:
        _type_: _description_
    """    ''' '''

    G = 6.67430e-11
    MT = 5.9722e24
    jour = 86400
    UA = 149507870700

    new_g_with_mesure = G * jour * MT / UA
    return new_g_with_mesure * projectile.masse * astre_Fixe.masse / ((projectile.position[0] - astre_Fixe.position[0])**2 + (projectile.position[1] - astre_Fixe.position[1])**2)
