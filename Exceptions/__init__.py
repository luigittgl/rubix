"""
Définit les exceptions propres à Rubix.
"""

class CameraError(Exception):
    """
    Problème de lecture de caméra.
    """
    pass

class CombinaisonError(Exception):
    """
    Rubik's cube non valide.
    """
    pass