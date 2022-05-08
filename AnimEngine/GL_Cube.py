"""
Code publié par Rabbit76 le 01/03/2019 à 8h23 à l'adresse suivante :
https://stackoverflow.com/questions/50303616/how-to-rotate-slices-of-a-rubiks-cube-in-python-pyopengl

Code sous licence CC BY-SA 4.0, conformément à la section 6 des termes de service de StackOverFlow en vigueur depuis le 02/05/2018.
De larges modifications ont été apportées au code, dans le respect des termes de la licence.

Depuis le 08/10/2015, les contributions aux adaptations de code sous licence CC BY-SA 4.0 sont licenciables sous licence GPLv3, comme le préconisent les "Trophées NSI".
Le code ci-dessous, sous licence CC BY-SA 4.0, est donc compatible unilatéralement avec GPLv3.

Voir :
 - https://creativecommons.org/licenses/by-sa/4.0/
 - https://stackoverflow.com/legal/terms-of-service#licensing
 - https://creativecommons.org/share-your-work/licensing-considerations/compatible-licenses

Nous remercions Rabbit76 pour sa contribution.
"""

from OpenGL.GL import *
from OpenGL.GLU import *

#Données de représentation 3D d'un cube
edges = ((0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),(5,1),(5,4),(5,7))
surfaces = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))
vertices = (( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), (-1, -1, -1),
( 1, -1,  1), ( 1,  1,  1), (-1, -1,  1), (-1,  1,  1))
colors = ((1, 0, 0), (0, 1, 0), (1, 0.5, 0), (1, 1, 0), (1, 1, 1), (0, 0, 1))

class Cube():
    """
    Classe modélisant un cube unique en 3D
    """
    def __init__(self, id:int, scale:float) -> None:
        """
        Instancie un objet Cube.
        Paramètres:     id (int) = identifiant du cube.
                        scale (float) = taille dans l'espace 3D.
        Retourne:       rien.
        """
        self.scale = scale
        self.init_i = [*id]
        self.current_i = [*id]
        self.rot = [[1 if i==j else 0 for i in range(3)] for j in range(3)]
        self._colors = colors

    def isAffected(self, axis:int, slice:int) -> None:
        """
        Renvoie True si le cube est affecté à un axe
        Paramètres:     axis (int) = axe.
                        slice (int) = tranche en animation.
        Retourne:       (bool) = True si le cube est affecté à un axe, False sinon.
        """
        return self.current_i[axis] == slice

    def get_position(self) -> list:
        """
        Renvoie l'index position du cube.
        Paramètres:     aucun.
        Retourne:       (list) = index position du cube.
        """
        return self.current_i

    def update(self, axis:int, slice:int, dir:int) -> None:
        """
        Mise à jour du cube et rotation.
        Paramètres:     axis (int) = axe de rotation
                        slice (int) = tranche en animation
                        dir (int) = sens de rotation (1 ou -1)
        Retourne:       rien.
        """
        if not self.isAffected(axis, slice):
            return
        i, j = (axis+1) % 3, (axis+2) % 3
        for k in range(3):
            self.rot[k][i], self.rot[k][j] = -self.rot[k][j]*dir, self.rot[k][i]*dir
        self.current_i[i], self.current_i[j] = (
            self.current_i[j] if dir < 0 else 3 - 1 - self.current_i[j],
            self.current_i[i] if dir > 0 else 3 - 1 - self.current_i[i] )

    def transformMat(self) -> list:
        """
        Rotation du cube.
        Paramètres:     aucun.
        Retourne:       (list) = matrice des transformations
        """
        scaleA = [[s*self.scale for s in a] for a in self.rot]  
        scaleT = [(p-(3-1)/2)*2.1*self.scale for p in self.current_i] 
        return [*scaleA[0], 0, *scaleA[1], 0, *scaleA[2], 0, *scaleT, 1]

    def set_color(self, _colors:list[tuple[float|int]]) -> None:
        """
        Change la couleur d'un cube.
        Paramètres:     _colors (list[tuple[float|int]]) = liste des tuples des nouvelles couleurs
                        Exemple :  ((1, 0, 0), (0, 1, 0), (1, 0.5, 0), (1, 1, 0), (1, 1, 1), (0, 0, 1))
        Retourne:       rien.
        """
        self._colors = _colors

    def get_color(self) -> tuple[tuple]:
        """
        Renvoie le tuple couleur du cube
        Paramètres:     aucun.
        Retourne:       (tuple[tuple]) = couleurs du cube.
        """
        return self._colors

    def draw(self, surf:tuple[tuple], animate:bool, angle:float, axis:int, slice:int, dir:int) -> None:
        """
        Dessine le cube avec OpenGL.
        Paramètres:     surf (tuple[tuple]) = surfaces du cube
                        animate (bool) = rotation du cube
                        angle (float) = angle de rotation d'une tranche
                        axis (int) = axe de rotation
                        slice (int) = tranche en animation
                        dir (int) = sens de rotation (1 ou -1)
        Retourne:       rien.
        """
        glPushMatrix()
        if animate and self.isAffected(axis, slice):
            glRotatef(angle*dir, *[1 if i==axis else 0 for i in range(3)])
        glMultMatrixf(self.transformMat())
        glBegin(GL_QUADS)
        for i in range(len(surf)):
            glColor3fv(self._colors[i])
            for j in surf[i]:
                glVertex3fv(vertices[j])
        glEnd()
        glPopMatrix()