from msilib.schema import Control
import tkinter as tk
from tkinter.ttk import *
from Frames.Distortion import PRESET_PATH
from Widgets.ParameterTab import *
from Frames.NetsFrame2 import NetsFrame2
from Widgets.PathBrowse import PathBrowse
from Widgets.ToggleBtn import ToggleBtn
from functools import partial
from PIL import Image
from NED_Analyzer import SMTF_Eval
import numpy as np

PRESET_PATH = '.\\Presets\\smtf_default.json'
OUTPUT_PATH = '.\\Output\\'
MTF_TEMP_PATH = '.\\Temp\\mtf_roi\\'
MTF_PATTERN_TEMP_PATH = '.\\Temp\\MTF_Pattern\\'

class SMTF(NetsFrame2):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)

        self.se_paras = {}
        self.mtf_paras = {}
        self.smtf_eval = None
        self.mtf_roi_coord = None
        self.pattern_size = None
        self.extracted_img = None
        self.preview_img = None
        self.mtf_extract_btns = []
        self.mtf_eval_btns = []

        # Parameter Tables
        # MTF Pattern Extraction
        mtf_extract_frame = LabelFrame(self.settings, text='MTF Pattern Extraction')
        mtf_extract_frame.pack(side='top', fill='x', pady=5)
        self.se_pattern_paras_tab = ParameterTab(mtf_extract_frame, self.se_paras)        
        self.se_pattern_paras_tab.pack(side='top', expand=1, fill='x')
        self.mtf_extract_btn = Button(mtf_extract_frame, text='Extract Pattern', command=self.mtf_extract)
        self.mtf_extract_btn.pack(side='right', padx=2, pady=5)
        self.mtf_extract_btn.config(state='disable')
        self.mtf_extract_preview_btn = ToggleBtn(mtf_extract_frame, on_txt='Preview On', off_txt='Preview off', on_cmd=partial(self.mtf_extract_preview, True), off_cmd=partial(self.mtf_extract_preview, False))
        self.mtf_extract_preview_btn.pack(side='right', padx=2, pady=5)
        self.mtf_extract_preview_btn.config(state='disable')


        # MTF Evaluation
        mtf_eval_frame = LabelFrame(self.settings, text='MTF Evaluation')
        mtf_eval_frame.pack(side='top', fill='x', pady=5)
        self.mtf_paras_tab = ParameterTab(mtf_eval_frame, self.mtf_paras)        
        self.mtf_paras_tab.pack(side='top', expand=1, fill='x')
        self.mtf_eval_btn = Button(mtf_eval_frame, text='Evaluate MTF', command=self.mtf_evaluate)
        self.mtf_eval_btn.pack(side='right', padx=2, pady=5)
        self.mtf_eval_btn.config(state='disable')
        self.mtf_eval_preview_btn = ToggleBtn(mtf_eval_frame, on_txt='Preview On', off_txt='Preview off', on_cmd=partial(self.mtf_eval_preview, True), off_cmd=partial(self.mtf_eval_preview, False))
        self.mtf_eval_preview_btn.pack(side='right', padx=2, pady=5)
        self.mtf_eval_preview_btn.config(state='disable')

        # output
        self.output_path = PathBrowse(self.settings)
        self.output_path.pack(side='top', expand=1, fill='x')
        
        # widget interlink & initialization
        self.controller = Controller(self.msg_box, self.img_file_load, self.preset_file_load, self.output_path, self.preview_canvas)

        linked_tabs = {'se_paras':self.se_pattern_paras_tab,
                       'mtf_paras':self.mtf_paras_tab,                       
                      }

        self.preset_file_load.init_linked_tabs(linked_tabs)
        self.preset_file_load.preset_path.set(PRESET_PATH)
        self.preset_file_load.load_preset()   
        self.se_pattern_paras_tab.fit_height()
        self.mtf_paras_tab.fit_height()

    def mtf_extract(self):
        edge_angle, self.pattern_size, line_type, method, threshold, iou_thresh = self.se_pattern_paras_tab.output_parsed_vals()
        self.smtf_eval.pattern_size = self.pattern_size
        self.smtf_eval.get_se_patterns(edge_angle, self.pattern_size, line_type, method, threshold, iou_thresh)
        self.extracted_img = Image.fromarray((self.smtf_eval.extracted_im).astype(np.uint8))
        if self.mtf_extract_preview_btn.toggle_stat:
            self.preview_canvas.update_image(self.extracted_img)
        self.mtf_extract_preview_btn.config(state='active')
        self.mtf_eval_btn.config(state='active')
        pass

    def mtf_evaluate(self):
        pixel_size, threshold, mtf_contrast = self.mtf_paras_tab.output_parsed_vals()
        self.smtf_eval.set_mtf_analysis_paras(pixel_size, threshold, mtf_contrast)
        self.smtf_eval.get_mtf_mesh()
        self.mtf_eval_preview_btn.config(state='active')
        self.evaluated_img = Image.fromarray((self.smtf_eval.evaluated_im).astype(np.uint8))

        pass

    def mtf_extract_preview(self, preview):
        if preview:
            self.preview_canvas.update_image(self.extracted_img)
        else:
            self.preview_canvas.update_image(self.preview_img)
        return

    def mtf_eval_preview(self, preview):
        if preview:
            self.preview_canvas.update_image(self.evaluated_img)
        else:
            self.preview_canvas.update_image(self.preview_img)
        return
    
    def load_img(self):
        self.preview_img = Image.fromarray((self.img_file_load.image).astype(np.uint8))
        self.raw_im = self.img_file_load.image
        self.preview_canvas.update_image(self.preview_img)        
        msg_output = f'Image loaded from {self.img_file_load.img_path.get()}\n'
        msg_output += f'Image Resolution: {self.raw_im.shape[1]}x{self.raw_im.shape[0]}'
        self.controller.msg_box.console(msg_output)
        self.smtf_eval = SMTF_Eval(MTF_TEMP_PATH, MTF_PATTERN_TEMP_PATH)
        self.smtf_eval.raw_im = self.raw_im
        self.smtf_eval.set_controller(self.controller)      
        self.mtf_extract_btn.config(state='active')
        self.mtf_extract_preview_btn.config(state='disabled')
        self.mtf_eval_btn.config(state='disabled')
        self.mtf_eval_preview_btn.config(state='disabled') 
        return

class Controller():
    def __init__(self, msg_box, img_file_load, preset_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path
        self.img_load = img_file_load
        self.preview_canvas = preview_canvas