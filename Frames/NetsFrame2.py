from textwrap import fill
import tkinter as tk
from turtle import bgcolor
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
from Widgets.ParameterTab import ParameterTab
from Widgets.ZoomCanvas import *
from Widgets.ImgFileLoad import ImgFileLoad
from Widgets.MsgBox import MsgBox
from Widgets.PresetFileLoad import PresetFileLoad
from Widgets.PathBrowse import PathBrowse
import os
import json
from tkinter import filedialog

class NetsFrame2(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)
        
        self.preset_path = tk.StringVar()                
        self.presets = None
        self.preview_img_size = preview_img_size
        self.columnconfigure(0, weight=2, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)
        self.rowconfigure(0, weight=1, uniform=1)
        
        # Output container settings
        output = Frame(self, style='Output.TFrame', padding=(10, 10))   
        output.grid(row=0, column=0, sticky="NEWS")
        output.rowconfigure(0, weight=5, uniform=1)
        output.rowconfigure(1, weight=1, uniform=1)
        output.columnconfigure(0, weight=1)
        
        # Preview Image Widget
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]                     
        preview_frame = LabelFrame(output, text='Preview Image', style='Test.TLabelframe')           
        preview_frame.grid(row=0, column=0, sticky='NEWS', pady=(0, 10))           
        
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.preview_canvas = Zoom_Advanced(preview_frame, self.preview_img)             

        # Message Output     
        msg_frame = LabelFrame(output, text='Output Message', style='TLabelframe')  
        msg_frame.grid(row=1, column=0, sticky='NEWS')
        self.msg_box = MsgBox(msg_frame)        
        self.msg_box.pack(side='top', expand=1, fill='both')        
        
        # Settings Container Settings        
        self.settings = Frame(self, style='Settings.TFrame', padding=(10, 10))        
        self.settings.grid(row=0, column=1, sticky='NEW')
                
        # Preset Save / Load
        self.preset_file_load = PresetFileLoad(self.settings)
        self.preset_file_load.pack(side='top', expand=1, fill='x')

        # Image Loading
        self.img_file_load = ImgFileLoad(self.settings, self.load_img)
        self.img_file_load.pack(side='top', expand=1, fill='both')
        

    
    def load_img(self):
        self.preview_img = Image.fromarray(self.img_file_load.image)
        self.raw_img = self.img_file_load.image
        self.preview_canvas.update_image(Image.fromarray((self.img_file_load.image).astype(np.uint8)))
        # self.canvas.update()
        # self.canvas.scale_to_canvas()
        msg_output = f'Image loaded from {self.img_file_load.img_path.get()}\n'
        msg_output += f'Image Resolution: {self.raw_img.shape[1]}x{self.raw_img.shape[0]}'
        self.controller.msg_box.console(msg_output)
        return
    
    def reset(self):
        for btn_group in self.buttons:
            self.disable_btn_group(btn_group)
        return

    def enable_btn_group(self, btn_group):
        for b in btn_group:
            b.config(state='enable')
        return

    def disable_btn_group(self, btn_group):
        for b in btn_group:
            b.config(state='disable')
        return
    


if __name__=='__main__':
    root = tk.Tk()
    root.geometry('1680x990')
    preview_img_size = (960, 740)
    nets_frame = NetsFrame2(root, preview_img_size)
    nets_frame.pack()
    root.mainloop()

