import imp

from numpy import pad
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
# from NED_Chart import *

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\Presets\\dist_default.json'
MESH_OUTPUT_PATH = f'{os.getcwd()}\\Output'

class Distortion(NetsFrame):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        f = open(PRESET_PATH, 'r')
        self.presets = json.load(f)
        f.close()
        self.dist_eval = Distortion_Eval()
        # self.dist_grid_paras = self.presets['dist_grid_paras']        
        self.grid_extract_paras = self.presets['grid_extract_paras']
        self.grid_sort_paras = self.presets['grid_sort_paras']
        
        self.output_path = tk.StringVar()        
        self.output_path.set(OUTPUT_PATH)        
        self.preset_path.set(PRESET_PATH)
        self.mesh_output_path = tk.StringVar()
        self.mesh_output_path.set(MESH_OUTPUT_PATH)
        self.img_path = tk.StringVar()
        self.mesh_output_type = tk.IntVar()
        self.mesh_output_type.set(1)        
        self.raw_img = None
        self.buttons = []
        
        # preset button event handler config
        self.preset_save_btn.configure(command=self.save_preset)
        self.preset_load_btn.configure(command=self.load_preset)

        # Image Loading 
        self.img_load_frame = LabelFrame(self.settings, text='Image Loading', padding=(5, 5, 5, 5))
        self.img_load_frame.pack(expand=True, fill='x', pady=10, side='top')
        
        self.img_load_input_frame = Frame(self.img_load_frame)
        self.img_load_input_frame.pack(side='top', expand=True, fill='both')
        self.img_load_btn_frame = Frame(self.img_load_frame)
        self.img_load_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.img_path_label = Label(self.img_load_input_frame, text='Image Path')
        self.img_path_label.pack(side='left', padx=5, pady=5)
        self.img_path_input = Entry(self.img_load_input_frame, textvariable=self.img_path)        
        self.img_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        img_load_btn = Button(self.img_load_btn_frame, text='Load', style='Buttons.TButton', command=self.img_load)
        img_load_btn.pack(side='right', padx=2, pady=5)
        img_browse_btn = Button(self.img_load_btn_frame, text='Browse...', style='Buttons.TButton', command=self.img_browse)        
        img_browse_btn.pack(side='right', padx=2, pady=5)
        
        # Grid Extraction Settings
        self.grid_extract_frame = LabelFrame(self.settings, text='Grid Extraction Settings', padding=(5, 5, 5, 5))
        self.grid_extract_frame.pack(expand=True, fill='x', pady=10, side='top')
        
        self.grid_extract_settings = ParameterTab(self.grid_extract_frame, self.grid_extract_paras)
        self.grid_extract_settings.tree.configure(height=6)
        self.grid_extract_settings.pack(expand=True, fill='x', pady=5, side='top')

        self.grid_extract_btn_frame = Frame(self.grid_extract_frame)
        self.grid_extract_btn_frame.pack(side='top', expand=True, fill='both')
        # self.extract_preview_btn = Button(self.grid_extract_btn_frame, text='Preview', style='Buttons.TButton', command=None)
        # self.extract_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.extract_preview_btn = ToggleBtn(self.grid_extract_btn_frame, 'Preview On', 'Preview Off', self.preview_grid_on, self.preview_grid_off)
        self.extract_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_extract_btn = Button(self.grid_extract_btn_frame, text='Extract Grid', style='Buttons.TButton', command=self.extract_grid)
        self.grid_extract_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_extract_btn_list = [self.extract_preview_btn, self.grid_extract_btn]
        self.buttons.append(self.grid_extract_btn_list)

        # Grid Sorting Settings
        self.grid_sort_frame = LabelFrame(self.settings, text='Grid Sorting Settings', padding=(5, 5, 5, 5))
        self.grid_sort_frame.pack(expand=True, fill='x', pady=10, side='top')
        self.grid_sort_settings = ParameterTab(self.grid_sort_frame, self.grid_sort_paras)
        self.grid_sort_settings.tree.configure(height=3)
        self.grid_sort_settings.pack(expand=True, fill='x', pady=5, side='top')
        
        self.grid_sort_btn_frame = Frame(self.grid_sort_frame)
        self.grid_sort_btn_frame.pack(side='top', expand=True, fill='both')
        # self.sort_preview_btn = Button(self.grid_sort_btn_frame, text='Preview', style='Buttons.TButton', command=None)
        # self.sort_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.export_grids_btn = Button(self.grid_sort_btn_frame, text='Export Grids', command=self.export_grids)
        self.export_grids_btn.pack(side='right', padx=2, pady=5)
        
        self.sort_preview_btn = ToggleBtn(self.grid_sort_btn_frame, 'Show Index On', 'Show Index Off', self.preview_sort_on, self.preview_sort_off)
        self.sort_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_sort_btn = Button(self.grid_sort_btn_frame, text='Sort Grid', style='Buttons.TButton', command=self.sort_grid)
        self.grid_sort_btn.pack(side='right', padx=2, pady=5)
        
        self.grid_sort_btn_list = [self.sort_preview_btn, self.grid_sort_btn, self.export_grids_btn]
        self.buttons.append(self.grid_sort_btn_list)
        
        # Distortion Analysis
        self.dist_analysis_frame = LabelFrame(self.settings, text='Distortion Analysis', padding=(5, 5, 5, 5))
        self.dist_analysis_frame.pack(side='top', expand=True, fill='x', pady=10)

        self.mesh_output_frame = Frame(self.dist_analysis_frame)
        self.mesh_output_frame.pack(side='top', expand=True, fill='both')
        
        self.mesh_output_label = Label(self.mesh_output_frame, text='Output Path')
        self.mesh_output_label.pack(side='left', padx=5, pady=5)
        
        self.mesh_output_path_input = Entry(self.mesh_output_frame, textvariable=self.mesh_output_path)
        self.mesh_output_path_input.pack(side='left', expand=True, fill='x', pady=5)
        
        self.mesh_output_path_btn = Button(self.mesh_output_frame, text='Browse...', style='Buttons.TButton', command=partial(self.path_browse, path_var=self.mesh_output_path))
        self.mesh_output_path_btn.pack(side='left', padx=2, pady=5)
        
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
        
        self.reset()

        
    def load_preset(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        self.grid_extract_paras = self.presets['grid_extract_paras']
        self.grid_sort_paras = self.presets['grid_sort_paras']
        self.grid_extract_settings.parameter_chg(self.grid_extract_paras)
        self.grid_sort_settings.parameter_chg(self.grid_sort_paras)
        
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        return 

    def save_preset(self):
        if os.path.isfile(self.preset_path.get()):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(self.preset_path.get(), 'w')
        for p in self.grid_extract_settings.output_values():
            self.grid_extract_paras[p[0]]['value'] = p[1]
        for p in self.grid_sort_settings.output_values():
            self.grid_sort_paras[p[0]]['value'] = p[1]
        
        save_preset = {'grid_extract_paras':self.grid_extract_paras, 'grid_sort_paras':self.grid_sort_paras}
        json.dump(save_preset, f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Saved')
        return

    def path_browse(self, path_var):
        cur_path = os.getcwd()
        temp_path = filedialog.askdirectory(parent=self, initialdir=cur_path, title='Please select a directory')
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        path_var.set(temp_path)
        return

    def img_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a image file', filetypes=[("PNG","*.png"), ("bmp","*.bmp"), ("JPG","*.jpg")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.img_path.set(temp_path)
        return

    def img_load(self):        
        img_path = self.img_path.get()
        if len(img_path) > 0:
            self.dist_eval.raw_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            self.update_img(Image.fromarray((self.dist_eval.raw_img).astype(np.uint8)))
            self.console(f'Image File: {img_path} Loaded')
            self.reset()
            self.enable_btn_group(self.grid_extract_btn_list)
        return
    
    def extract_grid(self):
        grid_extract_paras = self.grid_extract_settings.output_parsed_vals()                
        
        output_msg = self.dist_eval.img_grid_extract(*grid_extract_paras[3:])
        self.console(output_msg)
        self.dist_eval.chart_res = np.array(grid_extract_paras[0])
        self.dist_eval.grid_dim = np.array(grid_extract_paras[1])
        # output_msg = self.dist_eval.std_grid_gen(*grid_extract_paras[0:3])
        # self.console(output_msg)
        std_grid_pts_count = self.dist_eval.grid_dim[0] * self.dist_eval.grid_dim[1]
        if self.dist_eval.extracted_pts_count == std_grid_pts_count:
            output_msg = f'Standard Grid Points: {std_grid_pts_count}\n'
            output_msg += f'Extracted Points: {self.dist_eval.extracted_pts_count}\n'
            self.console(output_msg)
            self.enable_btn_group(self.grid_sort_btn_list)
        else:
            output_msg = f'Standard Grid Points: {std_grid_pts_count}\n'
            output_msg += f'Extracted Points: {self.dist_eval.extracted_pts_count}\n'
            output_msg += f'Incorrect extracted point count!'
            self.console(output_msg)
        
        
        return
    
    def sort_grid(self):
        grid_sort_paras = self.grid_sort_settings.output_parsed_vals()
        self.dist_eval.sort_dist_grid(*grid_sort_paras)
        self.dist_eval.draw_coords_index(0.8)
        self.console('Extracted Grid Sorted')
        self.dist_analyze_btn.config(state='enable')
        # if self.dist_eval.extracted_pts_count == self.dist_eval.std_grid_pts_count:
        #     grid_sort_paras = self.grid_sort_settings.output_parsed_vals()
        #     self.dist_eval.sort_dist_grid(*grid_sort_paras)
        #     self.dist_eval.draw_coords_index(0.8)
        #     self.console('Extracted Grid Sorted')
        #     self.dist_analyze_btn.config(state='enable')
        # else:
        #     self.console(f'Incorrect extracted point count (std_grid: {self.dist_eval.std_grid_pts_count}, extracted: {self.dist_eval.extracted_pts_count})')
        return

    def preview_grid_on(self):
        if self.dist_eval.labeled_img is None:
            return
        self.update_img(Image.fromarray((self.dist_eval.labeled_img).astype(np.uint8)))
        return

    def preview_grid_off(self):
        if self.dist_eval.labeled_img is None:
            return
        self.update_img(Image.fromarray((self.dist_eval.raw_img).astype(np.uint8)))
        return
    
    def preview_sort_on(self):
        if self.dist_eval.indexed_img is None:
            return
        self.update_img(Image.fromarray((self.dist_eval.indexed_img).astype(np.uint8)))
        return

    def preview_sort_off(self):
        if self.dist_eval.indexed_img is None:
            return
        self.update_img(Image.fromarray((self.dist_eval.indexed_img).astype(np.uint8)))
        return

    def dist_evaluate(self):
        output_msg = self.dist_eval.dist_eval()
        self.enable_btn_group(self.dist_analysis_btn_list)
        # print(output_msg)
        self.console(output_msg)
        return
    
    def show_dist_mesh(self, mesh_output_type):
        dist_rel = self.dist_eval.dist_rel
        dist_eval = self.dist_eval.dist_diff                
        # top_dist_rel_ind = np.argsort(-1 * abs(dist_rel))[0:10]
        # top_dist_diff_ind = np.argsort(-1 * abs(dist_eval))[0:10]
        grid_extract_paras = self.grid_extract_settings.output_parsed_vals()
        grid_dim = grid_extract_paras[1]
        chart_res = grid_extract_paras[0]
        if mesh_output_type.get() == 1:
            title = 'Relative Distortion %'
            fig, _ = self.plot_coords_mesh(title, (dist_rel) * 100, grid_dim, chart_res, 5, -5, 'coolwarm')
            
        elif mesh_output_type.get() == 2:
            title = 'Absolute Distortion %'
            fig, _ = self.plot_coords_mesh(title, (dist_eval) * 100, grid_dim, chart_res, 5, -5, 'coolwarm')
        # fig.savefig(output_path + 'distorted_dist_rel.png', dpi=600)
        fig.show()
        return

    def plot_coords_mesh(self, title, coords_val, grid_dim, chart_res, vmax, vmin, cmap='viridis'):        
        fig, ax = plt.subplots()            
        ax.set_title(title)
        # x = np.linspace(0, chart_res[0], grid_dim[0])
        # y = np.linspace(0, chart_res[1], grid_dim[1])
        x = np.linspace(1, grid_dim[0], grid_dim[0])
        y = np.linspace(1, grid_dim[1], grid_dim[1])
        xx, yy = np.meshgrid(x, y)
        coords_val_mesh = coords_val.reshape((grid_dim[1], grid_dim[0]))    
        # c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin, shading='auto')
        c = ax.imshow(coords_val_mesh)        
        fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
        return fig, ax

    def save_mesh(self):
        if (self.dist_eval.dist_rel is None) or (self.dist_eval.dist_diff is None):
            output_msg = f'Merit mesh not available!'
            self.console(output_msg)
            return
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        output_path = self.output_path.get() + '\\'
        rel_filename = f'Relative Distortion Mesh_{timestr}.npy'
        np.save(output_path + rel_filename, self.dist_eval.dist_rel)
        output_msg = f'Mesh file {rel_filename} saved'
        self.console(output_msg)

        diff_filename = f'Absolute Distortion Mesh_{timestr}.npy'
        np.save(output_path + diff_filename, self.dist_eval.dist_diff)
        output_msg = f'Mesh file {diff_filename} saved'
        self.console(output_msg)
        
        return

    def export_grids(self):
        # if (self.dist_eval.std_grid is None) or (self.dist_eval.dist_grid is None):
        #     output_msg = f'Grids not available!'
        #     self.console(output_msg)
        #     return
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        output_path = self.output_path.get() + '\\'
        dist_grid_filename = f'Distorted_Grid_{timestr}.npy'
        np.save(output_path + dist_grid_filename, self.dist_eval.dist_grid.coords)
        output_msg = f'Grid file {dist_grid_filename} saved'
        self.console(output_msg)
        std_grid_filename = f'Standard_Grid_{timestr}.npy'
        np.save(output_path + std_grid_filename, self.dist_eval.std_grid.coords)
        output_msg = f'Grid file {std_grid_filename} saved'
        self.console(output_msg)