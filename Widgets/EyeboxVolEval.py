
import tkinter as tk
from tkinter.ttk import *
from NED_Analyzer import Draper_Eval
from Widgets.ParameterTab import ParameterTab
from matplotlib import pyplot as plt
from NED_Analyzer import Draper_Eval
import numpy as np

# draper_paras = {'Sensor Resolution': {'value':'2250x1305', 'type':'value', 'options':None},
#               'Sensor Size': {'value':'7.46x4.14', 'type':'value', 'options':None},
#               'Camera Eff': {'value':8, 'type':'value', 'options':None},
#               'Far Mesh Distance': {'value':200, 'type':'value', 'options':None},
#               }

# eyebox_view_paras = {'Project Plane Grid': {'value':'-10,10,21', 'type':'value', 'options':None},
#               '3D View Angle': {'value':'35,135', 'type':'value', 'options':None},
#               'Aperture Depth': {'value':'2,10,5', 'type':'value', 'options':None}              
            #   }

class EyeboxVolEval(Frame):
    def __init__(self, window):
        super().__init__(window)

        self.area_chart_chk = tk.IntVar()
        self.controller = None
        self.output_path = None
        self.sensor_res = None 
        self.sensor_size = None 
        self.camera_eff = None 
        self.camera_distance = None
        self.proj_pts = None 
        self.roi_pts = None 
        self.proj_theta_phi = None
        self.alpha = (0.5, 0, 0.1)
        self.draper_paras = {}
        self.eyebox_view_paras = {}
        
        self.draper_frame = LabelFrame(self, text='Eyebox Volume Evaluation')
        self.draper_frame.pack(side='top', expand=1, fill='both')
        self.draper_paras_tab = ParameterTab(self.draper_frame, self.draper_paras)
        # self.draper_paras_tab.fit_height()
        self.draper_paras_tab.pack(side='top')
        self.draper_btn_frame = Frame(self.draper_frame)
        self.draper_btn_frame.pack(side='top', expand=1, fill='x')
        self.draper_eval_btn = Button(self.draper_btn_frame, text='Evaluate', command=self.eyebox_eval)
        self.draper_eval_btn.pack(side='right')
        self.draper_init_btn = Button(self.draper_btn_frame, text='Initialize', command=self.init_draper)
        self.draper_init_btn.pack(side='right')


        self.eyebox_view_frame = LabelFrame(self, text='Eyebox View Settings')
        self.eyebox_view_frame.pack(side='top', expand=1, fill='both')
        self.eyebox_view_paras_tab = ParameterTab(self.eyebox_view_frame, self.eyebox_view_paras)
        # self.eyebox_view_paras_tab.fit_height()
        self.eyebox_view_paras_tab.pack(side='top')
        self.eyebox_view_btn_frame = Frame(self.eyebox_view_frame)
        self.eyebox_view_btn_frame.pack(side='top', expand=1, fill='both')
        self.eyebox_view_export_btn = Button(self.eyebox_view_btn_frame, text='Export')
        self.eyebox_view_export_btn.pack(side='right')
        self.eyebox_view_btn = Button(self.eyebox_view_btn_frame, text='Show Results', command=self.draw_eyebox_vol)
        self.eyebox_view_btn.pack(side='right')
        

    def init_draper(self):
        self.sensor_res, self.sensor_size, self.camera_eff, self.camera_distance = self.draper_paras_tab.output_parsed_vals()
        self.output_path = self.controller.path_browse.output_path.get()
        self.controller.draper_eval = Draper_Eval(self.camera_eff, self.sensor_res, self.sensor_size, self.output_path)
        self.controller.msg_box.console('Draper analysis initialized')

    def eyebox_eval(self):
        self.pupil_aper_pts = self.controller.pupil_mesh_process.border_coords
        self.controller.draper_eval.init_pupil_image(self.pupil_aper_pts)
        self.far_aper_pts = self.controller.far_mesh_process.border_coords
        self.proj_pts, self.roi_pts, self.proj_theta_phi = self.controller.draper_eval.get_eyebox_aperture_pupil(self.camera_distance, self.far_aper_pts)
        self.controller.msg_box.console('Eyebox volume evaluaton completed')
    
    def draw_eyebox_vol(self):
        self.proj_plane_grid, self.view, self.plot_range, self.aper_depth_grid = self.eyebox_view_paras_tab.output_parsed_vals()
        self.proj_plane_grid = np.linspace(*self.proj_plane_grid)
        self.aper_depth_grid = np.linspace(*self.aper_depth_grid)
        x_range, y_range, z_range = self.plot_range
        x_min, x_max = x_range * -0.5, x_range * 0.5
        z_min, z_max = z_range * -0.5, z_range * 0.5
        y_min, y_max = 0, y_range
        aper_pts_list, ax, fig = self.controller.draper_eval.draw_eyebox_volume(self.proj_pts, self.roi_pts, self.proj_theta_phi, self.proj_plane_grid, self.aper_depth_grid, self.view, self.alpha)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)
        ax.set_box_aspect((x_range, y_range, z_range))   
        fig.show()
        return


    def set_controller(self, controller):
        self.controller = controller


  


        

    
