from textwrap import fill
import tkinter as tk
from turtle import bgcolor
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
from ZoomCanvas import *

class NetsFrame(Frame):
    def __init__(self, window):
        super().__init__(window)

        self.msg = tk.StringVar()
        self.msg.set('Message Output')
        
        output = Frame(self, style='Output.TFrame', width=980, height=960, padding=(10, 10))   
        output.grid(row=0, column=0, rowspan=2, sticky="NEWS")
        output.pack_propagate(0)
        
        preview_frame = LabelFrame(output, text='Preview Image', width=960, height=740, style='TLabelframe')        
        preview_frame.pack(side='top', expand=True, fill='both', pady=(0, 20))      
                
        img = np.zeros([720, 960, 3], dtype=np.uint8)
        cv2.putText(img, 'Preview Image', (400, 330), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        # img = Image.fromarray(img)

        self.preview_img = Image.fromarray(img)        
        self.preview_canvas = Zoom_Advanced(preview_frame, self.preview_img)     
        
        msg_frame = LabelFrame(output, width=960, height=160, text='Output Message', style='TLabelframe')        
        msg_frame.pack(side='bottom')
        msg_frame.pack_propagate(0)
        
        self.msg_output = tk.Text(msg_frame, height=6, state='disabled')
        self.msg_output.pack(side=tk.LEFT, expand=True, fill='both')
        msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL, command=self.msg_output.yview)
        self.msg_output['yscrollcommand'] = msg_scroll.set
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.settings = Frame(self, style='Settings.TFrame', width=500, height=720)
        # self.pack_propagate(0)
        self.settings.grid(row=0, column=1, sticky='EW')
        
        self.buttons = Frame(self, style='Buttons.TFrame', width=500, height=240)
        self.buttons.grid(row=1, column=1, sticky='EW')
    
    def console(self, msg, cr=True):
        self.msg_output.config(state='normal')
        if cr:
            self.msg_output.insert('end', msg + '\n')
        else:
            self.msg_output.insert('end', msg)
        self.msg_output.config(state='disabled')
        return
    
    def console_clr(self):
        self.msg_output.config(state='normal')
        self.msg_output.delete('1.0', 'end')
        self.msg_output.config(state='disabled')
    
    def update_img(self, img):
        self.preview_canvas.update_image(img)
        return



        

