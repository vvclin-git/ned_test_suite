import imp
import os
from tkinter import filedialog
from NED_Chart import *
import re
import time
import json
from tkinter.ttk import *
from Widgets.ImgFileLoad import ImgFileLoad
from Widgets.MsgBox import MsgBox
from Widgets.PresetFileLoad import PresetFileLoad
from Widgets.PathBrowse import PathBrowse
from Widgets.ChartParaTree import ChartParaTree
from Widgets.ToggleBtn import ToggleBtn
from PIL import Image, ImageTk
from Widgets.ZoomCanvas import *

CHART_FN_DICT = {'Reticle': gen_reticle, 
                    'Circle Grid': gen_circle_grid, 
                    'Checkerboard': gen_checkerboard, 
                    'Grille': gen_grille, 
                    'Slanted Edge MTF': gen_se_MTF}

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\Presets\\chart_default.json'

regex_coord = re.compile(r'\d+x\d+')
regex_color = re.compile(r'\d+,\d+,\d+')

class TestCharts(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)
        
        chart_json = open(PRESET_PATH, 'r')
        tree_paras = json.load(chart_json)
        chart_json.close()
        
        self.preset_path = tk.StringVar()                
        self.presets = None
        self.preview_img_size = preview_img_size
        self.columnconfigure(0, weight=2, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)
        self.rowconfigure(0, weight=1, uniform=1)
        
        # Output container settings
        output = Frame(self, style='Output.TFrame', padding=(10, 10))   
        output.grid(row=0, column=0, sticky="NEWS")
        output.rowconfigure(0, weight=5, uniform=1)
        output.rowconfigure(1, weight=1, uniform=1)
        output.columnconfigure(0, weight=1)
        
        # Preview Image Widget
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]                     
        preview_frame = LabelFrame(output, text='Preview Image', style='Test.TLabelframe')           
        preview_frame.grid(row=0, column=0, sticky='NEWS', pady=(0, 10))           
        
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.preview_canvas = Zoom_Advanced(preview_frame, self.preview_img)             

        # Message Output     
        msg_frame = LabelFrame(output, text='Output Message', style='TLabelframe')  
        msg_frame.grid(row=1, column=0, sticky='NEWS')
        self.msg_box = MsgBox(msg_frame)        
        self.msg_box.pack(side='top', expand=1, fill='both')        
        
        # Settings Container Settings        
        self.settings = Frame(self, style='Settings.TFrame', padding=(10, 10))        
        self.settings.grid(row=0, column=1, sticky='NEW')
                
        # Preset Save / Load
        self.preset_file_load = PresetFileLoad(self.settings)
        self.preset_file_load.pack(side='top', expand=1, fill='x')
        
        # Output Path
        self.output_path = PathBrowse(self.settings)
        self.output_path.pack(side='top', expand=1, fill='x', pady=5)

        # Chart Parameter Tree
        self.chart_para_frame = LabelFrame(self.settings, text='Test Chart Parameters')
        self.chart_para_frame.pack(side='top', expand=1, fill='x')
        self.chart_para_tree = ChartParaTree(self.chart_para_frame, tree_paras)
        self.chart_para_tree.set_tree_height(20)
        self.chart_para_tree.pack(side='top', expand=1, fill='x', pady=5, padx=2)
                
        self.output_chart_btn = Button(self.chart_para_frame, text='Output Charts', command=self.output_charts)
        self.output_chart_btn.pack(side='right', padx=2, pady=5)        
        
        self.preview_chart_btn = Button(self.chart_para_frame, text='Preview Chart', command=self.preview_chart)
        self.preview_chart_btn.pack(side='right', padx=2, pady=5)

        self.select_all_btn = ToggleBtn(self.chart_para_frame, 'Select All', 'Deselect All', self.chart_para_tree.deselect_all, self.chart_para_tree.select_all)
        self.select_all_btn.pack(side='right', padx=2, pady=5)

        self.fold_tree_btn = ToggleBtn(self.chart_para_frame, 'Fold', 'Unfold', self.chart_para_tree.unfold_tree, self.chart_para_tree.fold_tree)
        self.fold_tree_btn.pack(side='right', padx=2, pady=5)
        
        # Widget Initialization
        self.controller = Controller(self.msg_box, self.preset_file_load, self.output_path, self.preview_canvas)

        linked_tabs = {'chart_parameters':self.chart_para_tree}

        self.preset_file_load.init_linked_tabs(linked_tabs)
        self.preset_file_load.preset_path.set(PRESET_PATH)
        self.preset_file_load.load_preset()
        self.preset_file_load.set_controller(self.controller)   

        # f = open(PRESET_PATH, 'r')
        # self.presets = json.load(f)
        # f.close()
        
        # self.chart_types = self.presets['chart_types']
        # self.saved_chart_paras = self.presets['chart_parameters']
        # self.chart_chk_paras = self.presets['chart_chk_paras']
        
        # # print(self.saved_chart_paras[self.chart_types[0]])

        # self.chart_type = tk.StringVar()
        # self.chart_type.set(self.chart_types[0])
        # self.cur_chart_type = self.chart_type.get()
        # # self.saved_chart_paras = CHART_PARAMETERS        
        # self.output_path = tk.StringVar()
        # self.output_path.set(OUTPUT_PATH)        
        # self.preset_path.set(PRESET_PATH)
        
        # # preset button event handler config
        # self.preset_save_btn.configure(command=self.save_preset)
        # self.preset_load_btn.configure(command=self.load_preset)
        


        # # chart parameter settings
        # self.chart_settings_frame = LabelFrame(self.settings, text='Chart Parameter Settings', padding=(5, 5, 5, 5))
        # self.chart_settings_frame.pack(expand=True, fill='x', pady=10, side='top')
     
        # self.chart_selector_frame = Frame(self.chart_settings_frame)
        # self.chart_selector_frame.pack(side='top', expand=True, fill='both')        
        
        # self.chart_selector_label = Label(self.chart_selector_frame, text='Chart Type')        
        # self.chart_selector_label.pack(side='left', padx=5, pady=5)

        # self.chart_selector = tk.OptionMenu(self.chart_selector_frame, self.chart_type, *self.chart_types, command=self.init_parameters)
        # self.chart_selector.configure(anchor='w', width=30)
        # self.chart_selector.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        # preview_test_btn = Button(self.chart_selector_frame, text='Preview Chart', command=self.preview_chart)        
        # preview_test_btn.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        # self.chart_settings = ParameterTab(self.chart_settings_frame, self.saved_chart_paras[self.chart_types[0]])       
        # self.chart_settings.tree.configure(height=6)        
        # self.chart_settings.pack(side='top', expand=True, fill='x')
        
        # # chart output settings        
        # self.chart_output_frame = LabelFrame(self.settings, text='Chart Output Settings', padding=(5, 5, 5, 5))
        # self.chart_output_frame.pack(expand=True, fill='x', pady=10, side='top')
        
        # self.output_path_frame = Frame(self.chart_output_frame)
        # self.output_path_frame.pack(side='top', expand=True, fill='both')
        
        # self.output_path_label = Label(self.output_path_frame, text='Output Path')
        # self.output_path_label.pack(side='left', padx=5, pady=5)
        
        # self.output_path_input = Entry(self.output_path_frame, textvariable=self.output_path)
        # self.output_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        # self.output_path_btn = Button(self.output_path_frame, text='Browse...', style='Buttons.TButton', command=self.path_browse)
        # self.output_path_btn.pack(side='left', padx=5, pady=5)
        
        # self.chart_output_chk = ParameterTab(self.chart_output_frame, self.chart_chk_paras)
        # self.chart_output_chk.tree.heading("1", text="Chart Type")
        # self.chart_output_chk.tree.heading("2", text="Output")
        # self.chart_output_chk.tree.configure(height=len(self.chart_types))
        # self.chart_output_chk.pack(side='top', expand=True, fill='x')
        
        # self.chart_output_btn_frame = Frame(self.chart_output_frame)
        # self.chart_output_btn_frame.pack(side='top', expand=True, fill='x')

        # output_all_btn = Button(self.chart_output_btn_frame, text='Output Selected Charts', command=self.output_charts)
        # output_all_btn.pack(side='right', pady=5)
        
        
           
    
    # def rotate_imgs(self):
    #     self.update_img(self.img_list[0])
    #     self.img_list.append(self.img_list.pop(0))
    #     return
        
    # def update_msg_test(self):
    #     self.console('Message Text Update Test')
    #     return
        
    # def init_parameters(self, dummy):
    #     # print(self.chart_settings.output_values())
    #     # save current settings before cleaning
    #     for p in self.chart_settings.output_values():
    #         self.saved_chart_paras[self.cur_chart_type][p[0]]['value'] = p[1]
                
    #     self.chart_settings.clear()
    #     self.cur_chart_type = self.chart_type.get()
    #     # print(self.saved_chart_paras[self.cur_chart_type])
    #     self.chart_settings.parameter_chg(self.saved_chart_paras[self.cur_chart_type])
    #     # self.chart_settings.delete(*self.chart_settings.get_children())
    #     # chart_type_selected = self.chart_type.get()
    #     # for p in CHART_PARAMETERS[chart_type_selected]:            
    #     #     id = self.chart_settings.insert('', 'end', values=(p, ''))
            
    #     return

    # def path_browse(self):
    #     cur_path = os.getcwd()
    #     temp_path = filedialog.askdirectory(parent=self, initialdir=cur_path, title='Please select a directory')
    #     # if len(temp_path) > 0:
    #     #     print ("You chose: %s" % tempdir)
    #     self.output_path.set(temp_path)
    #     return
    
    # def file_browse(self):
    #     cur_path = os.getcwd()
    #     temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
    #     # if len(temp_path) > 0:
    #     #     print ("You chose: %s" % tempdir)
    #     if len(temp_path) > 0:            
    #         self.preset_path.set(temp_path)
    #     return

    # def preview_chart(self):        
    #     chart_type = self.chart_type.get()
    #     chart_im, output_msg = self.gen_chart(chart_type, self.chart_settings.output_values())
    #     # np.save('chart_im', chart_im)
    #     # cv2.imwrite('chart_im_cv.png', chart_im)         
    #     if len(chart_im[0][0]) == 3:
    #         chart_im_preview = Image.fromarray((chart_im).astype(np.uint8))
    #     else:
    #         chart_im_preview = Image.fromarray((chart_im[:, :, 0]).astype(np.uint8))
    #     # chart_im_preview.save('chart_im.png')
    #     self.preview_canvas.update_image(chart_im_preview)
    #     self.console(output_msg)
    #     return
    

    def preview_chart(self):        
        chart_type = self.chart_para_tree.selected_chart
        if len(chart_type) > 0:
            chart_paras = self.chart_para_tree.output_parsed_vals()
            chart_im, output_msg = self.gen_chart(chart_type, chart_paras[chart_type])
            # np.save('chart_im', chart_im)
            # cv2.imwrite('chart_im_cv.png', chart_im)         
            if len(chart_im[0][0]) == 3:
                chart_im_preview = Image.fromarray((chart_im).astype(np.uint8))
            else:
                chart_im_preview = Image.fromarray((chart_im[:, :, 0]).astype(np.uint8))
            # chart_im_preview.save('chart_im.png')
            self.preview_canvas.update_image(chart_im_preview)
            self.controller.msg_box.console(output_msg)
        return

    def gen_chart(self, chart_type, para_list):                
        chart_im, output_msg, _ = CHART_FN_DICT[chart_type](*para_list)        
        return chart_im, output_msg

    def output_charts(self):        
        output_path = self.output_path.get_path()
        if len(output_path) == 0:
            self.controller.msg_box.console('No file output, output path not specified')
            return
        output_name = ''
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        
        chart_paras = self.chart_para_tree.output_parsed_vals()
        self.controller.msg_box.console(f'Output Path: {output_path}')
        for t in chart_paras:
            self.controller.msg_box.console(f'Generating {t}...', cr=False)
            chart_im, output_msg = self.gen_chart(t, chart_paras[t])
            output_name = self.gen_output_name(output_msg)
            self.controller.msg_box.console(f'Exporting...', cr=False)
            stat = cv2.imwrite(f'{output_path}\\{output_name}{timestr}.png', chart_im)
            if stat:
                self.controller.msg_box.console(f'Done', cr=True)        
            else:
                self.controller.msg_box.console(f'Failed', cr=True)
        return

    def gen_output_name(self, chart_output_msg):
        out_paras = chart_output_msg.replace('\n', ',').split(',')        
        out_paras_dict = {}
        for i in range(len(out_paras) - 1):
            p = out_paras[i]
            para = p.split(':')
            out_paras_dict[para[0]] = para[1].lstrip()        
        output_name = ''
        for p in out_paras_dict:
            if p in {'Chart Type', 'Resolution', 'Grid Dimension', 'Grille Size', 'Padding'}:
                output_name += f'{out_paras_dict[p]}_'        
        return output_name

        # for c in self.chart_output_chk.output_values():
        #     if c[1] == 'Yes':
        #         output_name = c[0].replace(' ', '_')
        #         # print(c[0], self.saved_chart_paras[c[0]])
        #         for k in self.saved_chart_paras[c[0]].keys():
        #             # print([k, self.saved_chart_paras[c[0]][k]['value']])
        #             value = self.saved_chart_paras[c[0]][k]['value']
        #             if k == 'Resolution' or k == 'Grid Dimension':
        #                 output_name += f'_{value}'
        #             para_list.append([k, value])
        #         # print(para_list)
        #         self.console(f'Generating {c[0]}...', cr=False)
        #         chart_im, output_msg = self.gen_chart(c[0], para_list)
        #         self.console(f'Exporting...', cr=False)
        #         cv2.imwrite(f'{output_path}\\{output_name}_{timestr}.png', chart_im)
        #         self.console(f'Done', cr=True)

        #     para_list = []
        # return

    def load_preset(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()        
        self.chart_types = self.presets['chart_types']
        self.saved_chart_paras = self.presets['chart_parameters']
        self.chart_chk_paras = self.presets['chart_chk_paras']
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        self.chart_settings.parameter_chg(self.saved_chart_paras[self.cur_chart_type])
        self.chart_output_chk.parameter_chg(self.chart_chk_paras)
        return

    def save_preset(self):
        if os.path.isfile(self.preset_path.get()):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')            
            if chk_overwrite == 'no':
                return                
        f = open(self.preset_path.get(), 'w')
        for p in self.chart_settings.output_values():
            self.saved_chart_paras[self.cur_chart_type][p[0]]['value'] = p[1]
        save_preset = {'chart_types':self.chart_types, 'chart_parameters':self.saved_chart_paras, 'chart_chk_paras':self.chart_chk_paras}
        json.dump(save_preset, f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Saved')
        return

class Controller():
    def __init__(self, msg_box, preset_file_load, output_path, preview_canvas):
        self.msg_box = msg_box
        self.msg_box = msg_box
        self.preset_file_load = preset_file_load
        self.output_file_path = output_path
        
        self.preview_canvas = preview_canvas