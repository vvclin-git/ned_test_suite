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


# sys.path.append(f'{os.getcwd()}\\Widgets\\')
# print(os.getcwd())
# from MeshPreviewBox import MeshPreviewBox
from Widgets.MeshPreviewBox import MeshPreviewBox
from Widgets.MeshProcessBox import MeshProcessBox
from Widgets.MsgBox import MsgBox


class Draper(Frame):
    def __init__(self, window, draper_preview_size):
        super().__init__(window)
        


        # Top Frame
        top_frame = Frame(self)
        top_frame.pack(side='top', expand=1, fill='x')
        
        mesh_frame = LabelFrame(top_frame, text='Merit Mesh Process')
        mesh_frame.pack(side='left')

        eyebox_vol_frame = LabelFrame(top_frame, text='Eyebox Volume Preview')
        eyebox_vol_frame.pack(side='left')
        # Near Mesh Frame
        near_mesh_frame = Frame(mesh_frame)
        near_mesh_frame.pack(side='left', expand=1, fill='x')        
        near_mesh_process = MeshProcessBox(near_mesh_frame, draper_preview_size)
        near_mesh_process.pack(side='top')        

        # Far Frame
        far_mesh_frame = Frame(mesh_frame)
        far_mesh_frame.pack(side='left', expand=1, fill='x')        
        far_mesh_process = MeshProcessBox(far_mesh_frame, draper_preview_size)
        far_mesh_process.pack(side='top')

        # Eyebox Vol Frame
        eyebox_vol_preview_frame = Frame(eyebox_vol_frame)
        eyebox_vol_preview_frame.pack(side='left', expand=1, fill='x')
        eyebox_vol_img = MeshPreviewBox(eyebox_vol_preview_frame, draper_preview_size)
        eyebox_vol_img.pack(side='top')

        # Bottom Frame
        bottom_frame = Frame(self)
        bottom_frame.pack(side='top', expand=1, fill='both')
        
        # Message Output
        msg_frame = LabelFrame(bottom_frame, text='Output Message', style='TLabelframe')
        msg_frame.pack(side='left', expand=1, fill='both')
        self.msg_box = MsgBox(msg_frame) 
        self.msg_box.pack(side='top', expand=1, fill='both')       
        
        # self.controller = Controller(near_mesh_process, far_mesh_process, eyebox_vol, self.msg_box)
        self.controller = Controller(near_mesh_process, far_mesh_process, self.msg_box)
        near_mesh_process.set_controller(self.controller)
        far_mesh_process.set_controller(self.controller)
        # eyebox_vol.set_controller(self.controller)


class Controller():
    def __init__(self, near_mesh_process, far_mesh_process, msg_box):
        self.near_mesh_process = near_mesh_process
        self.fat_mesh_process = far_mesh_process
        # self.eyebox_vol = eyebox_vol
        self.msg_box = msg_box
        pass


# if __name__=='__main__':
#     root = tk.Tk()
#     preview_img_size = (480, 320)
#     sys.path.append(f'{os.getcwd()}\\Widgets\\')
#     print(os.getcwd())
    
#     draper = MeshPreviewBox(root, preview_img_size)
#     draper.pack()
#     root.mainloop()