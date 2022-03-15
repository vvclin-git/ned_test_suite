
from Frames.Draper import *
from Widgets.MeshPreviewBox import MeshPreviewBox
import tkinter as tk


root = tk.Tk()
preview_img_size = (480, 320)


draper = Draper(root, preview_img_size)
draper.pack()
root.mainloop()