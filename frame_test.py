
from Frames.Draper import *
from Frames.NetsFrame2 import *
from Frames.SMTF import *
from Frames.TestCharts import TestCharts
from Frames.Distortion import Distortion
from Widgets.MeshPreviewBox import MeshPreviewBox
import tkinter as tk
from tkinter.ttk import *


                     



# root = tk.Tk()
# preview_img_size = (480, 320)


# # draper = Draper(root, preview_img_size)
# # draper.pack()
# mp = MeshPreviewBox(root, preview_img_size)
# mp.pack()
# root.mainloop()


root = tk.Tk()
root.geometry('1480x990')
preview_img_size = (960, 740)
nets_frame = Distortion(root, preview_img_size)
nets_frame.pack(expand=1, fill='both')
root.mainloop()