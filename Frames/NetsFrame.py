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

        # preview_frame = LabelFrame(output, text='Preview Image', width=960, height=740, relief='groove', borderwidth=2)
        preview_frame = LabelFrame(output, text='Preview Image', width=960, height=740, style='TLabelframe')        
        preview_frame.pack(side='top')
        
        img = np.zeros([720, 960, 3], dtype=np.uint8)
        cv2.putText(img, 'Preview Image', (400, 330), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        img = Image.fromarray(img)
        preview_img = ImageTk.PhotoImage(img)        
        
        preview_img_box = tk.Canvas(preview_frame, width=960, height=720, relief='flat', highlightthickness=0, borderwidth=0)
        preview_img_box.create_image(0, 0, image=preview_img, anchor=tk.NW)                           
        preview_img_box.image = preview_img
        preview_img_box.pack()
        
        msg_frame = LabelFrame(output, width=960, height=180, text='Output Message', style='TLabelframe')        
        msg_frame.pack(side='bottom')
        msg_frame.pack_propagate(0)

        msg_output = Label(msg_frame, textvariable=self.msg, style='MessageBox.TLabel')
        msg_output.pack(side=tk.LEFT, expand=True, fill='both')
        msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL)
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        settings = Frame(self, style='Settings.TFrame', width=500, height=720)
        settings.grid(row=0, column=1)
        settings.columnconfigure(0, weight=1)
        settings.rowconfigure(0, weight=1)
        
        buttons = Frame(self, style='Buttons.TFrame', width=500, height=240)
        buttons.grid(row=1, column=1)
        buttons.columnconfigure(0, weight=1)
        buttons.rowconfigure(0, weight=1)




        

