
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
from Widgets.ZoomCanvas import *
from Widgets.ImgFileLoad import ImgFileLoad
import os
import json
from tkinter import filedialog

class MeshPreviewBox(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)

        self.canvas_frame = Frame(self)
        self.canvas_frame.pack(side='top')
        self.preview_img_size = preview_img_size
        # Preview Image Widget
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.canvas = Zoom_Advanced(self.canvas_frame, self.preview_img)


        # Image File Loading Widget
        self.img_load = ImgFileLoad(self, self.load_img)
        self.img_load.pack(side='top')

    def load_img(self):
        
        self.canvas.update_image(Image.fromarray((self.img_load.image).astype(np.uint8)))
        return
    


if __name__=='__main__':
    root = tk.Tk()
    preview_img_size = (960, 720)
    mp_box = MeshPreviewBox(root, preview_img_size)
    mp_box.pack()
    root.mainloop()


         