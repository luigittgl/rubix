"""
Regroupe les scripts nécessaires à l'affichage d'un Rubik's Cube en 3D.
__init__.py : contient les fonctions nécessaires à l'intégration des mouvements, de l'affichage  du cube et des entrées au clavier.
GL_Cube.py : contient les éléments permettant le rendu d'un cube sur OpenGL, dont la couleur et le placement.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from AnimEngine.GL_Cube import *
import Musique

class EntireCube():
    """
    Classe qui modélise un Rubik's Cube en 3D.
    """
    def __init__(self, scale:float) -> None:
        """
        Instancie un objet EntireCube.
        Paramètres:     scale (float) = taille dans l'espace 3D.
        Retourne:       rien.
        """
        self.ang_x, self.ang_y,self.ang_z, self.rot_cube = 0, 0, 0, (0, 0, 0)
        self.animate, self.animate_ang, self.animate_speed = False, 0, 5
        self.action = (0, 0, 0)

        self.async_slices_moves = []
        self.index_move = 0
        self.async_sound = False
        self.sound_volume = 1.0
        
        self.camera_mode = "manual"     #(manual,static,animation)
        self.camera_speed = 2.0
        self.anim_mode = 0      #(0=static, 1=x, 2=y, 3=xy, 4=xyz, 5=z)

        #Création des cubes individuels
        self.cubes = [Cube((x, y, z), scale) for x in range(3) for y in range(3) for z in range(3)]

        self.faces = ["U","L","F","R","B","D"]
        self.face_L = [(0,2,0),(0,2,1),(0,2,2),(0,1,0),(0,1,1),(0,1,2),(0,0,0),(0,0,1),(0,0,2)]
        self.face_R = [(2,2,2),(2,2,1),(2,2,0),(2,1,2),(2,1,1),(2,1,0),(2,0,2),(2,0,1),(2,0,0)]
        self.face_F = [(0,2,2),(1,2,2),(2,2,2),(0,1,2),(1,1,2),(2,1,2),(0,0,2),(1,0,2),(2,0,2)]
        self.face_B = [(2,2,0),(1,2,0),(0,2,0),(2,1,0),(1,1,0),(0,1,0),(2,0,0),(1,0,0),(0,0,0)]
        self.face_U = [(0,2,0),(1,2,0),(2,2,0),(0,2,1),(1,2,1),(2,2,1),(0,2,2),(1,2,2),(2,2,2)]
        self.face_D = [(0,0,2),(1,0,2),(2,0,2),(0,0,1),(1,0,1),(2,0,1),(0,0,0),(1,0,0),(2,0,0)]

        self.rot_map = {
            "L": (0, 0, 1), "M": (0, 1, 1), "R'": (0, 2, 1), "D": (1, 0, 1), "E": (1, 1, 1),
            "U'": (1, 2, 1), "B": (2, 0, 1), "S'": (2, 1, 1), "F'": (2, 2, 1),
            "L'": (0, 0, -1), "M'": (0, 1, -1), "R": (0, 2, -1), "D'": (1, 0, -1), "E'": (1, 1, -1),
            "U": (1, 2, -1), "B'": (2, 0, -1), "S": (2, 1, -1), "F": (2, 2, -1)}
        self.rot_cube_map  = { "up": (-1, 0, 0), "down": (1, 0 ,0), "left": (0, -1, 0), "right": (0, 1, 0),
        "ur": (-1, 1, 0),"ul": (-1, -1, 0),"dr": (1, 1, 0),"dl": (1, -1, 0),"stop":(0, 0, 0),"urz":(-1,1,1),"z":(0,0,1)}

    def rotation(self, rotation_key:str) -> int:
        """
        Effectue une rotation de la représentation 3D du Rubik's Cube.
            Tableau des rotations : 
            up, down, left, right, ur, ul, dr, dl, stop
        Paramètres:     rotation_key (str) = nom de la rotation.
        Retourne:       (int) = 0 si l'action a été enregistrée ; -1 si le mouvement est invalide.
        """
        if rotation_key in self.rot_cube_map:
            self.rot_cube = self.rot_cube_map[rotation_key]
            return 0
        else :
            return -1

    def move_slice(self, mouvement:str, animate_speed:int=5, debug:bool=False) -> str|int:
        """
        Fonction asynchrone.
        Effectue un mouvement d'une tranche sur la représentation 3D du Rubik's Cube.
        Tableau des mouvements : 
        L,L',D,D',M,M',E,E',R,R',U,U',B,B',S,S',F,F'
        Paramètres:     mouvement (str) = Nom du mouvement
                        animate_speed (int) = Vitesse du mouvement
                        debug (bool) = Affiche le mouvement réalisé
        Retourne:       (str|int) = mouvement (str), si l'action a été effectué
                                    -1 (int) si une action est déjà en cours, ou le mouvement est invalide
        """
        self.animate_speed = animate_speed
        if not self.animate and mouvement in self.rot_map:
            self.animate = True
            self.action = self.rot_map[mouvement]
            if debug == True :
                print(mouvement)
            return mouvement
        else :
            return -1

    def set_camera_mode(self, mode:str) -> None:
        """
        Change le mode de contrôle de la caméra.
        Modes disponibles : "manual" (touches clavier), "static" (aucun mouvement), "animation" (mode animation)
        Paramètres:     mode (str) = Mode de la caméra. 
        Retourne:       rien.
        """
        self.camera_mode = mode

    def set_animation_mode(self, mode:int, speed:float=2.0) -> None:
        """
        Change l'animation de caméra.
        Paramètres:     mode (int) = 0=static, 1=x, 2=y, 3=xy, 4=xyz, 5=z
                        speed (float) = Vitesse (entre 0.0 et 10.0)s
        Retourne:       rien.
        """
        self.anim_mode = mode
        self.camera_speed = speed

    def play_sequence(self, sequence:list[str], anim_speed:int=2, awaited:bool=True, debug:bool=False, enable_sound:bool=False) -> int:
        """
        Effectue tous les mouvements dans la liste "sequence" à la suite sur la représentation 3D.
        Paramètres:     sequence (list[str]) = Chaîne de mouvements à réaliser
                        anim_speed (int) = Vitesse d'animation
                        awaited (bool) = Détermine si l'execution doit être bloqué jusqu'à la terminaison de la fonction
                        debug (bool) = Affiche le mouvement réalisé
                        enable_sound (bool) = Joue le son correspondant au mouvement
        Retourne:       (int) = 0 si l'action a été effectuée, -1 sinon.
        """
        if awaited == False :
            self.async_slices_moves = sequence
            self.animate_speed = anim_speed+1
            self.async_sound = enable_sound
        else :
            move_table = ["L","L'","D","D'","M","M'","E","E'","R","R'","U","U'","B","B'","S","S'","F","F'","L2","D2","M2","E2","R2","U2","B2","S2","F2"]
            for movement in sequence :
                if movement in move_table :
                    self.move_slice(movement,animate_speed=anim_speed,debug=debug)
                    if enable_sound == True :
                        Musique.mixer.music.set_volume(self.sound_volume)
                        Musique.play_mvt(movement,self.sound_volume)
                    self.tick()
                    while self.animate != False :
                        pygame.display.flip()
                        self.tick()
                else :
                    return -1

    def update_camera_anim(self) -> None:
        """
        Mise à jour du mode de caméra (interne)
        Paramètres:     aucun.
        Retourne:       rien.
        """
        if self.camera_mode == "animation":
            if self.anim_mode == 0:
                self.rotation("stop")
            elif self.anim_mode == 1:
                self.rotation("right")
            elif self.anim_mode == 2: 
                self.rotation("up")
            elif self.anim_mode == 3: 
                self.rotation("ur")
            elif self.anim_mode == 4 : 
                self.rotation("urz")
            elif self.anim_mode == 5 :
                self.rotation("z")

    def update_async_slices(self) -> None:
        """
        Mise à jour des mouvements asynchrones
        Paramètres:     aucun.
        Retourne:       rien.
        """
        if self.async_slices_moves != [] :
            result = self.move_slice(self.async_slices_moves[self.index_move],self.animate_speed)
            if result != -1 and self.index_move <= len(self.async_slices_moves)-1 :
                if self.async_sound == True : 
                    Musique.mixer.music.set_volume(self.sound_volume)
                    Musique.play_mvt(self.async_slices_moves[self.index_move],self.sound_volume)
                self.index_move += 1
            if self.index_move >= len(self.async_slices_moves) :
                self.async_slices_moves = []
                self.index_move = 0 
                self.async_sound = False

    def get_cube_by_location(self, location:tuple[int]) -> Cube:
        """
        Retourne un cube selon la position.
        Paramètres:     location (tuple[int]) = couple position dans le Rubik's Cube
        Retourne:       (GL_Cube.Cube) = objet 3D correspondant au Cube.
        """
        positions = {}
        for i in self.cubes :
            positions[tuple(i.get_position())] = i
        return positions[location]

    def set_entire_color(self, color:tuple[float|int]) -> None:
        """
        Colore entièrement le cube.
        Paramètres:     color (tuple[float|int]) = 0 <= RGB <= 1
        Retourne:       rien.
        """
        for i in self.cubes :
            i.set_color((color,color,color,color,color,color))

    def get_side(self, side:str) -> tuple[list|int]:
        """
        Renvoie la liste des cubes et un identifiant selon la face choisi.
        Paramètres:     side (str) = Face à renvoyer (L-R-F-B-U-D)
        Retourne:       (list, int) = liste des cubes, identifiant
        """
        if side == "R" :    #L
            face = self.face_L
            _id = 1
        elif side == "L" :  #R
            face = self.face_R
            _id = 3
        elif side == "F" :
            face = self.face_F
            _id = 2
        elif side == "B" :
            face = self.face_B
            _id = 0
        elif side == "U" :
            face = self.face_U
            _id = 4
        elif side == "D" :
            face = self.face_D
            _id = 5
        else :
            return -1
        return face,_id

    def color_entire_face(self, side:str, color:tuple[float]=(0.0,1.0,0.0)) -> None:
        """
        Colore une face du cube avec une seule couleur.
        Paramètres:     side (str) = U <=> Dessus, L <=> Gauche, R <=> Droite, B <=> Arrière, F <=> Avant, D <=> Dessous
                        color (tuple[float]) = 0 <= RGB <= 1 
        Retourne:       rien.
        """
        face,_id = self.get_side(side)
        for i in face :
            cube_ = self.get_cube_by_location(i)
            colors = list(cube_.get_color())               
            colors[_id] = color
            cube_.set_color(tuple(colors))      
            
    def color_face(self, side:str, color:list[tuple[float|int]]=[(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0),(0,1,0)]) -> None:
        """
        Colore une face selon une matrice (liste de tuples ici).
        Paramètres:     side (str) = U <=> Dessus, L <=> Gauche, R <=> Droite, B <=> Arrière, F <=> Avant, D <=> Dessous
                        color (list[tuple[float|int]]) =  0 <= RGB <= 1
        Retourne:       rien.
        """
        face,_id = self.get_side(side)
        index=0
        for i in face :
            cube_ = self.get_cube_by_location(i)
            colors = list(cube_.get_color())               
            colors[_id] = color[index]
            cube_.set_color(tuple(colors))  
            index+=1

    def load_color_matrix(self, matrix:list[list[str]]) -> None:
        """
        Lecture d'une matrice représentant un cube.
        Paramètres:     matrix (list[list[str]]) = Matrice à lire
        Retourne:       rien.
        """
        color_dict = {"w":(1,1,1),"b":(0,0,1),"r":(1,0,0),"g":(0,1,0),"y":(1,1,0),"o":(1,0.5,0),"u":(0,0,0)}
        face_index = {0:"U",1:"R",2:"F",3:"L",4:"B",5:"D"}
        for i in range (0,len(matrix)) :
            mtx = matrix[i][0]
            mtx.extend(matrix[i][1])
            mtx.extend(matrix[i][2])
            for x in range(0,len(mtx)) :
                mtx[x] = color_dict[mtx[x]]
            self.color_face(face_index[i],mtx) 

    def set_camera_rotation(self, x_rot:float, y_rot:float, z_rot:float = 0) -> None:
        """
        Mets la rotation de la caméra.
        Paramètres:     x_rot (float) = Rotation sur l'axe x
                        y_rot (float) = Rotation sur l'axe y
                        z_rot (float) = Rotation sur l'axe z (optionnel)
        Retourne:       rien.
        """
        self.ang_x,self.ang_y,self.ang_z = x_rot,y_rot,z_rot
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -40)
        glRotatef(z_rot, 0, 0, 1)
        glRotatef(y_rot, 0, 1, 0)
        glRotatef(x_rot, 1, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    def tick(self) -> None:
        """
        Rafraichissement des fonctions (animations, mouvements...) du cube.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self.update_async_slices()
        self.update_camera_anim()
        self.ang_x += self.rot_cube[0]*self.camera_speed
        self.ang_y += self.rot_cube[1]*self.camera_speed
        self.ang_z += self.rot_cube[2]*self.camera_speed
        self.set_camera_rotation(self.ang_x,self.ang_y,self.ang_z)
        if self.animate:
            if self.animate_ang >= 90:
                for cube in self.cubes:
                    cube.update(*self.action)
                self.animate, self.animate_ang = False, 0
        for cube in self.cubes:
            cube.draw(surfaces,self.animate, self.animate_ang, *self.action)
        if self.animate:
            self.animate_ang += self.animate_speed

