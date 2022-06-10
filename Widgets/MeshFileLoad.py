
import numpy as np
from tkinter.ttk import *
import tkinter as tk
import os
from tkinter import filedialog
from functools import partial

class MeshFileLoad(Frame):
    def __init__(self, window, load_func) -> None:
        super().__init__(window)
        self.mesh = None
        self.mesh_path = tk.StringVar()        

        self.mesh_load_frame = LabelFrame(window, text='Mesh File Loading')
        self.mesh_load_frame.pack(expand=True, fill='x', side='top')
        
        self.mesh_load_input_frame = Frame(self.mesh_load_frame)
        self.mesh_load_input_frame.pack(side='top', expand=True, fill='both')
        self.mesh_load_btn_frame = Frame(self.mesh_load_frame)
        self.mesh_load_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.mesh_path_label = Label(self.mesh_load_input_frame, text='Mesh Path')
        self.mesh_path_label.pack(side='left', padx=5, pady=5)
        self.mesh_path_input = Entry(self.mesh_load_input_frame, textvariable=self.mesh_path)        
        self.mesh_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        mesh_load_btn = Button(self.mesh_load_btn_frame, text='Load', style='Buttons.TButton', command=partial(self.mesh_load, load_func))
        mesh_load_btn.pack(side='right', padx=2, pady=5)
        mesh_browse_btn = Button(self.mesh_load_btn_frame, text='Browse...', style='Buttons.TButton', command=self.mesh_browse)        
        mesh_browse_btn.pack(side='right', padx=2, pady=5)
    
    def mesh_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a 2D mesh file', filetypes=[("Numpy Binary File","*.npy")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.mesh_path.set(temp_path)
        return

    def mesh_load(self, load_func):
        mesh_path = self.mesh_path.get()
        if len(mesh_path) > 0:            
            self.mesh = np.load(mesh_path)            
            load_func()            
        return
