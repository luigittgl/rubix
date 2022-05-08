import Modelisation.Cutils

import pycuber as pc

"""
Module de modélisation d'un Rubik's Cube (mélange, représentation matricielle...)
Cutils : fonctions auxiliaires aux objets Cube
"""

class Cube(pc.Cube):
    """
    Classe modélisant un cube, crée avec la librairie pycuber.
    Hérite de pycuber.Cube.
    """
    def __init__(self) -> None:
        """
        Instancie un objet Cube.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        pc.Cube.__init__(self)
        self.formula = ""
        self.Cube_GL = None # Classe cube de AnimEngine/Cube_Interface.py
    
    def scramble(self) -> None:
        """
        Mélange le cube
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self.formula = Cutils.gen_formula() # génération formule
        self.apply(self.formula)
    
    def apply(self, formula:str|pc.Formula) -> None:
        """
        Applique une formule au cube ; permet + de cohérence dans notation.
        Paramètres:     formula (str) = formule aux conventions internationales.
        Retourne:       rien.
        """
        self(formula)
    
    def get_matrix(self) -> list:
        """
        Obtient la matrice représentant le cube.
        Paramètres:     aucun.
        Retourne:       (list) représentation en liste de matrices du cube.
        """
        return Cutils.convert_to_matrix(self)

    def get_formula_to_solve(self) -> str:
        """
        Obtient la formule permettant de résoudre le cube.
        Paramètres:     aucun.
        Retourne:       (str) formule permettant de résoudre le cube.
        """
        return Cutils.get_formula_to_solve(self.get_matrix())

class CubeByMatrix():
    """
    Classe modélisant un cube, crée avec une représentation en liste de matrices.
    """
    def __init__(self, matrice) -> None:
        """
        Instancie un objet CubeByMatrix.
        Paramètres:     matrice (list) = représentation en liste de matrices du cube.
        Retourne:       rien.
        """
        self.matrix = matrice
        self.Cube_GL = None # Classe cube de AnimEngine/Cube_Interface.py

    def print(self) -> None:
        """
        Affiche le cube.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        print(self.matrix)

    def get_matrix(self) -> list:
        """
        Obtient la matrice représentant le cube.
        Paramètres:     aucun.
        Retourne:       (list) représentation en liste de matrices du cube.
        """
        return self.matrix

    def get_formula_to_solve(self) -> str:
        """
        Obtient la formule permettant de résoudre le cube.
        Paramètres:     aucun.
        Retourne:       (str) formule permettant de résoudre le cube.
        """
        return Cutils.get_formula_to_solve(self.matrix) # formule de résolution