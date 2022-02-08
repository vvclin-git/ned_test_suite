from textwrap import fill
import tkinter as tk
from turtle import bgcolor
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk

class NetsFrame(Frame):
    def __init__(self, window):
        super().__init__(window)

        self.msg = tk.StringVar()
        self.msg.set('Message Output')
        
        output = Frame(self, style='Output.TFrame', width=980, height=960, padding=(10, 10))   
        output.grid(row=0, column=0, rowspan=2, sticky="NEWS")
        
        preview_frame = LabelFrame(output, text='Preview Image', width=960, height=740, style='TLabelframe')        
        preview_frame.pack(side='top')
        
        img = np.zeros([720, 960, 3], dtype=np.uint8)
        cv2.putText(img, 'Preview Image', (400, 330), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        img = Image.fromarray(img)
        self.preview_img = ImageTk.PhotoImage(img)        
        
        self.preview_canvas = tk.Canvas(preview_frame, width=960, height=720, relief='flat', highlightthickness=0, borderwidth=0)
        self.preview_img_box = self.preview_canvas.create_image(0, 0, image=self.preview_img, anchor=tk.NW)                           
        self.preview_canvas.image = self.preview_img
        self.preview_canvas.pack()
        
        msg_frame = LabelFrame(output, width=960, height=180, text='Output Message', style='TLabelframe')        
        msg_frame.pack(side='bottom')
        msg_frame.pack_propagate(0)

        self.msg_output = Label(msg_frame, textvariable=self.msg, style='MessageBox.TLabel')
        self.msg_output.pack(side=tk.LEFT, expand=True, fill='both')
        msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL)
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.settings = Frame(self, style='Settings.TFrame', width=500, height=720)
        self.settings.grid(row=0, column=1)

        
        self.buttons = Frame(self, style='Buttons.TFrame', width=500, height=240)
        self.buttons.grid(row=1, column=1)

    def console(self, msg):
        old_msg = self.msg.get()
        new_msg = old_msg + '\n' + msg
        self.msg.set(new_msg)
        return
    
    def update_img(self, img):
        self.preview_canvas.itemconfig(self.preview_img_box, image=img)
        self.preview_canvas.image = img
        return



        

