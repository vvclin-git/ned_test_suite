from textwrap import fill
import tkinter as tk
from turtle import bgcolor
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk

import os
import json
from tkinter import filedialog
import sys
from NED_Analyzer import Draper_Eval

from Widgets.MeshProcessBox import MeshProcessBox
from Widgets.MsgBox import MsgBox
from Widgets.PresetFileLoad import PresetFileLoad
from Widgets.PathBrowse import PathBrowse
from Widgets.EyeboxVolEval import EyeboxVolEval

PRESET_PATH = '.\\Presets\\draper_default.json'
OUTPUT_PATH = '.\\Output\\'

class Draper(Frame):
    def __init__(self, window, draper_preview_size):
        super().__init__(window)        
                
        self.draper_eval = None
        
        # Top Frame
        top_frame = Frame(self, style='Green.TFrame')
        top_frame.pack(side='top', expand=0, fill='x')
        
        mesh_frame = LabelFrame(top_frame, text='Merit Mesh Process')
        mesh_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)
        right_frame  =Frame(top_frame)        
        right_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)        
        
        # Pupil Mesh Frame              
        self.pupil_mesh_process = MeshProcessBox(mesh_frame, draper_preview_size)
        self.pupil_mesh_process.img_load.img_load_frame.configure(text='Pupil Mesh')
        self.pupil_mesh_process.pack(side='left', expand=1, fill='both', ipady=10, padx=5, pady=5)        

        # Far Frame        
        self.far_mesh_process = MeshProcessBox(mesh_frame, draper_preview_size)
        self.far_mesh_process.img_load.img_load_frame.configure(text='Far Mesh')
        self.far_mesh_process.pack(side='left', expand=1, fill='both', ipady=10, padx=5, pady=5)        
        
        # Settings Frame
        settings = LabelFrame(right_frame, text='Settings')
        settings.pack(side='top', expand=1, fill='both', ipady=5, pady=(0, 10))
        
        preset_file_load = PresetFileLoad(settings)        
        preset_file_load.pack(side='top', expand=1, fill='x', padx=5)

        self.path_browse = PathBrowse(settings)
        self.path_browse.pack(side='top', expand=1, fill='x', padx=5)
        self.path_browse.output_path.set(OUTPUT_PATH)

        # Eyebox Vol Frame        
        self.eyebox_vol_eval = EyeboxVolEval(right_frame)
        self.eyebox_vol_eval.pack(side='top', expand=1, fill='both', ipady=10)        


        linked_tabs = {'pupil_mesh_paras':self.pupil_mesh_process.process_paras_tab,
                       'far_mesh_paras':self.far_mesh_process.process_paras_tab,
                       'draper_paras':self.eyebox_vol_eval.draper_paras_tab,
                       'eyebox_view_paras':self.eyebox_vol_eval.eyebox_view_paras_tab
                      }

        preset_file_load.init_linked_tabs(linked_tabs)
        preset_file_load.preset_path.set(PRESET_PATH)
        preset_file_load.load_preset()   

        # Bottom Frame
        bottom_frame = Frame(self, style='Red.TFrame')
        bottom_frame.pack(side='top', expand=1, fill='both', anchor='n')
        
        # Message Output
        msg_frame = LabelFrame(bottom_frame, text='Output Message', style='TLabelframe')
        msg_frame.pack(side='top', expand=1, fill='both')
        self.msg_box = MsgBox(msg_frame) 
        self.msg_box.pack(side='top', expand=1, fill='both')       
        
        # self.controller = Controller(pupil_mesh_process, far_mesh_process, eyebox_vol, self.msg_box)
        self.controller = Controller(self.pupil_mesh_process, self.far_mesh_process, self.msg_box, preset_file_load, self.path_browse, self.eyebox_vol_eval, self.draper_eval)
        self.pupil_mesh_process.set_controller(self.controller)
        self.far_mesh_process.set_controller(self.controller)
        self.eyebox_vol_eval.set_controller(self.controller)
        # eyebox_vol.set_controller(self.controller)

             

class Controller():
    def __init__(self, pupil_mesh_process, far_mesh_process, msg_box, preset_file_load, path_browse, eyebox_vol_eval, draper_eval):
        self.pupil_mesh_process = pupil_mesh_process
        self.far_mesh_process = far_mesh_process
        
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.path_browse = path_browse
        self.eyebox_vol_eval = eyebox_vol_eval
        self.draper_eval = draper_eval
        pass


# if __name__=='__main__':
#     root = tk.Tk()
#     preview_img_size = (480, 320)
#     sys.path.append(f'{os.getcwd()}\\Widgets\\')
#     print(os.getcwd())
    
#     draper = MeshPreviewBox(root, preview_img_size)
#     draper.pack()
#     root.mainloop()