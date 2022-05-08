from Exceptions import CombinaisonError

import pycuber as pc
import random
import kociemba

# Les 18 actions possibles sur un cube (convention internationale)
ACTION_LIST = ["F", "B", "L", "R", "D", "U", "F'", "R'", "U'", "L'", "B'", "D'", "L2", "D2", "B2", "R2", "U2", "F2"]

def gen_formula(nb_step:int=24) -> pc.Formula:
    """
    Génère une formule de mélange du cube aléatoire.
    Paramètres:     nb_step (int) = nombre d'étapes de mélange
    Retourne:       (pc.Formula) = formule de mélange
    """
    # On prend 24 en valeur par défaut ; 20 étant le "nombre de Dieu" d'un Rubik's Cube.
    return pc.Formula([random.choice(ACTION_LIST) for _ in range(nb_step)])

def convert_to_matrix(cube:pc.Cube) -> list:
    """
    Convertit un cube en matrice.
    Paramètres:     cube (pc.Cube) = objet cube (comprend celui du fichier __init__.py par héritage)
    Retourne:       (list) = représentation en liste de matrices d'un cube.
    """
    index = {"L": cube.L, "U": cube.U, "F": cube.F, "D": cube.D, "R": cube.R, "B": cube.B}
    m = []
    m.append(list())
    for i in range(3):
        m[-1].append([get_value(square) for square in index["U"][i]])
    for _ in range(4):
        m.append(list())
    for i in range(3):
        j = 1
        for side in "LFRB":
            m[j].append([get_value(square) for square in index[side][i]])
            j += 1
    m.append(list())
    for i in range(3):
        m[-1].append([get_value(square) for square in index["D"][i]])
    return m

def copy_3by3(mat:list) -> list:
    """
    Copie profonde d'une liste de matrices carrées d'ordre 3.
    Paramètres:     mat (list) = liste de matrices carrées d'ordre 3.
    Retourne:       (list) = copie de mat.
    """
    return [[[mat[i][j][k] for k in range(len(mat[i][j]))] for j in range(len(mat[i]))] for i in range(len(mat))]

def get_value(square:pc.Square) -> str:
    """
    Retourne la couleur d'une case modélisée par pycuber.
    Paramètres:     square (pc.Square) = case pycuber.
    Retourne:       (str) = caractère représentant la couleur de la case.
    """
    return {
        "red": "r",
        "yellow": "y",
        "green": "g",
        "white": "w",
        "orange": "o",
        "blue": "b",
        "unknown": "u",
    }[square.colour]

def get_k_string(m:list) -> str:
    """
    Transforme la représentation en matrice d'un cube en chaîne de caractères compatible avec la librairie kociemba.
    Paramètres:     m (list) = représentation en liste de matrices d'un cube
    Retourne:       (str) = chaîne de représentation d'un cube avec kociemba.
    """
    d = []
    for face in m:
        d.append(list())
        for row in face:
            d[-1].append(str().join(row)) # liste en chaîne
    d_transfo = [d[0],d[3],d[2],d[5],d[1],d[4]] # réorganisation faces
    f = []
    for face in d_transfo:
        f.append(str().join(face)) # liste en chaîne
    return str().join(f) \
                .replace('y', 'U') \
                .replace('r', 'L') \
                .replace('g', 'F') \
                .replace('o', 'R') \
                .replace('b', 'B') \
                .replace('w', 'D') # remplacement avec convention de la librairie

def get_formula_to_solve(mtx:list) -> str:
    """
    Obtient la formule de résolution d'un cube.
    Paramètres:     mtx (list) = représentation en liste de matrices d'un cube
    Retourne:       (str) = formule de résolution
    """
    k = get_k_string(mtx)
    try:
        s = kociemba.solve(k)
    except ValueError:
        raise CombinaisonError("Le cube saisi n'est pas valide")
    else:
        return s+" " # pour fomattage