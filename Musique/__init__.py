from pygame import mixer
from os import path

G_path = path.realpath(__file__).replace("__init__.py","")

correspondances = {
    "L":"Do1",
    "L'":"Do1#",
    "D":"Fa",
    "D'":"Fa#",
    "B":"La",
    "B'":"La1#",
    "U":"Mi",
    "U'":"Sol1",
    "R":"Re1",
    "R'":"Re1#",
    "F":"Si1",
    "F'":"Sol1#"
} # les mouvements U2, F2, R2, etc sont décomposés.

mixer.init()
mixer.music.set_volume(1)

def play_mvt(mvt_rubix:str,volume:float=1.0) -> None:
    """
    Joue un son correspondant à un mouvement.
    Paramètres:     mvt_rubix (str) = caractères représentant un mouvement de Rubik's Cube.
                    volume (float) = volume du son (entre 0.0 et 1.0)
    Retourne:       rien.
    """
    path = G_path+"/enregistrements/"+correspondances[mvt_rubix]+".mp3"
    mixer.music.load(path)
    mixer.music.set_volume(volume) # selon entrée utilisateur
    mixer.music.play()