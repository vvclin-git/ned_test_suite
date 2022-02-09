import imp
from Frames.NetsFrame import *
# from tkinter.ttk import *

class TestCharts(NetsFrame):
    def __init__(self, window):
        super().__init__(window)
        print(self.msg.get())
        
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
        
    
    