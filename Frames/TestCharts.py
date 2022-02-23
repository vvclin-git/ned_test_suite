import imp
from Frames.NetsFrame import *
from ParameterTab import *
import os
from tkinter import filedialog
from NED_Chart import *
import re
import time
import json
from tkinter.ttk import *


CHART_FN_DICT = {'Reticle': gen_reticle, 
                    'Circle Grid': gen_circle_grid, 
                    'Checkerboard': gen_checkerboard, 
                    'Grille': gen_grille, 
                    'Slanted Edge MTF': gen_se_MTF}

OUTPUT_PATH = f'{os.getcwd()}\\Output'
PRESET_PATH = f'{os.getcwd()}\\default.json'

regex_coord = re.compile(r'\d+x\d+')
regex_color = re.compile(r'\d+,\d+,\d+')

class TestCharts(NetsFrame):
    def __init__(self, window, preview_img_size):
        super().__init__(window, preview_img_size)
        f = open('default.json', 'r')
        self.presets = json.load(f)
        f.close()
        
        self.chart_types = self.presets['chart_types']
        self.saved_chart_paras = self.presets['chart_parameters']
        self.chart_chk_paras = self.presets['chart_chk_paras']
        
        # print(self.saved_chart_paras[self.chart_types[0]])

        self.chart_type = tk.StringVar()
        self.chart_type.set(self.chart_types[0])
        self.cur_chart_type = self.chart_type.get()
        # self.saved_chart_paras = CHART_PARAMETERS        
        self.output_path = tk.StringVar()
        self.output_path.set(OUTPUT_PATH)        
        self.preset_path.set(PRESET_PATH)
        
        # preset button event handler config
        self.preset_save_btn.configure(command=self.save_preset)
        self.preset_load_btn.configure(command=self.load_preset)
        


        # chart parameter settings
        self.chart_settings_frame = LabelFrame(self.settings, text='Chart Parameter Settings', padding=(5, 5, 5, 5))
        self.chart_settings_frame.pack(expand=True, fill='x', pady=10, side='top')
     
        self.chart_selector_frame = Frame(self.chart_settings_frame)
        self.chart_selector_frame.pack(side='top', expand=True, fill='both')        
        
        self.chart_selector_label = Label(self.chart_selector_frame, text='Chart Type')        
        self.chart_selector_label.pack(side='left', padx=5, pady=5)

        self.chart_selector = tk.OptionMenu(self.chart_selector_frame, self.chart_type, *self.chart_types, command=self.init_parameters)
        self.chart_selector.configure(anchor='w', width=30)
        self.chart_selector.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        preview_test_btn = Button(self.chart_selector_frame, text='Preview Chart', command=self.preview_chart)        
        preview_test_btn.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        self.chart_settings = ParameterTab(self.chart_settings_frame, self.saved_chart_paras[self.chart_types[0]])       
        self.chart_settings.tree.configure(height=6)        
        self.chart_settings.pack(side='top', expand=True, fill='x')
        
        # chart output settings        
        self.chart_output_frame = LabelFrame(self.settings, text='Chart Output Settings', padding=(5, 5, 5, 5))
        self.chart_output_frame.pack(expand=True, fill='x', pady=10, side='top')
        
        self.output_path_frame = Frame(self.chart_output_frame)
        self.output_path_frame.pack(side='top', expand=True, fill='both')
        
        self.output_path_label = Label(self.output_path_frame, text='Output Path')
        self.output_path_label.pack(side='left', padx=5, pady=5)
        
        self.output_path_input = Entry(self.output_path_frame, textvariable=self.output_path)
        self.output_path_input.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        
        self.output_path_btn = Button(self.output_path_frame, text='Browse...', style='Buttons.TButton', command=self.path_browse)
        self.output_path_btn.pack(side='left', padx=5, pady=5)
        
        self.chart_output_chk = ParameterTab(self.chart_output_frame, self.chart_chk_paras)
        self.chart_output_chk.tree.heading("1", text="Chart Type")
        self.chart_output_chk.tree.heading("2", text="Output")
        self.chart_output_chk.tree.configure(height=len(self.chart_types))
        self.chart_output_chk.pack(side='top', expand=True, fill='x')
        
        self.chart_output_btn_frame = Frame(self.chart_output_frame)
        self.chart_output_btn_frame.pack(side='top', expand=True, fill='x')

        output_all_btn = Button(self.chart_output_btn_frame, text='Output Selected Charts', command=self.output_charts)
        output_all_btn.pack(side='right', pady=5)
        
        
        # Output Test

        # img_test_btn = Button(self.buttons, text='Change Image', command=self.rotate_imgs)
        # img_test_btn.pack()

        # msg_test_btn = Button(self.buttons, text='Update Message', command=self.update_msg_test)
        # msg_test_btn.pack()
        
        # msg_clr_btn = Button(self.buttons, text='Clear Message', command=self.console_clr)
        # msg_clr_btn.pack()
        
        # preview_test_btn = Button(self.buttons, text='Preview Chart', command=self.preview_chart)
        # preview_test_btn.pack()

        # output_test_btn = Button(self.chart_output_frame, text='Output Charts', command=self.output_charts)
        # output_test_btn.pack()
        # output_test_btn.grid(row=2, column=2, sticky='E')
        
        # # Styling
        # self["style"] = "Background.TFrame"        
    
    def rotate_imgs(self):
        self.update_img(self.img_list[0])
        self.img_list.append(self.img_list.pop(0))
        return
        
    def update_msg_test(self):
        self.console('Message Text Update Test')
        return
        
    def init_parameters(self, dummy):
        # print(self.chart_settings.output_values())
        # save current settings before cleaning
        for p in self.chart_settings.output_values():
            self.saved_chart_paras[self.cur_chart_type][p[0]]['value'] = p[1]
                
        self.chart_settings.clear()
        self.cur_chart_type = self.chart_type.get()
        # print(self.saved_chart_paras[self.cur_chart_type])
        self.chart_settings.parameter_chg(self.saved_chart_paras[self.cur_chart_type])
        # self.chart_settings.delete(*self.chart_settings.get_children())
        # chart_type_selected = self.chart_type.get()
        # for p in CHART_PARAMETERS[chart_type_selected]:            
        #     id = self.chart_settings.insert('', 'end', values=(p, ''))
            
        return

    def path_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askdirectory(parent=self, initialdir=cur_path, title='Please select a directory')
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        self.output_path.set(temp_path)
        return
    
    def file_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.preset_path.set(temp_path)
        return


    def gen_chart(self, chart_type, para_list):        
        parsed_paras = []        
        for p in para_list:
            # print(f'{p[0]}, {type(p[1])}')
            parsed = p[1]
            if type(p[1]) == str: 
                if regex_color.search(p[1]):                    
                    parsed_str = p[1].split(',')
                    parsed = (int(parsed_str[0]), int(parsed_str[1]), int(parsed_str[2]))
                elif regex_coord.search(p[1]):
                    parsed_str = p[1].split('x')
                    parsed = (int(p[1].split('x')[0]), int(p[1].split('x')[1]))               
                elif p[0] == 'Line Type':
                    parsed = {'filled':cv2.FILLED, 'line_4':cv2.LINE_4, 'line_8':cv2.LINE_8, 'line_AA':cv2.LINE_AA}[p[1]]                 
            
            parsed_paras.append(parsed)
        # print(parsed_paras)
        # chart_im, _ = CHART_FN_DICT[self.chart_type.get()](*parsed_paras)
        chart_im, output_msg, _ = CHART_FN_DICT[chart_type](*parsed_paras)
        # print(type(chart_im))
        return chart_im, output_msg

    def preview_chart(self):        
        chart_type = self.chart_type.get()
        chart_im, output_msg = self.gen_chart(chart_type, self.chart_settings.output_values())
        # np.save('chart_im', chart_im)
        # cv2.imwrite('chart_im_cv.png', chart_im)         
        if len(chart_im[0][0]) == 3:
            chart_im_preview = Image.fromarray((chart_im).astype(np.uint8))
        else:
            chart_im_preview = Image.fromarray((chart_im[:, :, 0]).astype(np.uint8))
        # chart_im_preview.save('chart_im.png')
        self.preview_canvas.update_image(chart_im_preview)
        self.console(output_msg)
        return

    def output_charts(self):
        para_list = []
        output_path = self.output_path.get()
        output_name = ''
        timestr = time.strftime("%Y%m%d-%H-%M-%S")
        for c in self.chart_output_chk.output_values():
            if c[1] == 'Yes':
                output_name = c[0].replace(' ', '_')
                # print(c[0], self.saved_chart_paras[c[0]])
                for k in self.saved_chart_paras[c[0]].keys():
                    # print([k, self.saved_chart_paras[c[0]][k]['value']])
                    value = self.saved_chart_paras[c[0]][k]['value']
                    if k == 'Resolution' or k == 'Grid Dimension':
                        output_name += f'_{value}'
                    para_list.append([k, value])
                # print(para_list)
                self.console(f'Generating {c[0]}...', cr=False)
                chart_im, output_msg = self.gen_chart(c[0], para_list)
                self.console(f'Exporting...', cr=False)
                cv2.imwrite(f'{output_path}\\{output_name}_{timestr}.png', chart_im)
                self.console(f'Done', cr=True)

            para_list = []
        return

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