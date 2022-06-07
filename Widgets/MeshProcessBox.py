
from Widgets.MeshPreviewBox import MeshPreviewBox
import cv2
import numpy as np
import tkinter as tk
from tkinter.ttk import *
from PIL import Image
from Widgets.ParameterTab import ParameterTab
from Widgets.ToggleBtn import ToggleBtn

# parameters = {'Blur Kernel Size': {'value':1, 'type':'value', 'options':None},
#               'Threshold Value': {'value':50, 'type':'value', 'options':None},
#               'Max Threshold Value': {'value':100, 'type':'value', 'options':None},
#               'Contour Approx Epsilon': {'value':0.1, 'type':'value', 'options':None},
#               }

class MeshProcessBox(MeshPreviewBox):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        
        self.controller = None
        # processed data storage
        self.border_coords = None
        self.preview_img = None
        self.preview = False
        self.parameters = {}
        
        # Widgets        
        # self.process_frame = Frame(self)
        # self.process_frame.pack(side='top', expand=1, fill='x')
        self.process_paras_tab = ParameterTab(self, self.parameters)
        # self.process_paras_tab.tree.configure(height=len(parameters))
        self.process_paras_tab.pack(side='top', expand=1, fill='x')

        # self.process_btn_frame = Frame(self)
        # self.process_btn_frame.pack(side='top', expand=1, fill='x')
        # self.set_mesh_btn = Button(self.process_btn_frame, text='Set Mesh', command=self.set_mesh)
        # self.set_mesh_btn.pack(side='right')
        self.preview_btn = ToggleBtn(self, 'Preview On', 'Preview Off', self.preview_on, self.preview_off)
        self.preview_btn.pack(side='right', padx=(2, 0))
        self.process_btn = Button(self, text='Process', command=self.process_mesh)
        self.process_btn.pack(side='right', padx=2)
        

    def process_mesh(self):        
        process_paras = self.process_paras_tab.output_parsed_vals()
        kernel_size, threshold_val, max_threshold_val, epsilon = process_paras        
        self.preview_img = self.preview_img.copy()
        self.raw_img = self.preview_img.copy()
        # self.preview_img = cv2.cvtColor(self.raw_img, cv2.COLOR_GRAY2RGB)
        # if self.preview_img.dtype != 'uint8':
        #     self.preview_img = self.preview_img.astype('uint8')
        mesh_blurred = self.mesh_load.mesh.copy()
        if kernel_size > 0 and (kernel_size + 1) % 2 == 0:
            mesh_blurred = cv2.medianBlur(self.mesh_load.mesh, kernel_size)        
        # thresholding
        _, thresh = cv2.threshold(mesh_blurred, threshold_val, max_threshold_val, cv2.THRESH_BINARY)
        if thresh.dtype != 'uint8':
            thresh = thresh.astype('uint8')
        # find border
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        peris = [cv2.arcLength(c, True) for c in contours]        
        approx_contours = [cv2.approxPolyDP(contours[i], epsilon * peris[i], True) for i in range(len(contours))]
        approx_contours.sort(key=lambda c: cv2.contourArea(c), reverse=True)        
        self.border_coords = np.zeros((len(approx_contours[0]), len(approx_contours[0][0][0]) + 1))
        self.border_coords[:, 0:2] = np.squeeze(approx_contours[0])
        contour_im = np.zeros_like(mesh_blurred)
        contour_im = np.dstack([contour_im, contour_im, contour_im])
        cv2.drawContours(contour_im, approx_contours, 0, (0, 255, 0), thickness=2)
        contour_im = np.dstack([contour_im, contour_im[:, :, 1]])
        # contour_im = cv2.cvtColor(contour_im, cv2.COLOR_RGB2RGBA)
        # contour_img = Image.fromarray(contour_im, mode='RGBA')
        contour_img = Image.fromarray(contour_im)        
        self.controller.msg_box.console(f'{len(self.border_coords)} Points Extracted')
        contour_img = contour_img.convert('RGBA')
        self.preview_img = self.preview_img.convert('RGBA')
        self.preview_img = Image.alpha_composite(self.preview_img, contour_img)
        if self.preview:
            self.update_img(self.preview_img)
        return
    
    def preview_on(self):
        if self.preview_img is None:
            return
        self.preview = True
        self.update_img(self.preview_img)

        return

    def preview_off(self):
        if self.preview_img is None:
            return
        self.preview = False
        self.update_img(self.raw_img)
        return
    
    def set_mesh(self):
        return

    def set_controller(self, controller):
        self.controller = controller
        self.process_paras_tab.controller = controller
             
        return