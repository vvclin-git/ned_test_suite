import imp

from numpy import pad
from Frames.NetsFrame2 import *
from Widgets.ParameterTab import *
import os
from tkinter import filedialog
from NED_Analyzer import *
import re
import time
import json
from tkinter.ttk import *
from Widgets.ToggleBtn import *
from Widgets.ImgFileLoad import *
from Widgets.PresetFileLoad import *
from Widgets.PathBrowse import *
import matplotlib
from matplotlib import pyplot as plt
from functools import partial
from PIL import ImageDraw
# from NED_Chart import *

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\Presets\\dist_default.json'
MESH_OUTPUT_PATH = f'{os.getcwd()}\\Output'

class Distortion(NetsFrame2):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        f = open(PRESET_PATH, 'r')
        self.presets = json.load(f)
        f.close()
        self.dist_eval = Distortion_Eval()
        # self.dist_grid_paras = self.presets['dist_grid_paras']        
        self.grid_extract_paras = self.presets['grid_extract_paras']
        self.grid_sort_paras = self.presets['grid_sort_paras']
        
        self.mesh_output_type = tk.IntVar()
        self.mesh_output_type.set(1)        
        # self.raw_img = None
        self.buttons = []       
        self.tmp_canvas_img = None        

        # Grid Extraction Settings
        self.grid_extract_frame = LabelFrame(self.settings, text='Grid Extraction Settings', padding=(5, 5, 5, 5))
        self.grid_extract_frame.pack(expand=True, fill='x', pady=5, side='top')
        
        self.grid_extract_settings = ParameterTab(self.grid_extract_frame, self.grid_extract_paras)
        self.grid_extract_settings.tree.configure(height=6)
        self.grid_extract_settings.pack(expand=True, fill='x', pady=5, side='top')

        self.grid_extract_btn_frame = Frame(self.grid_extract_frame)
        self.grid_extract_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.extract_preview_btn = ToggleBtn(self.grid_extract_btn_frame, 'Preview On', 'Preview Off', self.preview_grid_on, self.preview_grid_off)
        self.extract_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_extract_btn = Button(self.grid_extract_btn_frame, text='Extract Grid', style='Buttons.TButton', command=self.extract_grid)
        self.grid_extract_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_extract_btn_list = [self.extract_preview_btn, self.grid_extract_btn]
        self.buttons.append(self.grid_extract_btn_list)

        # Output Path
        self.output_path = PathBrowse(self.settings)
        self.output_path.pack(expand=1, fill='x', pady=5) 

        # Grid Sorting Settings
        self.grid_sort_frame = LabelFrame(self.settings, text='Grid Sorting / Ideal Grid Settings', padding=(5, 5, 5, 5))
        self.grid_sort_frame.pack(expand=True, fill='x', pady=5, side='top')
        self.grid_sort_settings = ParameterTab(self.grid_sort_frame, self.grid_sort_paras)
        self.grid_sort_settings.tree.configure(height=3)
        self.grid_sort_settings.pack(expand=True, fill='x', pady=5, side='top')
        
        self.grid_sort_btn_frame = Frame(self.grid_sort_frame)
        self.grid_sort_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.export_grid_btn = Button(self.grid_sort_btn_frame, text='Export Grid', command=self.export_grid)
        self.export_grid_btn.pack(side='right', padx=2, pady=5)

        self.gen_std_grid_btn = Button(self.grid_sort_btn_frame, text='Get Std Grid', command=self.get_std_grid)
        self.gen_std_grid_btn.pack(side='right', padx=2, pady=5)

        self.center_preview_btn = ToggleBtn(self.grid_sort_btn_frame, 'Center On', 'Center Off', self.preview_center_on, self.preview_center_off)
        self.center_preview_btn.pack(side='right', padx=2, pady=5)

        self.sort_preview_btn = ToggleBtn(self.grid_sort_btn_frame, 'Index On', 'Index Off', self.preview_sort_on, self.preview_sort_off)
        self.sort_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_sort_btn = Button(self.grid_sort_btn_frame, text='Sort Grid', style='Buttons.TButton', command=self.sort_grid)
        self.grid_sort_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_sort_btn_list = [self.sort_preview_btn, self.grid_sort_btn]
        self.buttons.append(self.grid_sort_btn_list)

              

        # Distortion Analysis
        self.dist_analysis_frame = LabelFrame(self.settings, text='Distortion Analysis', padding=(5, 5, 5, 5))
        self.dist_analysis_frame.pack(side='top', expand=True, fill='x', pady=5)

        self.show_mesh_frame = Frame(self.dist_analysis_frame)
        self.show_mesh_frame.pack(side='right', expand=True, fill='x')        
        
        self.mesh_rbtn_frame = Frame(self.dist_analysis_frame)
        self.mesh_rbtn_frame.pack(side='left', expand=True, fill='x') 
        self.mesh_rbtn_frame.columnconfigure(0, weight=1)
        
        self.dist_rel_mesh_rbtn = Radiobutton(self.mesh_rbtn_frame, text='Relative Mesh', value=1, variable=self.mesh_output_type)
        self.dist_rel_mesh_rbtn.grid(row=0, column=0, sticky='W', padx=5)        
        self.dist_diff_mesh_rbtn = Radiobutton(self.mesh_rbtn_frame, text='Absolute Mesh', value=2, variable=self.mesh_output_type)
        self.dist_diff_mesh_rbtn.grid(row=1, column=0, sticky='W', padx=5)                 
        
        self.save_mesh_btn = Button(self.show_mesh_frame, text='Save Mesh', command=self.save_mesh)
        self.save_mesh_btn.pack(side='right', padx=2, pady=5)
        
        self.show_mesh_btn = Button(self.show_mesh_frame, text='Show Mesh', command=partial(self.show_dist_mesh, mesh_output_type=self.mesh_output_type))
        self.show_mesh_btn.pack(side='right', padx=2, pady=5)

        self.dist_analyze_btn = Button(self.show_mesh_frame, text='Evaluate', command=self.dist_evaluate)
        self.dist_analyze_btn.pack(side='right', padx=2, pady=5)
        
        self.dist_analysis_btn_list = [self.dist_rel_mesh_rbtn, self.dist_diff_mesh_rbtn, self.save_mesh_btn, self.show_mesh_btn, self.dist_analyze_btn]
        self.buttons.append(self.dist_analysis_btn_list)
        
        # self.reset()

        # Widget Initialization
        self.controller = Controller(self.msg_box, self.preset_file_load, self.img_file_load, self.output_path, self.preview_canvas)

        linked_tabs = {'grid_extract_paras':self.grid_extract_settings, 'grid_sort_paras':self.grid_sort_settings}

        self.preset_file_load.init_linked_tabs(linked_tabs)
        self.preset_file_load.preset_path.set(PRESET_PATH)
        self.preset_file_load.load_preset()
        self.preset_file_load.set_controller(self.controller)
    
    def extract_grid(self):
        
        self.dist_eval.raw_im = self.img_file_load.image
        
        grid_extract_paras = self.grid_extract_settings.output_parsed_vals()                
        # output_msg = self.dist_eval.std_grid_gen(*grid_extract_paras[0:3])
        # self.controller.msg_box.console(output_msg)
        # output_msg = self.dist_eval.img_grid_extract(*grid_extract_paras[3:])
        output_msg = self.dist_eval.img_grid_extract(*grid_extract_paras[0:3])
        self.dist_eval.grid_dim = grid_extract_paras[3]
        self.dist_eval.std_grid_pts_count = self.dist_eval.grid_dim[0] * self.dist_eval.grid_dim[1]
        self.controller.msg_box.console(output_msg)
        
        if self.dist_eval.extracted_pts_count == self.dist_eval.std_grid_pts_count:
            output_msg = f'Standard Grid Points: {self.dist_eval.std_grid_pts_count}\n'
            output_msg += f'Extracted Points: {self.dist_eval.extracted_pts_count}\n'
            self.controller.msg_box.console(output_msg)
            self.enable_btn_group(self.grid_sort_btn_list)
        else:
            output_msg = f'Standard Grid Points: {self.dist_eval.std_grid_pts_count}\n'
            output_msg += f'Extracted Points: {self.dist_eval.extracted_pts_count}\n'
            output_msg += f'Incorrect extracted point count!'
            self.controller.msg_box.console(output_msg)
        
        
        return
    
    def sort_grid(self):
        grid_sort_paras = self.grid_sort_settings.output_parsed_vals()
        self.dist_eval.sort_dist_grid(*grid_sort_paras[0:2])
        self.dist_eval.draw_coords_index(0.8)
        self.controller.msg_box.console('Extracted Grid Sorted')
        # self.dist_analyze_btn.config(state='enable')
        x_min_pitch, y_min_pitch = self.dist_eval.get_center_pitch()
        x_center, y_center = self.dist_eval.get_center_pt()
        self.mark_center()
        self.controller.msg_box.console(f'Grid center location: {x_center}, {y_center}')
        self.controller.msg_box.console(f'Grid pitch at center: {x_min_pitch}, {y_min_pitch}')
        return

    def get_std_grid(self):
        grid_sort_paras = self.grid_sort_settings.output_parsed_vals()
        msg_output = self.dist_eval.std_grid_gen(*grid_sort_paras[2::])        
        self.controller.msg_box.console(msg_output)
        self.preview_canvas.update_image(Image.fromarray((self.dist_eval.labeled_im).astype(np.uint8)))
        return
    
    def export_grid(self):
        output_path = self.output_path.get_path()
        if len(output_path) == 0:
            self.controller.msg_box.console('No file output, output path not specified')
            return
        timestr = time.strftime("%Y%m%d-%H-%M-%S")        
        np.save(f'{output_path}Standard Grid Coordinate_{timestr}.npy', self.dist_eval.std_grid.coords)
        output_msg = f'Standard grid file Standard Grid Coordinate_{timestr}.npy saved'
        self.controller.msg_box.console(output_msg)
        np.save(f'{output_path}Distorted Grid Coordinate_{timestr}.npy', self.dist_eval.dist_grid.coords)
        output_msg = f'Distorted grid file Distorted Grid Coordinate_{timestr}.npy saved'
        self.controller.msg_box.console(output_msg)
        return

    def preview_grid_on(self):
        if self.dist_eval.labeled_im is None:
            return
        self.preview_canvas.update_image(Image.fromarray((self.dist_eval.labeled_im).astype(np.uint8)))
        return

    def preview_grid_off(self):
        if self.dist_eval.labeled_im is None:
            return
        self.preview_canvas.update_image(Image.fromarray((self.dist_eval.raw_im).astype(np.uint8)))
        return
    
    def preview_sort_on(self):
        if self.dist_eval.indexed_im is None:
            return
        self.preview_canvas.update_image(Image.fromarray((self.dist_eval.indexed_im).astype(np.uint8)))
        return

    def preview_sort_off(self):
        if self.dist_eval.indexed_im is None:
            return
        self.preview_canvas.update_image(Image.fromarray((self.dist_eval.indexed_im).astype(np.uint8)))
        return

    def mark_center(self):
        if self.dist_eval.dist_grid.sorted:
            draw = ImageDraw.Draw(self.preview_canvas.image)            
            for p in self.dist_eval.get_center_pts():
                x, y = p[:]
                draw.line([x - 5, y, x + 5, y], fill=128)
                draw.line([x, y - 5, x, y + 5], fill=128)            
            self.preview_canvas.update_image(self.preview_canvas.image)
        return


    def preview_center_on(self):
        if self.dist_eval.dist_grid.sorted:
            x, y = self.dist_eval.get_center_pt()            
            self.tmp_canvas_img = self.preview_canvas.image.copy()
            draw = ImageDraw.Draw(self.preview_canvas.image)            
            draw.line([x - 10, y, x + 10, y], fill=128)
            draw.line([x, y - 10, x, y + 10], fill=128)
            self.preview_canvas.update_image(self.preview_canvas.image)

        return
    
    def preview_center_off(self):
        if self.tmp_canvas_img:
            self.preview_canvas.update_image(self.tmp_canvas_img)

        return


    def dist_evaluate(self):
        output_msg = self.dist_eval.dist_eval()
        self.enable_btn_group(self.dist_analysis_btn_list)
        # print(output_msg)
        self.controller.msg_box.console(output_msg)
        return
    
    def show_dist_mesh(self, mesh_output_type):
        dist_rel = self.dist_eval.dist_rel
        dist_eval = self.dist_eval.dist_diff                
        # top_dist_rel_ind = np.argsort(-1 * abs(dist_rel))[0:10]
        # top_dist_diff_ind = np.argsort(-1 * abs(dist_eval))[0:10]
        # grid_extract_paras = self.grid_extract_settings.output_parsed_vals()
        grid_dim = self.dist_eval.grid_dim
        # chart_res = grid_extract_paras[0]
        if mesh_output_type.get() == 1:
            title = 'Relative Distortion %'
            fig, _ = self.plot_coords_mesh(title, (dist_rel) * 100, grid_dim, 5, -5, 'coolwarm')
            
        elif mesh_output_type.get() == 2:
            title = 'Absolute Distortion %'
            fig, _ = self.plot_coords_mesh(title, (dist_eval), grid_dim, 5, -5, 'coolwarm')
        # fig.savefig(output_path + 'distorted_dist_rel.png', dpi=600)
        fig.show()
        return

    def plot_coords_mesh(self, title, coords_val, grid_dim, vmax, vmin, cmap='viridis'):        
        fig, ax = plt.subplots()            
        ax.set_title(title)
        x = np.linspace(0, grid_dim[0], grid_dim[0])
        y = np.linspace(0, grid_dim[1], grid_dim[1])
        xx, yy = np.meshgrid(x, y)
        coords_val_mesh = coords_val.reshape((grid_dim[1], grid_dim[0]))    
        # c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin)        
        c = ax.imshow(coords_val_mesh)
        fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
        return fig, ax

    def save_mesh(self):
        if self.dist_eval.dist_rel is None or self.dist_eval.dist_diff is None:
            output_msg = f'Merit mesh not available!'
            self.controller.msg_box.console(output_msg)
            return
        output_path = self.output_path.get_path()
        if len(output_path) == 0:
            self.controller.msg_box.console('No file output, output path not specified')
            return
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        rel_filename = f'Relative Distortion Mesh_{timestr}'
        np.save(f'{output_path}\\{rel_filename}', self.dist_eval.dist_rel)
        output_msg = f'Mesh file {rel_filename} saved'
        self.controller.msg_box.console(output_msg)

        diff_filename = f'Absolute Distortion Mesh_{timestr}'
        np.save(f'{output_path}\\{diff_filename}', self.dist_eval.dist_diff)
        output_msg = f'Mesh file {diff_filename} saved'
        self.controller.msg_box.console(output_msg)
        
        return

class Controller():
    def __init__(self, msg_box, preset_file_load, img_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path
        self.img_file_load = img_file_load
        self.preview_canvas = preview_canvas