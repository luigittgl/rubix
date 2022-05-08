from tkinter import Tk, Toplevel, Button, Frame, Label
from functools import partial

# Constantes
decal_row = [0, 3, 3, 3, 3, 6]
decal_colonne = [3, 0, 3, 6, 9, 3]
to_color = {"0":"grey", "r":"red", "b":"blue", "o":"orange", "w":"white", "y":"yellow", "g":"green"}
L = -1 # dernier indice d'une liste

class ToplevelApp(Toplevel):
    """
    Classe modélisant l'éditeur de Rubik's cube.
    Hérite de tkinter.Toplevel (fenêtre additionnelle à tkinter.Tk)
    """
    def __init__(self, master:Tk, name:str, mode:str) -> None:
        """
        Instancie un objet ToplevelApp.
        Paramètres:     master (tkinter.Tk) = application/fenêtre tkinter de référence
                        name (str) = nom de la fenêtre
                        mode (str) = mode de l'éditeur ("Correction" ou "Saisie")
        Retourne:       rien.
        """
        # Configuration de la fenêtre
        Toplevel.__init__(self, master)
        self.title(name)
        self.resizable(width=0, height=0) # non-redimensionnable

        self.mode = mode
        self.buttons = [] # liste des bouttons représentant le Rubik's Cube.

        # Widgets
        self.frame_rubiks = Frame(self)
        self.btn_annuler = Button(self, text="Annuler", font=("Arial", 16))
        self.btn_confirm = Button(self, text="Valider", font=("Arial", 16))
        self.label_titre = Label(self, text=self.mode+" du Rubik's cube", font=("Arial", 18))
    
    def show(self, mtx:list) -> None:
        """
        Affiche le contenu de la fenêtre.
        Paramètres:     mtx (list) = représentation d'un cube en liste de matrices.
        Retourne:       rien.
        """
        self.label_titre.grid(row=0, column=0, columnspan=2, pady=(15, 10))
        for i in range(len(mtx)):
            self.buttons.append(list())
            for j in range(len(mtx[i])):
                self.buttons[L].append(list())
                for k in range(len(mtx[i][j])):
                    self.buttons[L][L].append(Case(self.frame_rubiks, to_color[mtx[i][j][k]]))
                    if (j, k) == (1, 1):
                        self.buttons[L][L][L].disable() # boutons du centre = obligatoirement d'une couleur (sauf en correction où il peut y avoir erreurs)
                    self.buttons[L][L][L].grid(row=j+decal_row[i], column=k+decal_colonne[i]) # on place le bouton avec un décalage pour organiser le Rubik's Cube
        self.frame_rubiks.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.btn_annuler.grid(row=2, column=0, pady=10)
        self.btn_confirm.grid(row=2, column=1, pady=10)

class Case(Button):
    """
    Classe modélisant une case de Rubik's Cube comme un bouton.
    Hérite de tkinter.Button.
    """
    def __init__(self, master:Frame, color:str) -> None:
        """
        Instancie un objet Case.
        Paramètres:     master (tkinter.Frame) = frame tkinter où on place le bouton.
                        color (str) = couleur du bouton (red, blue, yellow, ...)
        Retourne:       rien.
        """
        Button.__init__(self, master)
        self.configure(bg=color)
        self.configure(bd = 1)
        self.configure(relief = "ridge")
        self.configure(width = 5)
        self.configure(height = 2)
        self.configure(command = partial(self.change_color, self['bg']))
    
    def change_color(self, c) -> None:
        """
        Change la couleur du bouton.
        Paramètres:     c (str) = couleur actuelle du bouton.
        Retourne:       rien.
        """
        colors = ["red", "blue", "orange", "white", "yellow", "green"]
        # On crée une boucle de parcours des couleurs.
        # = liste chaînée avec dernier élément chainé au premier.
        if c in colors:
            index = colors.index(c)+1
            if index > len(c):
                index = 0
        else:
            index = 0
        self.configure(bg=colors[index])
        self.configure(command=partial(self.change_color, colors[index])) # couleur suivante
    
    def disable(self) -> None:
        """
        Désactive la case : couleur non-changeable.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self['state'] = "disabled"