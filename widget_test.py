import tkinter as tk
from Widgets.MeshPreviewBox import *
from Widgets.MeshProcessBox import *
from Widgets.MsgBox import *

class Controller():    
    def __init__(self, msg_box):
        self.msg_box = msg_box
        return


root = tk.Tk()
preview_img_size = (400, 300)

mp_box = MeshPreviewBox(root, preview_img_size)
# mp_box = MeshProcessBox(root, preview_img_size)
mp_box.pack()

msg_box = MsgBox(root)
controller = Controller(msg_box)
mp_box.set_controller(controller)
msg_box.pack()

root.mainloop()