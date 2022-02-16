import imp
from Frames.NetsFrame import *
from ParameterTab import *
import os
from tkinter import filedialog
from NED_Chart import *
import re
import time
# from tkinter.ttk import *

CHART_TYPES = ('Reticle', 'Circle Grid', 'Checkerboard', 'Grille', 'Slanted Edge MTF')

RETICLE_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Line Color': {'value':'0,255,0', 'type':'value', 'options':None},
                'Cross Size': {'value':20, 'type':'value', 'options':None},
                'Marker Size': {'value':10, 'type':'value', 'options':None},
                'Line Thickness': {'value':2, 'type':'value', 'options':None}}

CIRCLE_GRID_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grid Dimension': {'value':'64x36', 'type':'value', 'options':None},                
                'Marker Size': {'value':5, 'type':'value', 'options':None},
                'Padding': {'value':'10x10', 'type':'value', 'options':None}}

CHECKERBOARD_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grid Dimension': {'value':'32x18', 'type':'value', 'options':None},                
                'Begin with': {'value':'black', 'type':'list', 'options':('black', 'white')},
                'Padding': {'value':'0x0', 'type':'value', 'options':None}}

GRILLE_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grille Width': {'value':4, 'type':'value', 'options':None},                
                'Orientation': {'value':'vertical', 'type':'list', 'options':('vertical', 'horizontal')},
                }

SE_MTF_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grid Dimension': {'value':'32x18', 'type':'value', 'options':None},
                'Edge Angle': {'value':5, 'type':'value', 'options':None},
                'Pattern Size': {'value':80, 'type':'value', 'options':None},
                'Padding': {'value':'10x10', 'type':'value', 'options':None},                
                'Line Type': {'value':'line_8', 'type':'list', 'options':('line_8', 'line_4', 'line_AA', 'filled')},
                }

CHART_PARAMETERS = {'Reticle': RETICLE_PARAS, 
                    'Circle Grid': CIRCLE_GRID_PARAS, 
                    'Checkerboard': CHECKERBOARD_PARAS, 
                    'Grille': GRILLE_PARAS, 
                    'Slanted Edge MTF': SE_MTF_PARAS}

CHART_CHK_PARAS = {}
for c in CHART_TYPES:
    CHART_CHK_PARAS[c] = {'value':'Yes', 'type':'list', 'options':('Yes', 'No')}

CHART_FN_DICT = {'Reticle': gen_reticle, 
                    'Circle Grid': gen_circle_grid, 
                    'Checkerboard': gen_checkerboard, 
                    'Grille': gen_grille, 
                    'Slanted Edge MTF': gen_se_MTF}

OUTPUT_PATH = f'{os.getcwd()}\\Output'


regex_coord = re.compile(r'\d+x\d+')
regex_color = re.compile(r'\d+,\d+,\d+')



class TestCharts(NetsFrame):
    def __init__(self, window):
        super().__init__(window)
        self.chart_type = tk.StringVar()
        self.chart_type.set(CHART_TYPES[0])
        self.cur_chart_type = self.chart_type.get()
        self.saved_chart_paras = CHART_PARAMETERS
        self.output_path = tk.StringVar()
        self.output_path.set(OUTPUT_PATH)
        
        # chart parameter settings
        self.chart_settings_frame = LabelFrame(self.settings, text='Chart Parameter Settings', padding=(5, 5, 5, 5))
        self.chart_settings_frame.pack(expand=True, fill='x', pady=10, side='top')
        self.chart_settings_frame.columnconfigure(0, weight=1)
        self.chart_settings_frame.columnconfigure(1, weight=4)
        self.chart_settings_frame.columnconfigure(2, weight=1)        

        self.chart_selector_label = Label(self.chart_settings_frame, text='Chart Type')        
        self.chart_selector_label.grid(row=0, column=0, sticky='W')

        self.chart_selector = tk.OptionMenu(self.chart_settings_frame, self.chart_type, *CHART_TYPES, command=self.init_parameters)
        self.chart_selector.configure(anchor='w', width=30)                
        self.chart_selector.grid(row=0, column=1, stick='EW')

        self.chart_settings = ParameterTab(self.chart_settings_frame, CHART_PARAMETERS[CHART_TYPES[0]])       
        self.chart_settings.tree.configure(height=6)                    
        self.chart_settings.grid(row=1, column=0, columnspan=3, sticky='EW', pady=5)
        
        preview_test_btn = Button(self.chart_settings_frame, text='Preview Chart', command=self.preview_chart)
        preview_test_btn.grid(row=0, column=2, stick='E')

        # chart output settings
        
        self.chart_output_frame = LabelFrame(self.settings, text='Chart Output Settings', padding=(5, 5, 5, 5))
        self.chart_output_frame.pack(expand=True, fill='x', pady=10, side='top')
        self.chart_output_frame.columnconfigure(0, weight=1)
        self.chart_output_frame.columnconfigure(1, weight=10)   
        self.chart_output_frame.columnconfigure(2, weight=1)

        self.output_path_label = Label(self.chart_output_frame, text='Output Path')        
        self.output_path_label.grid(row=0, column=0, sticky='W')
        self.output_path_input = Entry(self.chart_output_frame, textvariable=self.output_path)
        self.output_path_input.grid(row=0, column=1, sticky='EW', ipady=5)
        self.output_path_btn = Button(self.chart_output_frame, text='Browse...', style='Buttons.TButton', command=self.path_browse)
        self.output_path_btn.grid(row=0, column=2, sticky='E')

        self.chart_output_chk = ParameterTab(self.chart_output_frame, CHART_CHK_PARAS)
        self.chart_output_chk.tree.heading("1", text="Chart Type")
        self.chart_output_chk.tree.heading("2", text="Output")
        self.chart_output_chk.tree.configure(height=len(CHART_TYPES))
        # self.chart_output_chk.pack(side='top')
        self.chart_output_chk.grid(row=1, column=0, columnspan=3, sticky='EW', pady=5)

        # Output Test

        img1 = Image.open('.\Temp\img01.png')
        img2 = Image.open('.\Temp\img02.png')
        img3 = Image.open('.\Temp\img03.png')
        img4 = Image.open('.\Temp\img_large.png')
        
        self.img_list = [img4]

        img_test_btn = Button(self.buttons, text='Change Image', command=self.rotate_imgs)
        img_test_btn.pack()

        msg_test_btn = Button(self.buttons, text='Update Message', command=self.update_msg_test)
        msg_test_btn.pack()
        
        msg_clr_btn = Button(self.buttons, text='Clear Message', command=self.console_clr)
        msg_clr_btn.pack()
        
        preview_test_btn = Button(self.buttons, text='Preview Chart', command=self.preview_chart)
        preview_test_btn.pack()

        output_test_btn = Button(self.buttons, text='Output Charts', command=self.output_charts)
        output_test_btn.pack()
        
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
        self.chart_settings.parameter_chg(self.saved_chart_paras[self.cur_chart_type], self.cur_chart_type)
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