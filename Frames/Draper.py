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


# sys.path.append(f'{os.getcwd()}\\Widgets\\')
# print(os.getcwd())
# from MeshPreviewBox import MeshPreviewBox
from Widgets.MeshPreviewBox import MeshPreviewBox
from Widgets.MeshProcessBox import MeshProcessBox
from Widgets.MsgBox import MsgBox
from Widgets.PresetFileLoad import PresetFileLoad
from Widgets.PathBrowse import PathBrowse
from Widgets.EyeboxVolEval import EyeboxVolEval

class Draper(Frame):
    def __init__(self, window, draper_preview_size):
        super().__init__(window)
        
        self.draper_eval = None
        


        # Top Frame
        top_frame = Frame(self)
        top_frame.pack(side='top', expand=1, fill='x')
        
        left_frame  =Frame(top_frame)
        left_frame.pack(side='left', expand=1, fill='both')

        right_frame  =Frame(top_frame)        
        right_frame.pack(side='left', expand=1, fill='both')

        mesh_frame = LabelFrame(left_frame, text='Merit Mesh Process')
        mesh_frame.pack(side='left', expand=1, fill='both')
        
        # Near Mesh Frame
        near_mesh_frame = Frame(mesh_frame)
        near_mesh_frame.pack(side='left', expand=1, fill='both')        
        self.near_mesh_process = MeshProcessBox(near_mesh_frame, draper_preview_size)
        self.near_mesh_process.pack(side='top')        

        # Far Frame
        far_mesh_frame = Frame(mesh_frame)
        far_mesh_frame.pack(side='left', expand=1, fill='both')        
        self.far_mesh_process = MeshProcessBox(far_mesh_frame, draper_preview_size)
        self.far_mesh_process.pack(side='top')
        # self.near_mesh_process.set_mesh_btn.configure(command=self.set_near_mesh)
        
        # Settings Frame
        settings = LabelFrame(right_frame, text='Settings')
        settings.pack(side='top', expand=1, fill='both')
        
        preset_file_load = PresetFileLoad(settings)
        preset_file_load.pack(side='top', expand=1, fill='x')

        self.path_browse = PathBrowse(settings)
        self.path_browse.pack(side='top', expand=1, fill='x')

        # Eyebox Vol Frame
        # eyebox_vol_frame = LabelFrame(right_frame, text='Eyebox Volume Evaluation')
        # eyebox_vol_frame.pack(side='top', expand=1, fill='both')
        self.eyebox_vol_eval = EyeboxVolEval(right_frame)
        self.eyebox_vol_eval.pack(side='top')
        

        # Bottom Frame
        bottom_frame = Frame(self)
        bottom_frame.pack(side='top', expand=1, fill='both')
        
        # Message Output
        msg_frame = LabelFrame(bottom_frame, text='Output Message', style='TLabelframe')
        msg_frame.pack(side='left', expand=1, fill='both')
        self.msg_box = MsgBox(msg_frame) 
        self.msg_box.pack(side='top', expand=1, fill='both')       
        
        # self.controller = Controller(near_mesh_process, far_mesh_process, eyebox_vol, self.msg_box)
        self.controller = Controller(self.near_mesh_process, self.far_mesh_process, self.msg_box, preset_file_load, self.path_browse, self.eyebox_vol_eval, self.draper_eval)
        self.near_mesh_process.set_controller(self.controller)
        self.far_mesh_process.set_controller(self.controller)
        self.eyebox_vol_eval.set_controller(self.controller)
        # eyebox_vol.set_controller(self.controller)

    def set_near_mesh(self):
        self.sensor_res, self.sensor_size, self.camera_eff, self.camera_distance = self.eyebox_vol_eval.draper_paras_tab.output_parsed_vals()
        self.output_path = self.path_browse.output_path.get()
        # print(camera_paras)
        self.draper_eval = Draper_Eval(self.camera_eff, self.sensor_res, self.sensor_size, self.output_path)
        aper_rois = self.draper_eval.get_aper_roi(self.near_mesh_process.border_coords)
        print(len(aper_rois))
        self.draper_eval.init_pupil_image(aper_rois)
    
    # def set_far_mesh(self):


        

class Controller():
    def __init__(self, near_mesh_process, far_mesh_process, msg_box, preset_file_load, path_browse, eyebox_vol_eval, draper_eval):
        self.near_mesh_process = near_mesh_process
        self.far_mesh_process = far_mesh_process
        # self.eyebox_vol = eyebox_vol
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