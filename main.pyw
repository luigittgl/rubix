from UI import *
from Exceptions import *
import AnimEngine
import Modelisation
import Scan
from os import path
from functools import partial

G_path = path.realpath(__file__).replace("main.pyw","") # chemin absolu
# Constantes
NAME_INTERFACE = "Rubix"
PATH_LOGO = G_path + "UI/images/logo.png"
DEFAULT_CUBE = [[['0', '0', '0'], ['0', 'y', '0'], ['0', '0', '0']], [['0', '0', '0'], ['0', 'r', '0'], ['0', '0', '0']], [['0', '0', '0'], ['0', 'g', '0'], ['0', '0', '0']], [['0', '0', '0'], ['0', 'o', '0'], ['0', '0', '0']], [['0', '0', '0'], ['0', 'b', '0'], ['0', '0', '0']], [['0', '0', '0'], ['0', 'w', '0'], ['0', '0', '0']]]

def set_anim(anim_mode:str, anim_speed:float) -> None:
    """
    Change le mode d'animation 3D du cube.
    Paramètres:     anim_mode (str) = mode de rotation (rotation double, rotation verticale, rotation horizontale, pas de rotation, rotation pivot, rotation triple)
                    anim_speed (float) = vitesse d'animation (de 0.0 à 10.0)
    Retourne:       rien.
    """
    global Rubix
    Rubix.set_camera_mode("animation")
    Rubix.set_animation_mode({
            "Rotation triple":4,
            "Rotation double":3,
            "Rotation verticale":2,
            "Rotation horizontale":1,
            "Rotation pivot":5,
            "Pas de rotation":0
        }[anim_mode], anim_speed
    )

def set_res_speed(speed:float) -> None:
    """
    Actualise la vitesse des animations.
    Paramètres:     speed (float) = vitesse souhaitée (de 0.0 à 10.0)
    Retourne:       rien.
    """
    global Rubix
    Rubix.animate_speed = speed

def set_volume(volume:float) -> None:
    """
    Actualise le volume de la musique.
    Paramètres:     volume (float) = volume souhaité (de 0.0 à 1.0)
    Retourne:        rien.
    """
    global Rubix
    Rubix.sound_volume = volume

def new_cube() -> None:
    """
    Crée un nouveau cube aléatoire (en variable globale) et l'affiche.
    Paramètres:     aucun.
    Renvoie:        rien.
    """
    global Rubix,Cube,Ui
    Cube, Rubix = None, None # réinitialisation
    Rubix = AnimEngine.init()
    Cube = Modelisation.Cube() # nouveau cube
    Cube.Cube_GL = Rubix # lien 3d/cube
    Cube.scramble() # mélange
    if "Ui" in globals(): # si l'interface est lancée, alors on la réinitialise
        Ui.show_formule_resolution("Trophées NSI 2022 - Terminale")
        Ui.enable_resolve()
    mtx = Cube.get_matrix()
    Rubix.load_color_matrix(mtx) # affichage cube

def solve() -> None:
    """
    Résout le Rubik's Cube en variable globale. Vérifie sa validité.
    Affiche la liste des mouvements ; lance les animations 3D ; et la musique.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    global Rubix
    global Cube
    try:
        x = Cube.get_formula_to_solve()
    except CombinaisonError as e: # cube invalide
        Ui.show_error(str(e))
    else:
        mvt_lst = []
        mvt = ""
        for char_id in range(0,len(x)) :
            if x[char_id] == " " :
                if "2" in mvt : # double mouvement : U2, R2...
                    mvt_lst.append(mvt[0])
                    mvt_lst.append(mvt[0])
                else :
                    mvt_lst.append(mvt)
                mvt = ""
            else :
                mvt = mvt + x[char_id]
        Ui.show_formule_resolution(x)
        Ui.update()
        Ui.disable_resolve() # bouton résoudre non cliquable
        Rubix.play_sequence(mvt_lst, awaited=False, enable_sound=True) # animations et sons

def pause() -> None:
    """
    Mets en pause les animations 3D.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    global speed
    speed = Ui.anim_scale_var.get()
    Ui.anim_scale_var.set(0) # vitesse nulle

def resume() -> None:
    """
    Permet (après avoir mis les animations en pause) de reprendre l'animation 3D.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    Ui.anim_scale_var.set(speed)

def launch_camera() -> None:
    """
    Lance l'outil de scan et scanne le cube.
    Récupère le cube scanné et vérifie sa validité.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    global Cube
    Ui.wait() # message "en attente de scan..."
    Ui.update()
    AnimEngine.stop() # arrêt de l'interface 3d
    try:
        matrice = Scan.main() # récupération résultat caméra
        assert len(matrice) == 6 # valeur [] retournée si arrêt du programme
    except CameraError as e: # pb de lecture
        AnimEngine.main() # relance 3d
        Ui.go()
        Ui.update()
        Ui.show_error(str(e))
    except AssertionError: # valeur [] retournée si arrêt du programme
        AnimEngine.main()
        Ui.go()
        Ui.update()
    else:
        AnimEngine.main()
        Ui.go()
        Ui.update()
        Cube = Modelisation.CubeByMatrix(matrice) # nouveau cube
        try:
            Cube.get_formula_to_solve() # test de validité
        except CombinaisonError:
            Ui.show_warning("Le cube scanné est invalide. Veuillez le corriger !")
            mat = Cube.get_matrix()
            for i in range(0, 6):
                mat[i][1][1] = DEFAULT_CUBE[i][1][1] # on fixe les centres
            launch_editor(mat) # correction du cube
        else:
            Cube.Cube_GL = Rubix
            Rubix.load_color_matrix(Modelisation.Cutils.copy_3by3(matrice)) # affichage cube
            Ui.update()

