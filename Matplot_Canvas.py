from textwrap import fill
import tkinter as tk
import numpy as np
from tkinter.ttk import *

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class MatPlot_Canvas(Frame):
    def __init__(self, window, chart_res):
        super().__init__(window)
        self.mesh = np.zeros((3, 4))
        
        self.chart_res = chart_res
        x = np.linspace(0, self.chart_res[0], self.mesh.shape[1])
        y = np.linspace(0, self.chart_res[1], self.mesh.shape[0])
        self.xx, self.yy = np.meshgrid(x, y) 
        
        self.fig = Figure(figsize=(4, 3), dpi=200)        
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.ax = self.fig.add_subplot()        
        
        # self.ax.pcolormesh(self.xx, self.yy, self.mesh, vmax=254, vmin=0)
        self.im = self.ax.imshow(self.mesh)
        
        
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top')
    
    def redraw(self):
        # x = np.linspace(0, self.chart_res[0], self.mesh.shape[1])
        # y = np.linspace(0, self.chart_res[1], self.mesh.shape[0])
        # self.xx, self.yy = np.meshgrid(x, y) 
        # self.ax.pcolormesh(self.xx, self.yy, self.mesh, vmax=254, vmin=0)
        # self.im.set_data(self.mesh)
        self.canvas.draw()


    def chg_mesh(self, chart_res, mesh, vmin, vmax, cmap='viridis'):
        grid_dim = mesh.shape
        x = np.linspace(0, chart_res[0], grid_dim[1])
        y = np.linspace(0, chart_res[1], grid_dim[0])
        xx, yy = np.meshgrid(x, y)        
        self.ax.pcolormesh(xx, yy, mesh, cmap=cmap, vmax=vmax, vmin=vmin)
        self.canvas.draw()
        return


if __name__=='__main__':
    root  = tk.Tk()
    chart_res = np.array([400, 300])
    mp_canvas = MatPlot_Canvas(root, chart_res)
    mp_canvas.pack()
    mesh_a = np.load('.\\Test Data\\mesh_1.npy')
    mesh_b = np.load('.\\Test Data\\mesh_2.npy')
    
    
    def mesh_test_a():
            print('mesh a')
            mp_canvas.mesh = mesh_a
            # mp_canvas.im = mp_canvas.ax.imshow(mp_canvas.mesh)
            mp_canvas.im.set_data(mesh_a)
            mp_canvas.im.set_clim(vmin=mesh_a.min(), vmax=mesh_a.max())
            mp_canvas.redraw()
        
    def mesh_test_b():
            print('mesh b')
            mp_canvas.mesh = mesh_b
            # mp_canvas.im = mp_canvas.ax.imshow(mp_canvas.mesh)
            mp_canvas.im.set_data(mesh_b)
            mp_canvas.im.set_clim(vmin=mesh_b.min(), vmax=mesh_b.max())
            mp_canvas.redraw()

    test_btn_1 = Button(root, text='test', command=mesh_test_a)
    test_btn_1.pack(side='left')
    test_btn_2 = Button(root, text='test', command=mesh_test_b)
    test_btn_2.pack(side='left')
    root.mainloop()

