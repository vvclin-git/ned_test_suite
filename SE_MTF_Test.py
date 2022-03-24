
import cv2
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image

from Widgets.ParameterTab import *
from Widgets.MeshPreviewBox import *
from Widgets.MsgBox import *

parameters = {             
            "Edge Angle": {"value": 5, "type": "value", "options": None}, 
            "Pattern Size": {"value": 80, "type": "value", "options": None},            
            "Line Type": {"value": "line_8", "type": "list", "options": ["line_8", "line_4", "line_AA", "filled"]},
            "Threshold": {"value": 0.5, "type": "value", "options": None},
            "Min. Radius": {"value": 5, "type": "value", "options": None}
            } 

class SE_MTF_Test(MeshPreviewBox):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        self.paras_tab = ParameterTab(self, parameters)
        self.paras_tab.pack(side='top', expand=1, fill='x')
        self.paras_tab.fit_height()
        self.extract_patterns_btn = Button(self, text='Extract Patterns', command=self.get_se_patterns)
        self.extract_patterns_btn.pack(side='top')
        self.msg_box = MsgBox(self)
        self.msg_box.pack(side='left', expand=1, fill='both')
        self.controller = Controller(self.paras_tab, self.msg_box)
        self.set_controller(self.controller)

    def draw_se_MTF_pattern(self, edge_angle, pattern_size, line_type):    
        chart_im = np.zeros((pattern_size, pattern_size, 3))
        center = (np.array(chart_im.shape[0:2]) * 0.5).astype('uint')
        anchor = center - 0.5 * pattern_size
        pt1 = anchor + np.array([0, pattern_size])
        pt2 = pt1 + np.array([0.5 * pattern_size * (1 - np.tan(np.radians(edge_angle))), 0])
        pt3 = pt2 + np.array([0.5 * pattern_size * (np.tan(np.radians(edge_angle))), -pattern_size])    
        pts = np.array([anchor, pt1, pt2, pt3, anchor]).astype('int32')
        pts = np.expand_dims(pts, axis=1)  
        cv2.fillPoly(chart_im, [pts], color=(255, 255, 255), lineType=line_type)
        return chart_im

    def get_se_patterns(self):
        edge_angle, pattern_size, line_type, threshhold, min_radius = self.paras_tab.output_parsed_vals()
        se_pattern_im = self.draw_se_MTF_pattern(edge_angle, pattern_size, line_type)
        self.labeled_img = self.raw_img.copy()
        stat = cv2.imwrite('se_pattern.png', se_pattern_im)
        se_pattern = cv2.imread('se_pattern.png')
        print(stat)
        res_se_pattern = cv2.matchTemplate(self.labeled_img, se_pattern, cv2.TM_CCOEFF_NORMED)
        
        
        loc = np.where(res_se_pattern >= threshhold)
        
        i = 0
        for pt in zip(*loc[::-1]):
            cv2.rectangle(self.labeled_img, pt, (pt[0]+pattern_size, pt[1]+pattern_size), (0,255,255), 1)

            i += 1
        cv2.imwrite('labeled.png', self.labeled_img)
        print(i)
        self.update_img(self.labeled_img)
        self.controller.msg_box.console(f'{len(loc[0])} SE MTF patterns founded')
  
    def group_locations(self, locations, min_radius):
        x = locations[:, 0]
        dist_x = x - x.T
        y = locations[:, 1]
        dist_y = y - y.T
        dist = np.sqrt(dist_x**2 + dist_y**2)
        np.fill_diagonal(dist, min_radius+1)
        too_close = np.nonzero(dist <= min_radius)
        groups = []
        points = np.arange(len(locations))
        i = 0
        j = 0
        while i < len(points):
            groups.append([points[i]])
            for j in range(len(too_close[0])):
                if too_close[0][j] == points[i]:
                    groups[i].append(too_close[1][j])
                    points = np.delete(points, np.nonzero(points == too_close[1][j]))
            i += 1

        new_locations = []
        for group in groups:
            new_locations.append(np.mean(locations[group], axis=0))

        return np.array(new_locations)


class Controller():
    def __init__(self, paras_tab, msg_box):
        self.paras_tab = paras_tab
        self.msg_box = msg_box
        pass

if __name__=='__main__':
    root = tk.Tk()
    preview_img_size = (1600, 1200)
    test = SE_MTF_Test(root, preview_img_size)
    test.pack(expand=1, fill='both')
    root.mainloop()