def launch_editor(mtx:list[list[str]]=DEFAULT_CUBE) -> None:
    """
    Lance l'éditeur de Rubik's Cube, et ferme l'animation 3D.
    Paramètres:     mtx (list[list[str]]) : représentation d'un cube en liste de matrices.
                    Facultatif (uniquement si cube déjà saisi, à corriger)
    Retourne:       rien.
    """
    global block_3d
    block_3d = True
    AnimEngine.stop()
    mode = "Saisie" if mtx == DEFAULT_CUBE else "Correction" # L'éditeur est le même pour une saisie totale et une correction si mauvais scan
    editor = Editor.ToplevelApp(Ui, NAME_INTERFACE+" Editor", mode)
    editor.btn_annuler.configure(command=partial(back_editor, editor)) # association fonction/bouton
    editor.btn_confirm.configure(command=partial(confirm_editor, editor))
    editor.show(mtx) # affichage éditeur

def back_editor(editor:Editor.ToplevelApp) -> None:
    """
    Ferme l'éditeur et relance l'animation 3D.
    Paramètres:     editor (Editor.ToplevelApp) = objet qui représente la fenêtre d'édition.
    Retourne:       rien.
    """
    global block_3d
    editor.destroy()
    block_3d = False
    AnimEngine.main()

def confirm_editor(editor:Editor.ToplevelApp) -> None:
    """
    Récupère la saisie de l'utilisateur dans l'éditeur de Rubik's cube.
    Crée un nouveau cube.
    Vérifie la validité du cube.
    Affiche le cube dans l'interface graphique et ferme l'éditeur.
    Paramètres:     editor (Editor.ToplevelApp) = objet qui représente la fenêtre d'édition.
    Retourne:       rien.
    """
    global Cube, block_3d
    m = [] # liste de matrices 3x3
    color_to = {"red":"r", "blue":"b", "white":"w", "green":"g", "orange":"o", "yellow":"y"}
    redo = False # True si une case non renseignée ; False sinon
    for i in range(len(editor.buttons)):
        m.append(list())
        for j in range(len(editor.buttons[i])):
            m[-1].append(list())
            for k in range(len(editor.buttons[j])):
                get = editor.buttons[i][j][k]['bg'] # récupération de la couleur du boutons
                if get in color_to.keys(): # si couleur valide
                    m[-1][-1].append(color_to[get])
                else:
                    m[-1][-1].append("0") # valeur par défaut
                    redo = True
    try:
        Modelisation.CubeByMatrix(m).get_formula_to_solve() # vérification solvabilité
    except CombinaisonError:
        Ui.show_warning("Le cube n'est pas valide !")
        editor.destroy()
        launch_editor(m) # nouvel éditeur
    else:
        if redo: # si manquements
            Ui.show_warning("Le cube n'est pas valide !")
            editor.destroy()
            launch_editor(m)
        else:
            editor.destroy()
            block_3d = False
            AnimEngine.main()
            Cube = Modelisation.CubeByMatrix(m) # nouveau cube valide
            Cube.Cube_GL = Rubix
            Rubix.load_color_matrix(Modelisation.Cutils.copy_3by3(m)) # affichage cube
            Ui.update()

def stop_execution() -> None:
    """
    Arrête l'exécution du programme.
    Paramètres:     aucun.
    Retourne:       rien.
    """
    global execution
    execution = False

if __name__ == "__main__" : # si le script est exécuté lui-même

    # Variants de boucle pour exécution
    execution = True
    block_3d = False # animation 3D

    # Nouveau cube
    new_cube()

    # Configuration caméra
    Scan.initInterface(PATH_LOGO, NAME_INTERFACE+" Scanner")

    # Config interface graphique
    Ui = Base.App(PATH_LOGO, NAME_INTERFACE+" UI")
    Ui.cam_anim_scale_var.set(Rubix.camera_speed)
    Ui.new_color_btn.configure(command=new_cube)
    Ui.resolve_btn.configure(command=solve)
    Ui.volume_scale_wd.configure(command=lambda x: set_volume(float(Ui.volume_scale_var.get()))) # changement volume
    Ui.pause_btn.configure(command=pause)
    Ui.scan_cube_btn.configure(command=launch_camera)
    Ui.resume_btn.configure(command=resume)
    Ui.enter_cube_btn.configure(command=launch_editor)
    Ui.protocol("WM_DELETE_WINDOW", stop_execution) # croix rouge = arrêt de l'exécution
    
    # Configuration modélisation 3D
    AnimEngine.initInterface(PATH_LOGO, NAME_INTERFACE+" 3D")
    AnimEngine.main()

    while execution: # boucle principale
        Ui.update() # actualisation interface graphique
        if not block_3d: # animation bloquée
            set_anim(Ui.camera_anim_opt_var.get(), float(Ui.cam_anim_scale_var.get())) # actualisation animation
            set_res_speed(Ui.anim_scale_var.get()) # actualisation vitesse
            set_volume(float(Ui.volume_scale_var.get())) # actualisation volume
            AnimEngine.update(Rubix) # actualisation