rot_cube_map  = {K_UP: "up", K_DOWN: "down", K_LEFT: "left", K_RIGHT: "right"}
rot_keys = {
    K_1: "L", K_2: "M", K_3: "R'", K_4: "D'", K_5: "E",
    K_6: "U'", K_7: "B", K_8: "S'", K_9: "F'",K_F1: "L'", 
    K_F2: "M'", K_F3: "R", K_F4: "D'", K_F5: "E'",
    K_F6: "U", K_F7: "B'", K_F8: "S", K_F9: "F"}  

def init(Debug_:bool=False, fps_:int=60) -> EntireCube:
    """
    Initialise la représentation 3D.
    Paramètres:     Debug (bool) = Option de débug (inactif par défaut)
                    fps_ (int) = Limite de fps (60 par défaut)
    Retourne:       Rubix (EntireCube) = Objet de la représentation 3D initialisé, instance de EntireCube
    """
    global Debug, fps, clock
    Debug = Debug_ # Debug permet de contrôler le cube avec les touches (1,2,3,4,5,6,7,8,9,F1,F2,F3,F4,F5,F6,F7,F8,F9)
    fps = fps_

    #Valeurs par défaut
    Rubix = EntireCube(2)
    Rubix.set_camera_mode("animation")
    Rubix.set_animation_mode(3,0.15)

    Rubix.set_entire_color((1,1,1))
    for i in Rubix.faces :
        Rubix.color_entire_face(i,(1,0,0))
    Rubix.color_entire_face("D",(0,1,0))
    Rubix.color_entire_face("U",(0,1,0))
    Rubix.color_entire_face("L",(0,0,1))
    Rubix.color_entire_face("R",(0,0,1))

    return Rubix

