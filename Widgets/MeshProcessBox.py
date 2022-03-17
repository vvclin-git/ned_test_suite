
from Widgets.MeshPreviewBox import MeshPreviewBox
import cv2
import numpy as np
import tkinter as tk
from tkinter.ttk import *

from Widgets.ParameterTab import ParameterTab
from Widgets.ToggleBtn import ToggleBtn

parameters = {'Blur Kernel Size': {'value':1, 'type':'value', 'options':None},
              'Threshold Value': {'value':50, 'type':'value', 'options':None},
              'Max Threshold Value': {'value':100, 'type':'value', 'options':None},
              'Contour Approx Epsilon': {'value':0.1, 'type':'value', 'options':None},
              }

class MeshProcessBox(MeshPreviewBox):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        
        self.controller = None
        # processed data storage
        self.border_coords = None
        self.preview_img = None
        self.preview = False
        
        # Widgets        
        self.process_frame = Frame(self)
        self.process_frame.pack(side='top')
        self.process_paras_tab = ParameterTab(self.process_frame, parameters)
        self.process_paras_tab.tree.configure(height=len(parameters))
        self.process_paras_tab.pack(side='top')

        self.process_btn_frame = Frame(self.process_frame)
        self.process_btn_frame.pack(side='top', expand=1, fill='x')
        self.set_mesh_btn = Button(self.process_btn_frame, text='Set Mesh', command=self.set_mesh)
        self.set_mesh_btn.pack(side='right')
        self.preview_btn = ToggleBtn(self.process_btn_frame, 'Preview On', 'Preview Off', self.preview_on, self.preview_off)
        self.preview_btn.pack(side='right')
        self.process_btn = Button(self.process_btn_frame, text='Process', command=self.process_mesh)
        self.process_btn.pack(side='right')
        

    def process_mesh(self):
        
        process_paras = self.process_paras_tab.output_parsed_vals()
        kernel_size, threshold_val, max_threshold_val, epsilon = process_paras        
        
        self.preview_img = cv2.cvtColor(self.raw_img, cv2.COLOR_GRAY2RGB)
        img = cv2.medianBlur(self.raw_img, kernel_size)        
        # thresholding
        _, thresh = cv2.threshold(img, threshold_val, max_threshold_val, cv2.THRESH_BINARY)
        # find border
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        peris = [cv2.arcLength(c, True) for c in contours]        
        approx_contours = [cv2.approxPolyDP(contours[i], epsilon * peris[i], True) for i in range(len(contours))]
        approx_contours.sort(key=lambda c: cv2.contourArea(c), reverse=True)        
        self.border_coords = np.zeros((len(approx_contours[0]), len(approx_contours[0][0][0]) + 1))
        self.border_coords[:, 0:2] = np.squeeze(approx_contours[0])
        cv2.drawContours(self.preview_img, approx_contours, 0, (0, 255, 0), thickness=2)
        self.controller.msg_box.console(f'{len(self.border_coords)} Points Extracted')
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