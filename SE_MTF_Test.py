
import cv2
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image

from Widgets.ParameterTab import *
from Widgets.MeshPreviewBox import *

parameters = {             
            "Edge Angle": {"value": 5, "type": "value", "options": None}, 
            "Pattern Size": {"value": 80, "type": "value", "options": None},            
            "Line Type": {"value": "line_8", "type": "list", "options": ["line_8", "line_4", "line_AA", "filled"]}} 

class SE_MTF_Test(MeshPreviewBox):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        self.paras_tab = ParameterTab(self, parameters)
        self.pack(side='top')
        self.extract_patterns_btn = Button(self, text='Extract Patterns', command=None)
        self.extract_patterns_btn.pack(side='top')

    def draw_se_MTF_pattern(self, edge_angle, pattern_size, line_type):    
        chart_im = np.zeros((pattern_size, pattern_size, 3))
        center = (np.array(chart_im.shape) * 0.5).astype('uint')
        anchor = center - 0.5 * pattern_size
        pt1 = anchor + np.array([0, pattern_size])
        pt2 = pt1 + np.array([0.5 * pattern_size * (1 - np.tan(np.radians(edge_angle))), 0])
        pt3 = pt2 + np.array([0.5 * pattern_size * (np.tan(np.radians(edge_angle))), -pattern_size])    
        pts = np.array([anchor, pt1, pt2, pt3, anchor]).astype('int32')
        pts = np.expand_dims(pts, axis=1)  
        cv2.fillPoly(chart_im, [pts], color=(255, 255, 255), lineType=line_type)
        return chart_im

    def get_se_patterns(self):
        edge_angle, pattern_size, line_type = self.paras_tab.output_parsed_vals()
        se_pattern_im = self.draw_se_MTF_pattern(edge_angle, pattern_size, line_type)
        cv2.imwrite('se_pattern.png', se_pattern_im)