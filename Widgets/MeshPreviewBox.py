
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
import sys
from Widgets.ZoomCanvas import *
from Widgets.ImgFileLoad import ImgFileLoad

import json
from tkinter import filedialog

class MeshPreviewBox(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)

        self.raw_img = None
        self.preview_img_size = preview_img_size
        self.controller = None
        # Image File Loading Widget
        self.img_load = ImgFileLoad(self, self.load_img)
        self.img_load.pack(side='top')
        
        # Preview Image Widget
        self.canvas_frame = Frame(self)
        self.canvas_frame.pack(side='top', expand=1, fill='x')
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.canvas = Zoom_Advanced(self.canvas_frame, self.preview_img)
      

    def load_img(self):        
        if self.controller:
            self.preview_img = Image.fromarray(self.img_load.image)
            self.raw_img = self.img_load.image
            self.canvas.update_image(Image.fromarray((self.img_load.image).astype(np.uint8)))
            # self.canvas.update()
            # self.canvas.scale_to_canvas()
            msg_output = f'Mesh image loaded from {self.img_load.img_path.get()}\n'
            msg_output += f'Mesh resolution: {self.raw_img.shape[1]}x{self.raw_img.shape[0]}'
            self.controller.msg_box.console(msg_output)
        return
    
    def update_img(self, img):
        self.preview_img = Image.fromarray(img) 
        self.canvas.update_image(self.preview_img)
        msg_output = f'Mesh image updaded'
        self.controller.msg_box.console(msg_output)
        return
    


if __name__=='__main__':
    
    
    root = tk.Tk()
    preview_img_size = (960, 720)
    mp_box = MeshPreviewBox(root, preview_img_size)
    mp_box.pack()
    root.mainloop()


         