from Exceptions import CameraError

import cv2
from datetime import datetime
import numpy
from scipy.spatial import KDTree
from os import path

G_path = path.realpath(__file__).replace("__init__.py","")

# Constantes
SECONDS_WAITING = 5
MARGE_PIXEL = 15
WINDOW_NAME = ""
PATH_LOGO = ""

# Variant d'exécution
running = True

def read_camera(video:cv2.VideoCapture) -> numpy.ndarray:
    """
    Lit la vidéo renvoyée par la caméra.
    Paramètres:     video (cv2.VideoCapture) = objet représentant l'entrée video.
    Retourne:       (numpy.ndarray) = représentation matricielle de l'image obtenue.
    """
    is_ok, image = video.read()
    if is_ok:
        return image
    raise CameraError("Impossible de lire la source")

def conditions_ok(contour:numpy.ndarray) -> bool:
    """
    Vérifie, pour un contour, s'il peut correspondre à une case de Rubik's Cube.
    Paramètres:     contour (numpy.ndarray) = contour openCV
    Retourne:       (bool) = True si le contour correspond, False sinon.
    """
    area = cv2.contourArea(contour)
    if not 1000 < area < 3000: # taille du cube
        return False
    perimeter = cv2.arcLength(contour, True)
    return cv2.norm(((perimeter / 4) * (perimeter / 4)) - area) < 150 # condition issue de tests

def to_int_list(obj:list|tuple|dict|set) -> list[int]:
    """
    Convertit un itérable en liste d'entiers, si possible (lève une ValueError sinon).
    Paramètres:     obj (iterable) = itérable à convertir.
    Retourne:       (list[int]) = une liste d'entiers.
    """
    return [int(x) for x in list(obj)]

def calcul_couleur(image:numpy.ndarray, x:float, y:float, w:float, h:float) -> list:
    """
    Calcule la couleur moyenne d'une case.
    Paramètres:     obj (iterable) = itérable à convertir.
                    x (float) = l'abscisse de la case
                    y (float) = l'ordonnée de la case
                    w (float) = la longueur de la case
                    h (float) = la hauteur de la case
    Retourne:       (list) = liste contenant :
                        - (int) = valeur moyenne HUE
                        - (int) = valeur moyenne SATURATION
                        - (int) = valeur moyenne VALUE
                        - (float) = une valeur indicatrice de l'emplacement de la case
    """
    val = 50*y + 10*x
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # image en RGB
    # moyenne des couleurs de chaque pixel de la case
    # on réduit la case pour que la couleur noir des contours ne soit pas prise en compte
    echantillon = to_int_list(cv2.mean(hsv[y+MARGE_PIXEL:y+h-MARGE_PIXEL,x+MARGE_PIXEL:x+w-MARGE_PIXEL]))
    return echantillon + [val]

def to_matrix(l:list) -> list[list]:
    """
    Convertit une liste de 9 éléments en matrice de 3x3.
    Paramètres:     l (list) = liste de 9 éléments
    Retourne:       (list) = matrice de 3x3
    """
    assert len(l) == 9
    new = [[], [], []]
    x = 0
    for i in range(9):
        new[x].append(l[i])
        if (i+1)%3 == 0 and i != 0: # ou i % 3 = 2
            x += 1
    return new

def association_couleurs(r:int, g:int, b:int) -> str:
    """
    Associe une couleur à une case.
    Paramètres:     r (int) = Red (entre 0 et 255)
                    g (int) = Green (entre 0 et 255)
                    b (int) = Blue (entre 0 et 255)
    Retourne:       (str) = caractère représentant la couleur de la case : r, b, g, y, o ou w.
    """
    colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 165, 0), (255, 255, 255)]
    trad = ["r", "b", "g", "y", "o", "w"]
    kdt_db = KDTree(colors) # arbre de classification (Deep Learning)
    distance, index = kdt_db.query((r, g, b)) # prédiction du modèle
    return trad[index]

