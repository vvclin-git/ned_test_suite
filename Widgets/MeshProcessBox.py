
from Widgets.MeshPreviewBox import MeshPreviewBox
import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter.ttk import *

from Widgets.ParameterTab import ParameterTab
from Widgets.ToggleBtn import ToggleBtn

parameters = {'Blur Kernel Size': {'value':1, 'type':'value', 'options':None},
              'Threshold Value': {'value':2, 'type':'value', 'options':None},
              'Contour Approx Epsilon': {'value':0.1, 'type':'value', 'options':None},
              }

class MeshProcessBox(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)

        self.mp_box = MeshPreviewBox(self, preview_img_size)
        self.mp_box.pack(side='top')
        self.process_frame = Frame(self)
        self.process_frame.pack(side='top')
        self.process_paras_tab = ParameterTab(self.process_frame, parameters)
        self.process_paras_tab.tree.configure(height=len(parameters))
        self.process_paras_tab.pack(side='top')

        self.process_btn_frame = Frame(self.process_frame)
        self.process_btn_frame.pack(side='top', expand=1, fill='x')
        self.set_mesh_btn = Button(self.process_btn_frame, text='Set Mesh', command=self.set_mesh)
        self.set_mesh_btn.pack(side='right')
        self.preview_btn = ToggleBtn(self.process_btn_frame, 'Preview On', 'Preview Off', self.preview_on, self.preview_off)
        self.preview_btn.pack(side='right')
        self.process_btn = Button(self.process_btn_frame, text='Process', command=self.process_mesh)
        self.process_btn.pack(side='right')
        

    def process_mesh(self):
        return
    
    def preview_on(self):
        return

    def preview_off(self):
        return
    
    def set_mesh(self):
        return