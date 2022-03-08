import imp
from Frames.NetsFrame import *
from ParameterTab import *
import os
from tkinter import filedialog
from NED_Analyzer import *
import re
import time
import json
from tkinter.ttk import *
from ToggleBtn import *
import matplotlib
from matplotlib import pyplot as plt
from functools import partial

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\grille_default.json'
MESH_OUTPUT_PATH = f'{os.getcwd()}\\Output'

class Grille(NetsFrame):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        f = open(PRESET_PATH, 'r')
        self.presets = json.load(f)
        f.close()
        self.grille_eval = Grille_Eval()

        self.grille_grid_paras = self.presets['grille_grid_paras']

        self.output_path = tk.StringVar()        
        self.output_path.set(OUTPUT_PATH)        
        self.preset_path.set(PRESET_PATH)
        self.mesh_output_path = tk.StringVar()
        self.mesh_output_path.set(MESH_OUTPUT_PATH)
        self.img_path = tk.StringVar()
        # self.mesh_output_type = tk.IntVar()
        # self.mesh_output_type.set(1)        
        self.raw_img = None
        
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

        # Grille Analysis Settings
        self.grille_grid_frame = LabelFrame(self.settings, text='Grille Merit Grid Settings', padding=(5, 5, 5, 5))
        self.grille_grid_frame.pack(expand=True, fill='x', pady=10, side='top')
        
        self.grille_grid_settings = ParameterTab(self.grille_grid_frame, self.grille_grid_paras)
        self.grille_grid_settings.tree.configure(height=3)
        self.grille_grid_settings.pack(expand=True, fill='x', pady=5, side='top')

        self.grille_grid_btn_frame = Frame(self.grille_grid_frame)
        self.grille_grid_btn_frame.pack(side='top', expand=True, fill='both')
        # self.extract_preview_btn = Button(self.grille_grid_btn_frame, text='Preview', style='Buttons.TButton', command=None)
        # self.extract_preview_btn.pack(side='right', padx=2, pady=5)
        self.grille_grid_preview_btn = ToggleBtn(self.grille_grid_btn_frame, 'Preview On', 'Preview Off', self.preview_grid_on, self.preview_grid_off)
        self.grille_grid_preview_btn.pack(side='right', padx=2, pady=5)
        
        self.grille_grid_btn = Button(self.grille_grid_btn_frame, text='Generate Grid', style='Buttons.TButton', command=self.gen_mc_grid)
        self.grille_grid_btn.pack(side='right', padx=2, pady=5)

        # Grille Contrast Analysis
        self.grille_analysis_frame = LabelFrame(self.settings, text='Grille Contrast Analysis', padding=(5, 5, 5, 5))
        self.grille_analysis_frame.pack(side='top', expand=True, fill='x', pady=10)

        self.mesh_output_frame = Frame(self.grille_analysis_frame)
        self.mesh_output_frame.pack(side='top', expand=True, fill='both')
        
        self.mesh_output_label = Label(self.mesh_output_frame, text='Output Path')
        self.mesh_output_label.pack(side='left', padx=5, pady=5)
        
        self.mesh_output_input = Entry(self.mesh_output_frame, textvariable=self.mesh_output_path)
        self.mesh_output_input.pack(side='left', expand=True, fill='x', pady=5)
        
        self.mesh_output_btn = Button(self.mesh_output_frame, text='Browse...', style='Buttons.TButton', command=partial(self.path_browse, path_var=self.mesh_output_path))
        self.mesh_output_btn.pack(side='left', padx=2, pady=5)
        
        self.show_mesh_frame = Frame(self.grille_analysis_frame)
        self.show_mesh_frame.pack(side='top', expand=True, fill='x')        
              
        self.save_mesh_btn = Button(self.show_mesh_frame, text='Save Mesh', command=self.save_mesh)
        self.save_mesh_btn.pack(side='right', padx=2, pady=5)
        
        self.grille_mesh_btn = Button(self.show_mesh_frame, text='Show Mesh', command=self.show_grille_mesh)
        self.grille_mesh_btn.pack(side='right', padx=2, pady=5)

        self.grille_analyze_btn = Button(self.show_mesh_frame, text='Evaluate', command=self.grille_evaluate)
        self.grille_analyze_btn.pack(side='right', padx=2, pady=5)
    


    def load_preset(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        self.grille_grid_paras = self.presets['grille_grid_paras']        
        self.grille_grid_settings.parameter_chg(self.grille_grid_paras)
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        return 

    def save_preset(self):
        if os.path.isfile(self.preset_path.get()):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(self.preset_path.get(), 'w')
        for p in self.grille_grid_settings.output_values():
            self.grille_grid_paras[p[0]]['value'] = p[1]
        
        
        save_preset = {'grille_grid_paras':self.grille_grid_paras}
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
            self.grille_eval.raw_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            self.grille_eval.labeled_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
            self.update_img(Image.fromarray((self.grille_eval.raw_img).astype(np.uint8)))
            self.console(f'Image File: {img_path} Loaded')
        return

    def preview_grid_on(self):
        if self.grille_eval.labeled_img is None:
            self.console('Preview image not available!')
            return
        self.update_img(Image.fromarray((self.grille_eval.labeled_img).astype(np.uint8)))
        return

    def preview_grid_off(self):
        if self.grille_eval.labeled_img is None:
            self.console('Preview image not available!')
            return
        self.update_img(Image.fromarray((self.grille_eval.raw_img).astype(np.uint8)))
        return

    def gen_mc_grid(self):
        grille_grid_paras = self.grille_grid_settings.output_parsed_vals()
        output_msg = self.grille_eval.gen_mc_grid(*grille_grid_paras)
        self.console(output_msg)
        return
    
    def grille_evaluate(self):
        output_msg = self.grille_eval.grille_eval()
        self.console(output_msg)
        return

    def show_grille_mesh(self):
        grille_mc_mesh = self.grille_eval.grille_mc
        grille_grid_paras = self.grille_grid_settings.output_parsed_vals()
        grid_dim = grille_grid_paras[2]
        chart_res = grille_grid_paras[1]
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
        c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin)        
        fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
        return fig, ax
    
    def save_mesh(self):
        if self.grille_eval.grille_mc is None:
            output_msg = f'Merit mesh not available!'
            self.console(output_msg)
            return
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        filename = f'Grille Contrast Mesh_{timestr}'
        np.save(self.output_path + filename, self.grille_eval.grille_mc)
        output_msg = f'Mesh file {filename} saved'
        self.console(output_msg)
        return