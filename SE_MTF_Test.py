
import cv2
from cv2 import CV_8UC3
import numpy as np
from tkinter.ttk import *
import tkinter as tk
from PIL import Image

from Widgets.ParameterTab import *
from Widgets.MeshPreviewBox import *
from Widgets.MsgBox import *
import json

PRESET_PATH = '.\\Presets\\smtf_default.json'
preset_file = open(PRESET_PATH, 'r')
parameters = json.load(preset_file)["se_paras"]

# parameters = {             
#             "Edge Angle": {"value": 5, "type": "value", "options": None}, 
#             "Pattern Size": {"value": 80, "type": "value", "options": None},            
#             "Line Type": {"value": "cv2.LINE_8", "type": "list", "options": ['cv2.LINE_4', 'cv2.LINE_8', 'cv2.LINE_AA']},
#             "Extract Method": {"value": 'cv2.TM_CCOEFF_NORMED', "type": "list", "options": ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
#             'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']},
#             "Threshold": {"value": 0.95, "type": "value", "options": None},
#             "IoU Threshold": {"value": 0.01, "type": "value", "options": None}
#             } 

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

    def draw_se_pattern(self, edge_angle, pattern_size, line_type, reverse):    
        chart_im = np.zeros((pattern_size, pattern_size, 3))
        center = (np.array(chart_im.shape[0:2]) * 0.5).astype('uint')
        anchor = center - 0.5 * pattern_size
        pt1 = anchor + np.array([0, pattern_size])
        pt2 = pt1 + np.array([0.5 * pattern_size * (1 - np.tan(np.radians(edge_angle))), 0])
        pt3 = pt2 + np.array([0.5 * pattern_size * (np.tan(np.radians(edge_angle))), -pattern_size])    
        pts = np.array([anchor, pt1, pt2, pt3, anchor]).astype('int32')
        pts = np.expand_dims(pts, axis=1)  
        cv2.fillPoly(chart_im, [pts], color=(255, 255, 255), lineType=line_type)
        if reverse:
            chart_rev_im = np.zeros_like(chart_im)
            chart_rev_im[np.where(chart_im == 0)] = 255
            return chart_rev_im
        return chart_im

    def get_se_patterns(self):
        edge_angle, pattern_size, line_type, reverse, method, threshold, iou_thresh = self.paras_tab.output_parsed_vals()
        # method = eval('cv2.TM_CCOEFF_NORMED')
        se_pattern_im = self.draw_se_pattern(edge_angle, pattern_size, line_type, reverse)
        self.labeled_img = self.raw_img.copy()
        self.labeled_img = (self.labeled_img // (self.labeled_img.max() / 256 + 1)).astype('uint8')
        self.labeled_img = cv2.cvtColor(self.labeled_img, cv2.COLOR_GRAY2RGB)
        stat = cv2.imwrite('.\\temp\\se_pattern.png', se_pattern_im)
        se_pattern = cv2.imread('.\\temp\\se_pattern.png')        
        res_se_pattern = cv2.matchTemplate(self.labeled_img, se_pattern, method)       
        
        loc = np.where(res_se_pattern >= threshold)
        loc_value = res_se_pattern[res_se_pattern >= threshold]
        res_box_list = np.zeros((len(loc[0]), 3))
        res_box_list[:, 0] = loc[1]
        res_box_list[:, 1] = loc[0]
        res_box_list[:, 2] = loc_value
        self.res_box_num = len(res_box_list[:, 2])
        self.pick_list = []
        self.nms(res_box_list, iou_thresh, np.array((pattern_size, pattern_size)))
        
        self.controller.msg_box.console('')
        for pt in self.pick_list:
            cv2.rectangle(self.labeled_img, (int(pt[0]), int(pt[1])), (int(pt[0]) + pattern_size, int(pt[1]) + pattern_size), (0,255,255), 1)
        
        cv2.imwrite('labeled.png', self.labeled_img)
       
        self.update_img(self.labeled_img)        
        
        self.controller.msg_box.console(f'{len(self.pick_list)} SE MTF patterns founded')


    def nms(self, res_box_list, iou_thresh, pattern_size):
        
        if res_box_list.size == 0:
            return 
        else:
                     
            res_box_list = res_box_list[np.argsort(res_box_list[:, 2])[::-1]]
            box1 = res_box_list[0, 0:3]
            self.pick_list.append(box1)
            for box2 in res_box_list[1:, 0:3]:
                iou, _, _ = self.iou_calc(box1[0:2], box2[0:2], pattern_size)
                if iou > iou_thresh:
                    box2[2] = 0
            box1[2] = 0
            progress = 1 - (res_box_list[:, 0].size / self.res_box_num)
            msg_output = f'{len(self.pick_list)} pattern extracted, progress: {progress: 3.2%}'            
            self.controller.msg_box.console_update(msg_output)
            
            return self.nms(res_box_list[res_box_list[:, 2] > 0], iou_thresh, pattern_size)

    def iou_calc(self, box1, box2, shape):
        x1, y1 = box1[0], box1[1]
        x2, y2 = box2[0], box2[1]
        if abs(x1-x2) >= shape[0] or abs(y1-y2) >= shape[1]:
            return -1, None, None
        x_inter, y_inter = max(x1, x2), max(y1, y2)    
        coord_inter = np.array((x_inter, y_inter))
        shape_inter = np.array((shape[0] - abs(x1-x2), shape[1] - abs(y1-y2)))
        area_inter = shape_inter[0] * shape_inter[1]
        area_union = (shape[0] * shape[1]) * 2 - area_inter
        iou = area_inter / area_union
        return iou, coord_inter, shape_inter

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