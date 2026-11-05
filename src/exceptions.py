class HorsSystemeError(Exception):
    """_Exception si le projectile est hors du systeme_"""    
    def __init__(self, message):
        super().__init__(message)

class TempsMaximumAtteinte(Exception):
    """_Exception si le temps maximum a ete atteinte_"""    
    def __init__(self, message):
        super().__init__(message)

class DebutHistorique(Exception):
    """Exception si le temps du pas est plus petit que le temps d'apparitions"""
    def __init__(self, message):
        super().__init__(message)

class FinHistorique(Exception):
    """Exception si le temps du pas est plus grand que le temps d'apparitions"""
    def __init__(self, message):
        super().__init__(message)