def analize_face(video:cv2.VideoCapture, text1:str=" ", text2:str=" ") -> list[list]:
    """
    Détecte, analyse et modélise une face du cube.
    Paramètres:     video (cv2.VideoCapture) = objet représentant l'entrée video.
                    text1 (str) = premier texte à afficher.
                    text2 (str) = second texte à afficher.
    Retourne:       (list) = matrice 3x3 représentant une face.
    """
    global running # variant d'exécution
    while True: # s'arrête lorsque face complète
        image = read_camera(video) # lecture

        # Gommage des "trous" de mauvaise couleur + optimisation pour analyse
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        gray = cv2.adaptiveThreshold(gray,20,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,5,0)

        #Détection des contours
        contours = cv2.findContours(gray,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)[0]

        # Affichage du texte
        image = cv2.putText(image, text1, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2) # affichage texte
        image = cv2.putText(image, text2, (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2) # affichage texte
        
        # Vérification des contours et calcul des couleurs
        _colors = []
        for contour in contours:
            if conditions_ok(contour):
                x, y, w, h = cv2.boundingRect(contour) # coordonnées de la case
                image = cv2.drawContours(image, [contour], 0, (255, 255, 0), 2) # on trace la case identifiée
                _colors.append(calcul_couleur(image, x, y, w, h)) # association de la couleur à la case et enregistrement
        cv2.imshow(WINDOW_NAME, image) # on affiche la fenêtre
        key_pressed = cv2.waitKey(1) & 0xFF # non-bloquant
        if key_pressed == 27 or key_pressed == ord('q'):
            # Fermeture du scan
            running = False
            cv2.destroyAllWindows()
            break
        if len(_colors) != 9: # face incomplète
            continue

        # couleurs triées par indice par la valeur de (50*y + 10*x) --> ordre des cases
        colors = sorted(_colors, key=lambda x: x[4], reverse=False) 
        
        # Création de la matrice de la face
        face = [0, 0, 0, 0, 0, 0, 0, 0, 0] # initialisation de la face (en liste simplifiée)
        for i in range(len(colors)):
            r, g, b = colors[i][0], colors[i][1], colors[i][2] # R, G, B
            face[i] = association_couleurs(r, g, b)
        print(to_matrix(face))
        if 0 in face: # couleur non identifiée = face incomplète
            continue
        return to_matrix(face) # face sous forme de matrice

def wait_with_video(video:cv2.VideoCapture, vid:str, tstamp:int=8, text1:str=" ", text2:str=" ") -> None:
    """
    Fait patienter le scan en affichant un texte, en gardant la caméra visible.
    Paramètres:     video (cv2.VideoCapture) = objet représentant l'entrée de la caméra
                    vid (str) = chemin d'accès à la vidéo.
                    tstamp (int) = nombre de secondes d'attente.
                    text1 (str) = premier texte à afficher.
                    text2 (str) = second texte à afficher.
    Retourne:       rien.
    """
    global running
    start = datetime.now()
    video_asked = cv2.VideoCapture(vid)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    while True:
        image = read_camera(video_asked)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        image = cv2.putText(image, text1, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2) # affichage texte
        image = cv2.putText(image, text2, (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2) # affichage texte
        cv2.imshow(WINDOW_NAME, image)
        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == 27 or key_pressed == ord('q'):
            running = False
            cv2.destroyAllWindows()
            break
        if (datetime.now() - start).total_seconds() < SECONDS_WAITING:
            continue
        break

def wait_with_image(video:cv2.VideoCapture, img:str, tstamp:int=8, text1:str=" ", text2:str=" ") -> None:
    """
    Fait patienter le scan en affichant un texte et une image.
    Paramètres:     video (cv2.VideoCapture) = objet représentant l'entrée de la caméra
                    img (str) = chemin d'accès à l'image.
                    tstamp (int) = nombre de secondes d'attente.
                    text1 (str) = premier texte à afficher.
                    text2 (str) = second texte à afficher.
    Retourne: rien.
    """
    global running
    start = datetime.now()
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(width, height)
    while True:
        image = cv2.imread(img, cv2.IMREAD_UNCHANGED)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        image = cv2.putText(image, text1, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2) # affichage texte
        image = cv2.putText(image, text2, (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 0), 2) # affichage texte
        cv2.imshow(WINDOW_NAME, image)
        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == 27 or key_pressed == ord('q'):
            running = False
            cv2.destroyAllWindows()
            break
        if (datetime.now() - start).total_seconds() < SECONDS_WAITING: # calcul temps écoulé
            continue
        break
    
def rot90_anticlockwise(m:list[list]) -> list[list]:
    """
    Effectue une rotation à 90 degrés (dans le sens inverse des aiguilles d'une montre) d'une matrice 3x3.
    Paramètres:     m (list[list]) = matrice 3x3.
    Retourne:       (list[list]) = matrice 3x3, rotation effectuées.
    """
    return [[m[j][i] for j in range(len(m))] for i in range(len(m[0])-1,-1,-1)]

def main() -> None:
    """
    Exécution du processus de scan.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    global running
    running = True
    video = cv2.VideoCapture(0)
    video.read()
    keys = ["blanc", "vert", "rouge", "bleu", "orange", "jaune"] # ordre des faces
    faces = [None for _ in range(0, 6)]
    wait_with_image(
        video,
        G_path+"/videos/position_depart_cube.png",
        text1="Mettez le cube dans cette position,",
        text2="en face de la webcam"
    ) # image position initiale du cube
    for i in range(len(keys)): # pour chaque face
        if not running: # arrêt du programme
            return []
        faces[i] = analize_face(video, text1=f"Lecture de la face dont", text2=f"le centre est {keys[i]}...")
        if i < len(keys)-1 and running: # face suivante
            wait_with_video(
                video,
                G_path+f"/videos/tourner_cube_{keys[i+1]}.mp4",
                text1="Tournez le cube vers la face dont",
                text2=f"le centre est {keys[i+1]}..."
            ) # vidéo tuto : comment tourner le cube ?
    cv2.destroyAllWindows()
    return [rot90_anticlockwise(faces[5]), faces[2], faces[1], faces[4], faces[3], faces[0]] # on tourne la face 1 pour correspondre à notre modèle de représentation

def initInterface(path_logo:str, name:str) -> None:
    """
    Initialise les constantes de l'interface.
    Paramètres:     path_logo (str) = chemin d'accès au logo de Rubix.
                    name (str) = nom de la fenêtre.
    Retourne:       rien.
    """
    global WINDOW_NAME, PATH_LOGO
    WINDOW_NAME = name
    PATH_LOGO = path_logo
