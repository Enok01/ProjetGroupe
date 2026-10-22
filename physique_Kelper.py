from Projectile import Projectile 
from Astre_Fixe import Astre_Fixe

from math import sin, cos, tanh, radians 

def prochaine_vitesse_du_projectile(pos_projectile: list[int], dt: float, vitesse_proj: list[float], liste_astre: list[Astre_Fixe]): 
    """_summary_

    Args:
        pos_projectile (list[int]): _la position du projectille a ce moment_
        dt (float): _description_
        vitesse_proj (list[float]): _description_
        liste_astre (list[Astre_Fixe]): _description_

    Returns:
        _type_: _description_
    """ 

    ax, ay = 0,0

    for astre in liste_astre:

        distance_entre_eux = (pos_projectile[0] - astre.position[0], pos_projectile[1] - astre.position[1])
        
        # trouve l'angle entre l'astre et le projectille
        angle_rad = 0 if distance_entre_eux[1] < 0 else radians(180)
        if not distance_entre_eux[0] == 0:
            angle_rad = radians(tanh(distance_entre_eux[1] / distance_entre_eux[0]))    

        #Calcule la acceleration entre le projectile et l'astre donnee avec l'equation Fg = Gm1m2/d**2 et a = F/m2
        G = 6.67430e-11
        MT = 5.9722e24
        jour = 86400
        UA = 149507870700
        new_g_with_mesure = G * jour * MT / UA
        a = -new_g_with_mesure * astre.masse / ((distance_entre_eux[0])**2 + (distance_entre_eux[1])**2)
        ax, ay += a*cos(angle_rad), a*sin(angle_rad) 
    
    new_vx, new_vy = vitesse_proj[0] + dt * ax, vitesse_proj[1] + dt * ay
    new_pos_x, new_pos_y = pos_projectile[0] + vitesse_proj[0] * dt + 0.5 * ax * dt**2, pos_projectile[1] + vitesse_proj[0] * dt + 0.5 * ay * dt**2

    return (new_pos_x, new_pos_y), (new_vx, new_vy)

