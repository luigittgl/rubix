from tkinter import Tk, Label, Button, Frame, StringVar, DoubleVar, Scale, OptionMenu, messagebox
from tkinter.font import BOLD
from PIL import Image, ImageTk

# Constantes
SIZE_LOGO = 190

class App(Tk) :
    """
    Classe modélisant l'UI de Rubix.
    Hérite de tkinter.Tk (UI faite avec tkinter).
    """                                                                                                      
    def __init__(self, path_logo:str, win_title:str, win_resizable:bool=False, camera_anim_opt:list=["Rotation double","Rotation triple","Rotation horizontale","Rotation verticale","Rotation pivot","Pas de rotation"]) -> None:
        """
        Instancie un objet App.
        Paramètres: path_logo (str) = chemin d'accès au logo de Rubix.
                    win_title (str) = nom de la fenêtre.
                    win_resizable (bool) = True si fenêtre redimensionnable, False sinon.
                    camera_anim_opt (list) = Liste des modes d'animations possibles.
        Retourne:   rien.
        """
        Tk.__init__(self) # initialisation fenêtre tkinter
        self.camera_anim_opt = camera_anim_opt

        # Paramètres de la fenêtre
        self.title(win_title)
        self.resizable(height=win_resizable,width=win_resizable)

        # Icône de fenêtre
        self.logo = Image.open(path_logo)
        self.iconphoto(True, ImageTk.PhotoImage(self.logo))

        # Logo Rubix
        img_pil = self.logo.resize((SIZE_LOGO, SIZE_LOGO))
        img = ImageTk.PhotoImage(img_pil)

        # Widgets
        self.frame = Frame(self, width=self.winfo_width(), height=self.winfo_height())

        self.frame_top = Frame(self.frame)

        self.pause_btn = Button(self.frame_top,text="Pause",width=12,height=1)
        self.pause_btn.grid(row=0, column=0, padx=5)

        self.label_title = Label(self.frame_top, image=img, width=150, height=150)
        self.label_title.image = img
        self.label_title.grid(row=0, column=1, padx=5, pady=(20, 10))

        self.resume_btn = Button(self.frame_top,text="Reprendre",width=12,height=1)
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.frame_top.grid(row=0, column=0, columnspan=2)

        self.formule_resolution_text = StringVar()
        self.formule_resolution_text.set("Trophées NSI 2022 - Terminale")
        self.formule_resolution = Label(self.frame, textvariable=self.formule_resolution_text)
        self.formule_resolution.grid(row=1, column=0, columnspan=2, pady=(0, 5))

        self.anim_scale_var = DoubleVar()
        self.anim_scale_var.set(2.0)
        self.anim_scale_wd = Scale(self.frame,orient="horizontal",from_=0.0,to=10,resolution=0.1,
        label="Vitesse",sliderlength=20,length=200,variable=self.anim_scale_var,relief="sunken")
        self.anim_scale_wd.grid(row=2, column=0, pady=5, padx=10)

        self.resolve_btn = Button(self.frame,text="Résoudre",width=9,height=2, bg="green")
        self.resolve_btn.grid(row=2,column=1)

        self.cam_anim_scale_var = DoubleVar()
        self.cam_anim_scale_var.set(0.15)
        self.cam_anim_scale_wd = Scale(self.frame,orient="horizontal",from_=-1,to=1,resolution=0.05,
        label="Vitesse de rotation",sliderlength=20,length=200,variable=self.cam_anim_scale_var,relief="sunken")
        self.cam_anim_scale_wd.grid(row=3, column=0, pady=5, padx=10)

        self.camera_anim_opt_var = StringVar()
        self.camera_anim_opt_var.set(self.camera_anim_opt[0])
        self.camera_anim_opt = OptionMenu(self.frame,self.camera_anim_opt_var,*self.camera_anim_opt)
        self.camera_anim_opt.config(width=13,height=2)
        self.camera_anim_opt.grid(row=3, column=1, pady=5, padx=10)
        
        self.volume_scale_var = DoubleVar()
        self.volume_scale_var.set(2.0)
        self.volume_scale_wd = Scale(self.frame,orient="horizontal",from_=0.0,to=1,resolution=0.05,
        label="Volume de la musique",sliderlength=20,length=320,variable=self.volume_scale_var,relief="sunken")
        self.volume_scale_wd.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.enter_cube_btn = Button(self.frame,text="Saisir un cube",width=32, bg="yellow")
        self.enter_cube_btn.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.scan_cube_btn = Button(self.frame,text="Scanner un cube",width=32, bg="blue")
        self.scan_cube_btn.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        self.new_color_btn = Button(self.frame,text="Générer un nouveau cube",width=32, bg="red")
        self.new_color_btn.grid(row=8, column=0, columnspan=2, padx=10, pady=(5, 20))
        
        self.wait_label = Label(self, text="En attente de scan...\nAppuyez sur la touche \"q\" pour annuler.")

        # Affichage UI
        self.go()
    
    def wait(self) -> None:
        """
        Affiche un message d'attente pendant le scan par caméra.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}") # maintien taille fenêtre
        self.frame.pack_forget()
        self.wait_label.pack(expand=True, fill="both")
    
    def go(self) -> None:
        """
        Affiche l'UI et enlève le message d'attente.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self.wait_label.pack_forget()
        self.frame.pack()
    
    def show_error(self, text:str) -> None:
        """
        Affiche un message d'erreur.
        Paramètres:     text (str) = texte du message
        Retourne:       rien.
        """
        messagebox.showerror("Erreur", text)
    
    def show_warning(self, text:str) -> None:
        """
        Affiche un message d'avertissement.
        Paramètres:     text (str) = texte du message
        Retourne:       rien.
        """
        messagebox.showwarning("Attention", text)
    
    def show_formule_resolution(self, string:str) -> None:
        """
        Modifie le texte "Trophées NSI 2022 - Projet Rubix" avec la formule de résolution.
        Paramètres:     string (str) = formule de résolution
        Retourne:       rien.
        """
        self.formule_resolution_text.set(string)
    
    def disable_resolve(self) -> None:
        """
        Désactive le bouton de résolution.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self.resolve_btn['state'] = "disabled"
    
    def enable_resolve(self) -> None:
        """
        Active le bouton de résolution.
        Paramètres:     aucun.
        Retourne:       rien.
        """
        self.resolve_btn['state'] = "normal"