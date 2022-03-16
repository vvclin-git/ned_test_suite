
import tkinter as tk
from tkinter.ttk import *
from Widgets.ParameterTab import ParameterTab

draper_paras = {'Sensor Resolution': {'value':1, 'type':'value', 'options':None},
              'Sensor Size': {'value':50, 'type':'value', 'options':None},
              'Camera Eff': {'value':100, 'type':'value', 'options':None},
              'Far Mesh Distance': {'value':0.1, 'type':'value', 'options':None},
              }

class EyeboxVol(Frame):
    def __init__(window):
        super().__init__(window)

        draper_paras_tab = ParameterTab(self, )