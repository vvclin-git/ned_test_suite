
from Frames.Draper import *
from Frames.NetsFrame import *
from Frames.SMTF import *
from Frames.TestCharts import TestCharts
from Frames.Distortion import Distortion
from Widgets.MeshPreviewBox import MeshPreviewBox
from Frames.Grille import Grille
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
preview_img_size = (640, 480)
nets_frame = NetsFrame(root, preview_img_size)
nets_frame.pack(expand=1, fill='both')
root.mainloop()