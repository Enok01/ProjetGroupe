class HorsSystemeError(Exception):
    """_Exception si le projectile est hors du systeme_"""    
    def __init__(self, message):
        super().__init__(message)

class TempsMaximumAtteinte(Exception):
    """_Exception si le temps maximum a ete atteinte_"""    
    def __init__(self, message):
        super().__init__(message)
    