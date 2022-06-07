
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
import sys
from Widgets.ZoomCanvas import *
from Widgets.MeshFileLoad import MeshFileLoad

import json
from tkinter import filedialog

class MeshPreviewBox(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)
        
        self.preview_img_size = preview_img_size
        self.controller = None
        # Image File Loading Widget
        self.mesh_load = MeshFileLoad(self, self.load_mesh)
        self.mesh_load.pack(side='top')
        
        # Preview Image Widget
        self.canvas_frame = Frame(self)
        self.canvas_frame.pack(side='top', expand=1, fill='both')
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.canvas = Zoom_Advanced(self.canvas_frame, self.preview_img)
      

    def load_mesh(self):          
        mesh_shape = self.mesh_load.mesh.shape
        if len(mesh_shape) != 2:
            if self.controller:
                msg_output = f'Only 2D mesh is acceptable, no mesh loaded.'                
                self.controller.msg_box.console(msg_output)
            return
        self.mesh_norm = np.zeros_like(self.mesh_load.mesh)
        self.mesh_norm = cv2.normalize(self.mesh_load.mesh, self.mesh_norm, 255, 0, cv2.NORM_MINMAX)
        # self.preview_im = np.dstack([self.mesh_norm, self.mesh_norm, self.mesh_norm])        
        self.preview_im = cv2.applyColorMap(self.mesh_norm.astype('uint8'), cv2.COLORMAP_VIRIDIS)
        self.preview_im = cv2.cvtColor(self.preview_im, cv2.COLOR_BGR2RGB)
        self.preview_img = Image.fromarray(self.preview_im.astype('uint8'))
        
        self.canvas.update_image(self.preview_img)
        # self.canvas.update()
        # self.canvas.scale_to_canvas()
        if self.controller:
            msg_output = f'Mesh loaded from {self.mesh_load.mesh_path.get()}\n'
            msg_output += f'Mesh Dimension: {mesh_shape[1]}x{mesh_shape[0]}'
            self.controller.msg_box.console(msg_output)
        return
    
    def update_img(self, img):
        self.preview_img = img 
        self.canvas.update_image(self.preview_img)
        msg_output = f'Mesh image updated'
        if self.controller:
            self.controller.msg_box.console(msg_output)
        return
    
    def set_controller(self, controller):
        self.controller = controller
    


if __name__=='__main__':
    
    
    root = tk.Tk()
    preview_img_size = (960, 720)
    mp_box = MeshPreviewBox(root, preview_img_size)
    mp_box.pack()
    root.mainloop()


         