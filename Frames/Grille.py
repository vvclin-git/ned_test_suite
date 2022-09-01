import imp
from Frames.NetsFrame import *
from Widgets.ParameterTab import *
import os
from tkinter import filedialog
from NED_Analyzer import *
import re
import time
import json
from tkinter.ttk import *
from Widgets.ToggleBtn import *
import matplotlib
from matplotlib import pyplot as plt
from functools import partial

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\Presets\\grille_default.json'
MESH_OUTPUT_PATH = f'{os.getcwd()}\\Output'

class Grille(NetsFrame):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        f = open(PRESET_PATH, 'r')
        self.presets = json.load(f)
        f.close()
        self.grille_eval = Grille_Eval()
        self.grille_grid_paras = self.presets['grille_grid_paras']
        self.buttons = []              

        # Grille Analysis Settings
        self.grille_grid_frame = LabelFrame(self.settings, text='Grille Merit Grid Settings', padding=(5, 5, 5, 5))
        self.grille_grid_frame.pack(expand=True, fill='x', pady=5, side='top')
        
        self.grille_grid_settings = ParameterTab(self.grille_grid_frame, self.grille_grid_paras)
        self.grille_grid_settings.fit_height()
        self.grille_grid_settings.pack(expand=True, fill='x', pady=5, side='top')

        self.grille_grid_btn_frame = Frame(self.grille_grid_frame)
        self.grille_grid_btn_frame.pack(side='top', expand=True, fill='both')
                
        self.grille_grid_btn = Button(self.grille_grid_btn_frame, text='Generate Grid', style='Buttons.TButton', command=self.gen_mc_grid)
        self.grille_grid_btn.pack(side='right', padx=2, pady=5)
        
        self.grille_get_fov_btn = Button(self.grille_grid_btn_frame, text='Get FoV Area', style='Buttons.TButton', command=self.get_fov_bbox)
        self.grille_get_fov_btn.pack(side='right', padx=2, pady=5)

        self.grille_grid_btn_list = [self.grille_grid_preview_btn, self.grille_grid_btn]
        self.buttons.append(self.grille_grid_btn_list)

        # Output Path
        self.output_path = PathBrowse(self.settings)
        self.output_path.pack(expand=1, fill='x', pady=5) 
        # Grille Contrast Analysis
        self.grille_analysis_frame = LabelFrame(self.settings, text='Grille Contrast Analysis', padding=(5, 5, 5, 5))
        self.grille_analysis_frame.pack(side='top', expand=True, fill='x', pady=10)
        
        self.show_mesh_frame = Frame(self.grille_analysis_frame)
        self.show_mesh_frame.pack(side='top', expand=True, fill='x')        
              
        self.save_mesh_btn = Button(self.show_mesh_frame, text='Save Mesh', command=self.save_mesh)
        self.save_mesh_btn.pack(side='right', padx=2, pady=5)
        
        self.show_mesh_btn = Button(self.show_mesh_frame, text='Show Mesh', command=self.show_grille_mesh)
        self.show_mesh_btn.pack(side='right', padx=2, pady=5)

        self.grille_analyze_btn = Button(self.show_mesh_frame, text='Evaluate', command=self.grille_evaluate)
        self.grille_analyze_btn.pack(side='right', padx=2, pady=5)
        
        # self.grille_analysis_btn_list = [self.mesh_output_btn, self.save_mesh_btn, self.show_mesh_btn, self.grille_analyze_btn]
        # self.buttons.append(self.grille_analysis_btn_list)
        
        # self.reset()

        # Widget Initialization
        # self.grille_eval.raw_im = self.img_file_load.image

        self.controller = Controller(self.msg_box, self.preset_file_load, self.img_file_load, self.output_path, self.preview_canvas)

        linked_tabs = {'grille_grid_paras':self.grille_grid_paras}

        self.preset_file_load.init_linked_tabs(linked_tabs)
        self.preset_file_load.preset_path.set(PRESET_PATH)
        self.preset_file_load.load_preset()
        self.preset_file_load.set_controller(self.controller)    

    def gen_mc_grid(self):        
        self.grille_eval.raw_im = self.img_file_load.im
        self.grille_eval.preview_im = self.preview_im
        grille_grid_paras = self.grille_grid_settings.output_parsed_vals()
        output_msg = self.grille_eval.gen_mc_grid(*grille_grid_paras[2::])
        self.preview_canvas.add_overlay(self.grille_eval.labeled_im, 'Grille Mesh')
        self.controller.msg_box.console(output_msg)
        self.grille_analyze_btn.config(state='enable')
        return
    
    def grille_evaluate(self):
        output_msg = self.grille_eval.grille_eval()
        self.controller.msg_box.console(output_msg)
        # self.enable_btn_group(self.grille_analysis_btn_list)
        return

    def show_grille_mesh(self):
        grille_mc_mesh = self.grille_eval.grille_mc
        grille_grid_paras = self.grille_grid_settings.output_parsed_vals()
        grid_dim = grille_grid_paras[4]
        chart_res = grille_grid_paras[3]
        title = 'Grille Contrast'
        fig, _ = self.plot_coords_mesh(title, grille_mc_mesh, grid_dim, chart_res, 0, 1, 'coolwarm')
        fig.show()
        return
    
    def plot_coords_mesh(self, title, coords_val, grid_dim, chart_res, vmax, vmin, cmap='viridis'):        
        fig, ax = plt.subplots()            
        ax.set_title(title)
        x = np.linspace(0, chart_res[0], grid_dim[0])
        y = np.linspace(0, chart_res[1], grid_dim[1])
        xx, yy = np.meshgrid(x, y)
        coords_val_mesh = coords_val.reshape((grid_dim[1], grid_dim[0]))    
        # c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin)        
        c = ax.imshow(coords_val_mesh)
        fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
        return fig, ax
    
    def save_mesh(self):
        if self.grille_eval.grille_mc is None:
            output_msg = f'Merit mesh not available!'
            self.controller.msg_box.console(output_msg)
            return
        output_path = self.output_path.get_path()
        if len(output_path) == 0:
            self.controller.msg_box.console('No file output, output path not specified')
            return
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        filename = f'Grille Contrast Mesh_{timestr}'
        # np.save(self.output_path.output_path + filename, self.grille_eval.grille_mc)
        np.save(f'{output_path}\\{filename}', self.grille_eval.grille_mc)
        output_msg = f'Mesh file {filename} saved'
        self.controller.msg_box.console(output_msg)
        return
    
    def get_fov_bbox(self):
        grille_grid_paras = self.grille_grid_settings.output_parsed_vals()
        min_threshold = grille_grid_paras[0]
        max_threshold = grille_grid_paras[1]
        # thresh = np.zeros_like(self.grille_eval.raw_im)
        raw_im_norm = np.zeros_like(self.raw_im)
        raw_im_norm = cv2.normalize(self.raw_im, raw_im_norm, 255, 0, cv2.NORM_INF)
        _, thresh = cv2.threshold(raw_im_norm, min_threshold, max_threshold, cv2.THRESH_TOZERO)
        fov_bbox = cv2.boundingRect(thresh.astype('uint8'))
        output_msg = f'FoV Anchor: ({fov_bbox[0]}, {fov_bbox[1]})\n'
        output_msg += f'FoV Dimenstion: {fov_bbox[2]}, {fov_bbox[3]}'
        
        fov_bbox_overlay = np.zeros_like(self.raw_im)
        fov_bbox_overlay = cv2.cvtColor(fov_bbox_overlay, cv2.COLOR_GRAY2BGR).astype('uint8')
        bbox_pt1 = (fov_bbox[0], fov_bbox[1])
        bbox_pt2 = (fov_bbox[0] + fov_bbox[2], fov_bbox[1] + fov_bbox[3])
        cv2.rectangle(fov_bbox_overlay, bbox_pt1, bbox_pt2, color=(0, 255, 0), thickness=1)
        self.preview_canvas.add_overlay(fov_bbox_overlay, 'Field of View')
        self.controller.msg_box.console(output_msg)
        self.grille_grid_settings.submit_value('Field of View Anchor', f'{fov_bbox[0]},{fov_bbox[1]}')
        self.grille_grid_settings.submit_value('Field of View Dimension', f'{fov_bbox[2]}x{fov_bbox[3]}')        
        return


class Controller():
    def __init__(self, msg_box, preset_file_load, img_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path
        self.img_file_load = img_file_load
        self.preview_canvas = preview_canvas