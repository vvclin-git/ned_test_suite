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
# from NED_Chart import *


OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\dist_default.json'

class Distortion(NetsFrame):
    def __init__(self, window):
        super().__init__(window)
        f = open(PRESET_PATH, 'r')
        self.presets = json.load(f)
        f.close()
        self.dist_eval = Distortion_Eval()
        self.dist_grid_paras = self.presets['dist_grid_paras']        
        self.grid_extract_paras = self.presets['grid_extract_paras']
        self.grid_sort_paras = self.presets['grid_sort_paras']
        
        self.output_path = tk.StringVar()
        self.output_path.set(OUTPUT_PATH)
        self.preset_path = tk.StringVar()
        self.preset_path.set(PRESET_PATH)
        self.img_path = tk.StringVar()
        self.raw_img = None

        # analysis preset 
        self.analysis_preset_frame = LabelFrame(self.settings, text='Analysis Parameter Preset', padding=(5, 5, 5, 5))
        self.analysis_preset_frame.pack(expand=True, fill='x', pady=5, side='top')
        self.analysis_preset_frame.columnconfigure(0, weight=5, uniform=1)
        self.analysis_preset_frame.columnconfigure(1, weight=2, uniform=1)
        self.analysis_preset_frame.columnconfigure(2, weight=2, uniform=1)

        self.output_path_input = Entry(self.analysis_preset_frame, textvariable=self.preset_path)
        self.output_path_input.grid(row=0, column=0, columnspan=3, sticky='EW', ipady=5)
        
        output_browse_btn = Button(self.analysis_preset_frame, text='Browse...', style='Buttons.TButton', command=self.preset_browse)
        output_browse_btn.grid(row=1, column=0, sticky='E', padx=0, pady=5)
        output_load_btn = Button(self.analysis_preset_frame, text='Load...', style='Buttons.TButton', command=self.preset_load)
        output_load_btn.grid(row=1, column=1, sticky='E', padx=0, pady=5)
        output_save_btn = Button(self.analysis_preset_frame, text='Save As...', style='Buttons.TButton', command=self.preset_save)        
        output_save_btn.grid(row=1, column=2, sticky='E', padx=0, pady=5)

        # Image Loading 
        self.img_load_frame = LabelFrame(self.settings, text='Image Loading', padding=(5, 5, 5, 5))
        self.img_load_frame.pack(expand=True, fill='x', pady=5, side='top')
        self.img_load_frame.columnconfigure(0, weight=6, uniform=1)
        self.img_load_frame.columnconfigure(1, weight=2, uniform=1)
        self.img_load_frame.columnconfigure(2, weight=2, uniform=1)
        
        self.img_path_input = Entry(self.img_load_frame, textvariable=self.img_path)
        self.img_path_input.grid(row=0, column=0, sticky='EW', ipady=5)
        # self.img_path_input.pack(side='left', expand=True, fill='x')

        img_browse_btn = Button(self.img_load_frame, text='Browse...', style='Buttons.TButton', command=self.img_browse)
        img_browse_btn.grid(row=0, column=1, sticky='E', padx=0, pady=5)
        img_browse_btn = Button(self.img_load_frame, text='Load', style='Buttons.TButton', command=self.img_load)
        img_browse_btn.grid(row=0, column=2, sticky='E', padx=0, pady=5)
        
        
        # img_browse_btn.pack(side='left', expand=True, fill='x')

        # Distortion Grid Settings
        self.dist_grid_frame = LabelFrame(self.settings, text='Distortion Grid Settings', padding=(5, 5, 5, 5))
        self.dist_grid_frame.pack(expand=True, fill='x', pady=5, side='top')
        self.dist_grid_settings = ParameterTab(self.dist_grid_frame, self.dist_grid_paras)
        self.dist_grid_settings.tree.configure(height=3)
        self.dist_grid_settings.pack(expand=True, fill='x', pady=5, side='top')

        # Grid Extraction Settings
        self.grid_extract_frame = LabelFrame(self.settings, text='Grid Extraction Settings', padding=(5, 5, 5, 5))
        self.grid_extract_frame.pack(expand=True, fill='x', pady=5, side='top')
        self.grid_extract_settings = ParameterTab(self.grid_extract_frame, self.grid_extract_paras)
        self.grid_extract_settings.tree.configure(height=3)
        self.grid_extract_settings.pack(expand=True, fill='x', pady=5, side='top')
        self.grid_extract_btn = Button(self.grid_extract_frame, text='Extract Grid', style='Buttons.TButton', command=None)
        self.grid_extract_btn.pack(side='top')
        
        # Grid Sorting Settings
        self.grid_sort_frame = LabelFrame(self.settings, text='Grid Sorting Settings', padding=(5, 5, 5, 5))
        self.grid_sort_frame.pack(expand=True, fill='x', pady=5, side='top')
        self.grid_sort_settings = ParameterTab(self.grid_sort_frame, self.grid_sort_paras)
        self.grid_sort_settings.tree.configure(height=3)
        self.grid_sort_settings.pack(expand=True, fill='x', pady=5, side='top')
        self.grid_sort_btn = Button(self.grid_sort_frame, text='Sort Grid', style='Buttons.TButton', command=None)
        self.grid_sort_btn.pack(side='top')
    
    def path_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askdirectory(parent=self, initialdir=cur_path, title='Please select a directory')
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        self.output_path.set(temp_path)
        return
    
    def preset_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.preset_path.set(temp_path)
        return
    
    def preset_load(self):
        f = open(self.preset_path.get(), 'r')
        chart_parameters = json.load(f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        return chart_parameters

    def preset_save(self):
        if os.path.isfile(self.preset_path.get()):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(self.preset_path.get(), 'w')
        save_preset = {'chart_types':self.chart_types, 'chart_parameters':self.saved_chart_paras, 'chart_chk_paras':self.chart_chk_paras}
        json.dump(save_preset, f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Saved')
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
            self.raw_img = cv2.imread(img_path)
            self.update_img(Image.fromarray((self.raw_img).astype(np.uint8)))
            self.console(f'Image File: {img_path} Loaded')
        return