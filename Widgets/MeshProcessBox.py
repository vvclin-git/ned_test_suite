
from Widgets.MeshPreviewBox import MeshPreviewBox
import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter.ttk import *

from Widgets.ParameterTab import ParameterTab


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
        self.process_paras_tab.pack(side='top')

        self.process_btn_frame = Frame(self.process_frame)
        self.process_btn_frame.pack(side='top')
        self.process_btn = Button(self.process_btn_frame, text='Process', command=self.process_mesh)
        
