from msilib.schema import Control
# import tkinter as tk
from tkinter.ttk import *
from Frames.Distortion import PRESET_PATH
from Widgets.MsgBox import MsgBox
from Widgets.ParameterTab import *
from Frames.NetsFrame import NetsFrame
from Widgets.PathBrowse import PathBrowse
from Widgets.ToggleBtn import ToggleBtn
from functools import partial
from PIL import Image
from NED_Analyzer import SMTF_Eval
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import time

PRESET_PATH = '.\\Presets\\smtf_default.json'
OUTPUT_PATH = '.\\Output\\'
MTF_TEMP_PATH = '.\\Temp\\mtf_roi\\'
MTF_PATTERN_TEMP_PATH = '.\\Temp\\MTF_Pattern\\'

class SMTF(NetsFrame):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)

        self.se_paras = {}
        self.mtf_paras = {}
        self.output_paras = {}
        self.smtf_eval = None
        self.mtf_roi_coord = None
        self.pattern_size = None
        self.extracted_img = None
        self.preview_img = None
        self.pre_preview_img = None
        self.mtf_mesh = None
        self.mtf_coords = None
        self.disabled_btns = []        

        # Parameter Tables
        # MTF Pattern Extraction
        mtf_extract_frame = LabelFrame(self.settings, text='MTF Pattern Extraction')
        mtf_extract_frame.pack(side='top', fill='x', pady=5)
        self.se_pattern_paras_tab = ParameterTab(mtf_extract_frame, self.se_paras)        
        self.se_pattern_paras_tab.pack(side='top', expand=1, fill='x')
        self.mtf_extract_btn = ttk.Button(mtf_extract_frame, text='Extract Pattern', command=self.mtf_extract)
        self.mtf_extract_btn.pack(side='right', padx=2, pady=5)
        self.mtf_extract_btn.config(state='disable')
        self.disabled_btns.append(self.mtf_extract_btn)
        self.mtf_extract_preview_btn = ToggleBtn(mtf_extract_frame, on_txt='Preview On', off_txt='Preview off', on_cmd=partial(self.mtf_extract_preview, True), off_cmd=partial(self.mtf_extract_preview, False))
        self.mtf_extract_preview_btn.pack(side='right', padx=2, pady=5)
        self.mtf_extract_preview_btn.config(state='disable')
        self.disabled_btns.append(self.mtf_extract_preview_btn)


        # MTF Evaluation
        mtf_eval_frame = LabelFrame(self.settings, text='MTF Evaluation')
        mtf_eval_frame.pack(side='top', fill='x', pady=5)
        self.mtf_paras_tab = ParameterTab(mtf_eval_frame, self.mtf_paras)        
        self.mtf_paras_tab.pack(side='top', expand=1, fill='x')
        self.mtf_eval_btn = ttk.Button(mtf_eval_frame, text='Evaluate MTF', command=self.mtf_evaluate)
        self.mtf_eval_btn.pack(side='right', padx=2, pady=5)
        self.mtf_eval_btn.config(state='disable')
        self.disabled_btns.append(self.mtf_eval_btn)
        self.mtf_eval_preview_btn = ToggleBtn(mtf_eval_frame, on_txt='Preview On', off_txt='Preview off', on_cmd=partial(self.mtf_eval_preview, True), off_cmd=partial(self.mtf_eval_preview, False))
        self.mtf_eval_preview_btn.pack(side='right', padx=2, pady=5)
        self.mtf_eval_preview_btn.config(state='disable')
        self.disabled_btns.append(self.mtf_eval_preview_btn)
       
        # output
        
        self.output_path = PathBrowse(self.settings)
        self.output_path.pack(side='top', expand=1, fill='x')
        
        output_frame = LabelFrame(self.settings, text='Evaluation Result Output')
        output_frame.pack(side='top', fill='x', pady=5)
        self.output_paras_tab = ParameterTab(output_frame, self.output_paras)
        self.output_paras_tab.pack(side='top', expand=1, fill='x')
        self.export_btn = ttk.Button(output_frame, text='Export Results', command=self.export)
        self.export_btn.pack(side='right', padx=2, pady=5)
        self.export_btn.config(state='disable')
        self.disabled_btns.append(self.export_btn)
        self.get_mtf_mesh_btn = ttk.Button(output_frame, text='Get MTF Mesh', command=self.get_mtf_mesh)
        self.get_mtf_mesh_btn.pack(side='right', padx=2, pady=5)
        self.get_mtf_mesh_btn.config(state='disable')
        self.disabled_btns.append(self.get_mtf_mesh_btn)
        self.get_mtf_grid_btn = ttk.Button(output_frame, text='Get MTF Grid', command=self.get_mtf_grid)
        self.get_mtf_grid_btn.pack(side='right', padx=2, pady=5)
        self.get_mtf_grid_btn.config(state='disable')
        self.disabled_btns.append(self.get_mtf_grid_btn)
        self.show_fov_btn = ToggleBtn(output_frame, on_txt='FoV on', off_txt='FoV off', on_cmd=partial(self.show_fov, True), off_cmd=partial(self.show_fov, False))
        self.show_fov_btn.pack(side='right', padx=2, pady=5)
        self.show_fov_btn.config(state='disable')
        self.disabled_btns.append(self.show_fov_btn)
        self.get_fov_btn = ttk.Button(output_frame, text='Get FoV', command=self.get_fov_bbox)
        self.get_fov_btn.pack(side='right', padx=2, pady=5)
        
        # widget interlink & initialization
        self.controller = Controller(self.msg_box, self.img_file_load, self.preset_file_load, self.output_path, self.preview_canvas)

        linked_tabs = {'se_paras':self.se_pattern_paras_tab,
                       'mtf_paras':self.mtf_paras_tab,
                       'output_paras':self.output_paras_tab,                       
                      }

        self.preset_file_load.init_linked_tabs(linked_tabs)
        self.preset_file_load.preset_path.set(PRESET_PATH)
        self.preset_file_load.load_preset()   
        self.se_pattern_paras_tab.fit_height()
        self.mtf_paras_tab.fit_height()
    
    
    def get_mtf_grid(self):
        fov_anchor, fov_dim, grid_dim, mesh_dim, interpolation = self.output_paras_tab.output_parsed_vals()       
        fov_anchor = np.array(fov_anchor) + self.smtf_eval.pattern_size * 0.5
        fov_dim = np.array(fov_dim) - self.smtf_eval.pattern_size
        mtf_grid_x = np.linspace(fov_anchor[0], fov_dim[0] + fov_anchor[0], grid_dim[0])
        mtf_grid_y = np.linspace(fov_anchor[1], fov_dim[1] + fov_anchor[1], grid_dim[1])
        mtf_grid_xx, mtf_grid_yy = np.meshgrid(mtf_grid_x, mtf_grid_y)
        mtf_grid_coords = np.vstack((mtf_grid_xx.flatten(), mtf_grid_yy.flatten())).T
        
        self.mtf_coords = np.array(self.smtf_eval.pick_list)[:, 0:2] + self.smtf_eval.pattern_size * 0.5
        self.mtf_vals = np.array(self.smtf_eval.mtf_value_list)        
        mtf_coords_kdtree = KDTree(self.mtf_coords)               
        
        for i in range(grid_dim[0] * grid_dim[1]):
            dist, _= mtf_coords_kdtree.query((mtf_grid_coords[i, 0], mtf_grid_coords[i, 1]))
            if dist > self.smtf_eval.pattern_size * 0.5:
                # ax.scatter(x=(mtf_grid_coords[i, 0]), y=(mtf_grid_coords[i, 1]), c='red')
                self.mtf_coords = np.append(self.mtf_coords, np.atleast_2d(mtf_grid_coords[i, :]), axis=0)
                self.mtf_vals = np.append(self.mtf_vals, np.atleast_1d(0), axis=0) 
        px = 1/plt.rcParams['figure.dpi']
        fig, ax = plt.subplots(figsize=(grid_dim[0] * 25 * px, grid_dim[1] * 25 * px))
        
        mtf_plot = ax.scatter(x=self.mtf_coords[:, 0], y=self.mtf_coords[:, 1], c=self.mtf_vals[:])
        self.get_mtf_mesh_btn.config(state='active')
        # asp = abs(np.diff(ax.get_ylim())[0] / np.diff(ax.get_xlim())[0])
        # asp = abs(grid_dim[1] / grid_dim[0])
        # ax.set_aspect(asp)
        ax.set_ylim(ax.get_ylim()[::-1])
        ax_colorbar = fig.add_axes()
        plt.colorbar(mtf_plot, ax_colorbar)
        plt.show()


    def get_mtf_mesh(self):
        fov_anchor, fov_dim, grid_dim, mesh_dim, interpolation = self.output_paras_tab.output_parsed_vals()       
        fov_dim = np.array(fov_dim) - self.smtf_eval.pattern_size
        fov_anchor = np.array(fov_anchor) + self.smtf_eval.pattern_size * 0.5
        
        mesh_x = np.linspace(fov_anchor[0], fov_dim[0] + fov_anchor[0], mesh_dim[0])
        mesh_y = np.linspace(fov_anchor[1], fov_dim[1] + fov_anchor[1], mesh_dim[1])
        mesh_xx, mesh_yy = np.meshgrid(mesh_x, mesh_y)
        
        self.mtf_mesh = griddata(self.mtf_coords, self.mtf_vals, (mesh_xx, mesh_yy), method=interpolation)
        
        px = 1/plt.rcParams['figure.dpi']
        fig, ax = plt.subplots(figsize=(grid_dim[0] * 25 * 1.125 * px, grid_dim[1] * 25 * px))
        mtf_mesh_plot = ax.imshow(self.mtf_mesh, aspect='auto', interpolation='nearest', extent=(fov_anchor[0], fov_dim[0] + fov_anchor[0], fov_dim[1] + fov_anchor[1], fov_anchor[1]), origin='upper')
        # ax_colorbar = fig.add_subplot(111)
        ax_colorbar = fig.add_axes()
        plt.colorbar(mtf_mesh_plot, ax_colorbar)        
        plt.show()


    def mtf_extract(self):
        edge_angle, self.pattern_size, line_type, reverse, method, threshold, iou_thresh = self.se_pattern_paras_tab.output_parsed_vals()
        self.smtf_eval.pattern_size = self.pattern_size
        self.smtf_eval.get_se_patterns(edge_angle, self.pattern_size, line_type, reverse, method, threshold, iou_thresh)
        self.extracted_label_img = Image.fromarray((self.smtf_eval.extracted_label_im).astype(np.uint8))
        if self.mtf_extract_preview_btn.toggle_stat:
            self.preview_canvas.update_image(self.extracted_label_img)
        self.mtf_extract_preview_btn.config(state='active')
        self.mtf_eval_btn.config(state='active')
        self.show_fov_btn.config(state='active')
        pass

    def mtf_evaluate(self):
        pixel_size, threshold, mtf_contrast, font_scale, thickness = self.mtf_paras_tab.output_parsed_vals()
        self.smtf_eval.set_mtf_analysis_paras(pixel_size, threshold, mtf_contrast)
        self.smtf_eval.get_mtf_mesh(font_scale, thickness)
        self.mtf_eval_preview_btn.config(state='active')        
        self.extracted_label_img = Image.fromarray((self.smtf_eval.extracted_label_im).astype(np.uint8))
        coords = np.array(self.smtf_eval.pick_list)
        mtf_vals = np.array(self.smtf_eval.mtf_value_list)
        np.save('coords.npy', coords)        
        np.save('mtf_vals.npy', mtf_vals)        
        self.get_mtf_grid_btn.config(state='active')
        self.export_btn.config(state='active')
        pass

    def mtf_extract_preview(self, preview):
        if preview:
            self.preview_canvas.update_image(self.extracted_label_img)
        else:
            self.preview_canvas.update_image(self.preview_img)
        return

    def mtf_eval_preview(self, preview):
        if preview:
            self.preview_canvas.update_image(self.extracted_label_img)
        else:
            self.preview_canvas.update_image(self.preview_img)
        return
    
    def show_fov(self, preview):
        if preview:
            self.pre_preview_img = self.preview_canvas.image
            fov_anchor, fov_dim, _, _, _ = self.output_paras_tab.output_parsed_vals()
            fov_anchor = np.array(fov_anchor)
            fov_dim = np.array(fov_dim)
            fov_pt1 = fov_anchor
            fov_pt2 = fov_anchor + fov_dim        
            if self.smtf_eval.extracted_label_im is not None:
                fov_preview_im = self.smtf_eval.extracted_label_im.copy()
            else:
                fov_preview_im = self.preview_im.copy()
            cv2.rectangle(fov_preview_im, fov_pt1, fov_pt2, color=(0, 255, 0), thickness=2)
            fov_preview_img = Image.fromarray((fov_preview_im).astype(np.uint8))
            self.preview_canvas.update_image(fov_preview_img)
        else:
            self.preview_canvas.update_image(self.pre_preview_img)
        return
    
    def export(self):
        output_path = self.output_path.output_path.get()
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        if len(output_path) > 0:
            if self.smtf_eval.extracted_label_im is not None:
                cv2.imwrite(output_path + f'Labeled_Image_{timestr}.png', self.smtf_eval.extracted_label_im)
                self.controller.msg_box.console(f'Labeled image exported at {output_path}Labeled_Image_{timestr}.png')
            if self.mtf_coords is not None and self.mtf_vals is not None:
                np.save(output_path + f'MTF Grid Coordinates_{timestr}.npy', self.mtf_coords)
                self.controller.msg_box.console(f'MTF grid coordinate exported at {output_path}MTF Grid Coordinates_{timestr}.npy')
                np.save(output_path + f'MTF Grid Values_{timestr}.npy', self.mtf_vals)
                self.controller.msg_box.console(f'MTF grid value exported at {output_path}MTF Grid Values_{timestr}.npy')
            if self.mtf_mesh is not None:
                np.save(output_path + f'MTF Mesh_{self.mtf_mesh.shape[1]}x{self.mtf_mesh.shape[0]}_{timestr}.npy', self.mtf_mesh)
                self.controller.msg_box.console(f'MTF mesh exported at {output_path}MTF Mesh_{self.mtf_mesh.shape[1]}x{self.mtf_mesh.shape[0]}_{timestr}.npy')
        else:
            messagebox.showerror('Output Path Error', 'Output path not specified!')
            return    

    def load_img(self):       
        self.raw_im = self.img_file_load.im
        if len(self.raw_im.shape) > 2:
            messagebox.showerror('Incorrect Image Format', 'Only grayscale image is allowed for the analysis!')
            return
        self.preview_im = self.raw_im.copy()       
        # self.preview_im = (self.preview_im // (self.preview_im.max() / 256 + 1)).astype('uint8')
        self.preview_im = cv2.normalize(self.raw_im, self.preview_im, 255, 0, cv2.NORM_INF)
        self.preview_im = cv2.cvtColor(self.preview_im, cv2.COLOR_GRAY2RGB)
        self.preview_img = Image.fromarray((self.preview_im).astype(np.uint8))
        self.preview_canvas.update_image(self.preview_img)        
        msg_output = f'Image loaded from {self.img_file_load.img_path.get()}\n'
        msg_output += f'Image Resolution: {self.raw_im.shape[1]}x{self.raw_im.shape[0]}'        
        self.controller.msg_box.console(msg_output)
        self.smtf_eval = SMTF_Eval(MTF_TEMP_PATH, MTF_PATTERN_TEMP_PATH)
        self.smtf_eval.raw_im = self.raw_im
        self.smtf_eval.set_controller(self.controller)      
        self.disable_btn_group(self.disabled_btns)
        self.mtf_extract_btn.config(state='active')
        
        # test data
        # self.smtf_eval.pick_list = np.load('coords.npy').tolist()
        # self.smtf_eval.mtf_value_list = np.load('mtf_vals.npy').tolist()        
        # self.smtf_eval.pattern_size = 50
        # self.mtf_coords = np.array(self.smtf_eval.pick_list)[:, 0:2] + self.smtf_eval.pattern_size * 0.5
        # self.mtf_vals = np.array(self.smtf_eval.mtf_value_list)
        return

    def get_fov_bbox(self):
        mtf_grid_coords_1 = np.array(self.smtf_eval.pick_list.copy())
        mtf_grid_coords_2 = mtf_grid_coords_1.copy() + self.smtf_eval.pattern_size
        mtf_grid_coords = np.vstack([mtf_grid_coords_1[:, 0:2], mtf_grid_coords_2[:, 0:2]])
        fov_bbox = cv2.boundingRect(mtf_grid_coords.astype('float32'))
        output_msg = f'FoV Anchor: ({fov_bbox[0]}, {fov_bbox[1]})\n'
        output_msg += f'FoV Dimenstion: {fov_bbox[2]}, {fov_bbox[3]}'
        self.controller.msg_box.console(output_msg)
        self.output_paras_tab.submit_value('FoV Anchor', f'{fov_bbox[0]},{fov_bbox[1]}')
        self.output_paras_tab.submit_value('FoV Dimension', f'{fov_bbox[2]}x{fov_bbox[3]}')
        return

class Controller():
    def __init__(self, msg_box, img_file_load, preset_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path
        self.img_load = img_file_load
        self.preview_canvas = preview_canvas