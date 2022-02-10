import imp
from Frames.NetsFrame import *
from ParameterTab import *
# from tkinter.ttk import *

CHART_TYPES = ('Reticle', 'Circle Grid', 'Checkerboard', 'Grille', 'Slanted Edge MTF')

RETICLE_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Line Color': {'value':'green', 'type':'value', 'options':None},
                'Line Thickness': {'value':2, 'type':'value', 'options':None},
                'Cross Size': {'value':5, 'type':'value', 'options':None},
                'Marker Size': {'value':1, 'type':'value', 'options':None}}

CIRCLE_GRID_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grid Dimension': {'value':'2560x1440', 'type':'value', 'options':None},                
                'Marker Size': {'value':1, 'type':'value', 'options':None},
                'Padding': {'value':1, 'type':'value', 'options':None}}

CHECKERBOARD_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grid Dimension': {'value':'2560x1440', 'type':'value', 'options':None},                
                'Begin with': {'value':'black', 'type':'list', 'options':('black', 'white')},
                'Padding': {'value':0, 'type':'value', 'options':None}}

GRILLE_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grille Width': {'value':4, 'type':'value', 'options':None},                
                'Orientation': {'value':'vertical', 'type':'list', 'options':('vertical', 'horizontal')},
                }

SE_MTF_PARAS = {'Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                'Grid Dimension': {'value':'2560x1440', 'type':'value', 'options':None},
                'Edge Angle': {'value':5, 'type':'value', 'options':None},
                'Pattern Size': {'value':5, 'type':'value', 'options':None},
                'Padding': {'value':5, 'type':'value', 'options':None},                
                'Line type': {'value':'line8', 'type':'list', 'options':('line8', 'line4')},
                }

CHART_PARAMETERS = {'Reticle': RETICLE_PARAS, 
                    'Circle Grid': CIRCLE_GRID_PARAS, 
                    'Checkerboard': CHECKERBOARD_PARAS, 
                    'Grille': GRILLE_PARAS, 
                    'Slanted Edge MTF': SE_MTF_PARAS}

class TestCharts(NetsFrame):
    def __init__(self, window):
        super().__init__(window)
        self.chart_type = tk.StringVar()
        self.chart_type.set(CHART_TYPES[0])
        # Settings Test
        self.chart_selector = tk.OptionMenu(self.settings, self.chart_type, *CHART_TYPES, command=self.init_parameters)
        self.chart_selector.configure(anchor='w')
        self.chart_selector.pack(expand=True, fill='x')        
        
        self.chart_settings = ParameterTab(self.settings, CHART_PARAMETERS[CHART_TYPES[0]])       
        self.chart_settings.pack()              

        # Output Test
        img1 = ImageTk.PhotoImage(file='.\Temp\img01.png')
        img2 = ImageTk.PhotoImage(file='.\Temp\img02.png')
        img3 = ImageTk.PhotoImage(file='.\Temp\img03.png')
        self.img_list = [img1, img2, img3]

        img_test_btn = Button(self.buttons, text='Change Image', command=self.rotate_imgs)
        img_test_btn.pack()

        msg_test_btn = Button(self.buttons, text='Update Message', command=self.update_msg_test)
        msg_test_btn.pack()
        
        msg_clr_btn = Button(self.buttons, text='Clear Message', command=self.console_clr)
        msg_clr_btn.pack()
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
        self.chart_settings.clear()
        chart_type_selected = self.chart_type.get()
        print(CHART_PARAMETERS[chart_type_selected])
        self.chart_settings.parameter_chg(CHART_PARAMETERS[chart_type_selected])
        # self.chart_settings.delete(*self.chart_settings.get_children())
        # chart_type_selected = self.chart_type.get()
        # for p in CHART_PARAMETERS[chart_type_selected]:            
        #     id = self.chart_settings.insert('', 'end', values=(p, ''))
            
        return
