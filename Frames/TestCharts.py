import imp
from Frames.NetsFrame import *
# from tkinter.ttk import *

CHART_TYPES = ('Reticle', 'Circle Grid', 'Checkerboard', 'Grille', 'Slanted Edge MTF')
CHART_PARAMETERS = {'Reticle': ('Resolution', 'Line Color', 'Line Thickness', 'Cross Size', 'Marker Size'), 
                    'Circle Grid': ('Resolution', 'Grid Dimension', 'Marker Size', 'Padding'), 
                    'Checkerboard': ('Resolution', 'Grid Dimension', 'Begin With', 'Padding'), 
                    'Grille': ('Resolution', 'Grille Width', 'Orientation'), 
                    'Slanted Edge MTF': ('Resolution', 'Grid Dimension', 'Edge Angle', 'Pattern Size', 'Padding', 'Line Type')}

class TestCharts(NetsFrame):
    def __init__(self, window):
        super().__init__(window)
        self.chart_type = tk.StringVar()
        self.chart_type.set(CHART_TYPES[0])
        # Settings Test
        self.chart_selector = tk.OptionMenu(self.settings, self.chart_type, *CHART_TYPES, command=self.init_parameters)
        self.chart_selector.configure(anchor='w')
        self.chart_selector.pack(expand=True, fill='x')        
        
        self.chart_settings = Treeview(self.settings, columns=('Parameter', 'Value'), show='headings')
        self.chart_settings.heading('Parameter', text='Parameter', anchor='w')
        self.chart_settings.heading('Value', text='Value', anchor='w')
        self.chart_settings.pack()
        
        self.init_parameters('')
        # for p in CHART_PARAMETERS[CHART_TYPES[0]]:
        #     print(p)
        #     self.chart_settings.insert('', 'end', values=p)

        

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
        self.chart_settings.delete(*self.chart_settings.get_children())
        chart_type_selected = self.chart_type.get()
        for p in CHART_PARAMETERS[chart_type_selected]:            
            id = self.chart_settings.insert('', 'end', values=(p, ''))
            
        return