def update(Rubix:EntireCube) -> None: 
    """
    Mise à jour du rendu pour chaque image (actualise Rubix, pygame, et touches de debug si actif)
    Paramètres:     Rubix (EntireCube) = Objet EntireCube.
    Retourne:       rien.
    """
    Rubix.tick()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        #Mouvements avec les touches
        if event.type == KEYDOWN and Debug == True:
            if event.key in rot_keys:
                Rubix.move_slice(rot_keys[event.key],debug=True)

            if event.key in rot_cube_map :
                Rubix.rotation(rot_cube_map[event.key])
        else :
            Rubix.rotation("stop")

    pygame.display.flip()
    clock.tick(fps)

def stop() -> None:
    """
    Arrête l'exécution de pygame.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    pygame.quit()

def initInterface(path_logo:str, name:str) -> None:
    """
    Initialisation des données de l'interface de pygame.
    Paramètres:     path_logo (str) = Chemin du logo.
                    name (str) = nom de la fenêtre.
    Retourne:       rien.
    """
    global WINDOW_NAME, PATH_LOGO
    WINDOW_NAME = name
    PATH_LOGO = path_logo

def main() -> None:
    """
    Initialisation de pygame et OpenGL.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    global clock, WINDOW_NAME
    pygame.init()
    pygame.display.set_caption(WINDOW_NAME)
    pygame.display.set_icon(pygame.image.load(PATH_LOGO))
    display = (800,600)
    clock = pygame.time.Clock()
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    glEnable(GL_DEPTH_TEST) 
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)