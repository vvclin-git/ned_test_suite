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
        
        preview = Frame(self, style='Preview.TFrame', width=960, height=900)        
        
        preview.grid(row=0, column=0, rowspan=2, sticky="NEWS")
        # preview.columnconfigure(0, weight=1)
        # preview.rowconfigure(0, weight=3)
        # preview.rowconfigure(1, weight=1)
        
        img = np.zeros([675, 900, 3], dtype=np.uint8)
        cv2.putText(img, 'Preview Image', (400, 330), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)
        # # cv2.imwrite('img.png', img)
        img = Image.fromarray(img)
        preview_img = ImageTk.PhotoImage(img)        
        
        preview_img_box = tk.Canvas(preview, width=960, height=675)
        # preview_img_box = tk.Canvas(preview, height=10, width=10)
        # preview_img_box.create_text(200, 200, text='test')
        preview_img_box.create_image(0, 0, image=preview_img, anchor=tk.NW)
        # # preview_img_box = Label(preview, borderwidth=2, relief='groove', anchor='center')                   
        preview_img_box.image = preview_img
        preview_img_box.grid(row=0, column=0, sticky=tk.N)
        # preview_img_box.pack(side=tk.TOP)        
        # preview_img_box.pack()
        
        msg_frame = LabelFrame(preview, width=960, height=225, text='Output Message', relief='groove', borderwidth=2)
        msg_frame.grid(row=1, column=0, sticky='NEWS')
        # msg_frame.pack(side=tk.TOP)
        # msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL)
        # msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # msg_output = Label(msg_frame, text='Message Output')
        # msg_output.pack(side=tk.LEFT, fill=tk.BOTH)

        # preview_test = Label(preview, background='red')
        # preview_test.grid(row=0, column=0, sticky='NEWS')
        
        settings = Frame(self, style='Settings.TFrame', width=480, height=675)
        settings.grid(row=0, column=1)
        settings.columnconfigure(0, weight=1)
        settings.rowconfigure(0, weight=1)

        
        buttons = Frame(self, style='Buttons.TFrame', width=480, height=225)
        buttons.grid(row=1, column=1)
        buttons.columnconfigure(0, weight=1)
        buttons.rowconfigure(0, weight=1)




        

