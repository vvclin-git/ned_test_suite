
import tkinter as tk
from tkinter.ttk import *
from Widgets.ParameterTab import ParameterTab
from matplotlib import pyplot as plt

draper_paras = {'Sensor Resolution': {'value':'2250x1305', 'type':'value', 'options':None},
              'Sensor Size': {'value':'7.46x4.14', 'type':'value', 'options':None},
              'Camera Eff': {'value':8, 'type':'value', 'options':None},
              'Far Mesh Distance': {'value':200, 'type':'value', 'options':None},
              }

eyebox_vol_paras = {'Project Plane Grid': {'value':'-10,10,21', 'type':'value', 'options':None},
              '3D View Angle': {'value':'35,135', 'type':'value', 'options':None},
              'Aperture Depth': {'value':'2,10,5', 'type':'value', 'options':None}              
              }

class EyeboxVolEval(Frame):
    def __init__(self, window):
        super().__init__(window)

        self.area_chart_chk = tk.IntVar()
        self.controller = None
        self.output_path = None
        
        self.draper_paras_tab = ParameterTab(self, draper_paras)
        self.draper_paras_tab.fit_height()
        self.draper_paras_tab.pack(side='top')

        self.eyebox_vol_paras_tab = ParameterTab(self, eyebox_vol_paras)
        self.eyebox_vol_paras_tab.fit_height()
        self.eyebox_vol_paras_tab.pack(side='top')

        output_cmd_frame = Frame(self)
        output_cmd_frame.pack(side='top', expand=1, fill='x')

        preview_btn = Button(output_cmd_frame, text='Preview')
        preview_btn.pack(side='right')
        export_btn = Button(output_cmd_frame, text='Export')
        export_btn.pack(side='right')

    def set_controller(self, controller):
        self.controller = controller

  


        

    
