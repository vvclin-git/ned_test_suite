from textwrap import fill
import tkinter as tk
from turtle import bgcolor
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
from ZoomCanvas import *

class NetsFrame(Frame):
    def __init__(self, window):
        super().__init__(window)
        
        self.preset_path = ''        
        self.msg = tk.StringVar()
        self.msg.set('Message Output')
        self.presets = None
        
        self.columnconfigure(0, weight=2, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)
        self.rowconfigure(0, weight=1, uniform=1)

        output = Frame(self, style='Output.TFrame', width=980, height=960, padding=(10, 10))
        # output = Frame(self, style='Output.TFrame', padding=(10, 10))   
        output.grid(row=0, column=0, sticky="NEWS")
        # output.pack_propagate(0)
        # output.pack(side='left', expand=True, fill='both')
        # preview_frame = LabelFrame(output, text='Preview Image', width=960, height=740, style='Test.TLabelframe')                
        preview_frame = LabelFrame(output, text='Preview Image', style='Test.TLabelframe')   
        preview_frame.pack(side='top', expand=True, fill='both', pady=(0, 20))      
        # preview_frame.pack_propagate(0)        
        img = np.zeros([720, 960, 3], dtype=np.uint8)
        cv2.putText(img, 'Preview Image', (400, 330), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        # img = Image.fromarray(img)

        self.preview_img = Image.fromarray(img)        
        self.preview_canvas = Zoom_Advanced(preview_frame, self.preview_img)     
        
        msg_frame = LabelFrame(output, width=960, height=160, text='Output Message', style='TLabelframe')        
        # msg_frame = LabelFrame(output, text='Output Message', style='TLabelframe')  
        # msg_frame.pack(side='top', expand=True, fill='x')
        # msg_frame.pack_propagate(0)
        
        self.msg_output = tk.Text(msg_frame, height=10, state='disabled')
        self.msg_output.pack(side=tk.LEFT, expand=True, fill='both')
        msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL, command=self.msg_output.yview)
        self.msg_output['yscrollcommand'] = msg_scroll.set
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Settings
        # self.settings = Frame(self, style='Settings.TFrame', width=500, height=720, padding=(10, 10))
        self.settings = Frame(self, style='Settings.TFrame', padding=(10, 10))
        # self.pack_propagate(0)
        self.settings.grid(row=0, column=1, sticky='NEWS')
        # self.settings.pack(side='left', expand=True, fill='both')
        # Preset Save / Load
        self.preset_frame = LabelFrame(self.settings, text='Parameter Preset', padding=(2, 2, 2, 2))
        self.preset_frame.pack(expand=True, fill='x', pady=5, side='top')

        self.preset_input_frame = Frame(self.preset_frame)
        self.preset_input_frame.pack(side='top', expand=True, fill='both')
        self.preset_btn_frame = Frame(self.preset_frame)
        self.preset_btn_frame.pack(side='top', expand=True, fill='both')
        
        self.preset_path_label = Label(self.preset_input_frame, text='Preset Path')
        self.preset_path_label.pack(side='left', padx=5, pady=5)
        self.preset_path_input = Entry(self.preset_input_frame, textvariable=self.preset_path)
        self.preset_path_input.pack(side='left', padx=5, pady=5, expand=True, fill='both')
                
        self.preset_browse_btn = Button(self.preset_btn_frame, text='Browse...', style='Buttons.TButton', command=None)
        self.preset_browse_btn.pack(side='right', padx=2, pady=5)
        self.preset_load_btn = Button(self.preset_btn_frame, text='Load...', style='Buttons.TButton', command=None)
        self.preset_load_btn.pack(side='right', padx=2, pady=5)
        self.preset_save_btn = Button(self.preset_btn_frame, text='Save As...', style='Buttons.TButton', command=None)        
        self.preset_save_btn.pack(side='right', padx=2, pady=5)

        # self.buttons = Frame(self, style='Buttons.TFrame', width=500, height=240)
        # self.buttons = Frame(self, style='Buttons.TFrame')
        # self.buttons.grid(row=1, column=1, sticky='EW')
    
    def console(self, msg, cr=True):
        self.msg_output.config(state='normal')
        if cr:
            self.msg_output.insert('end', msg + '\n')
        else:
            self.msg_output.insert('end', msg)
        self.msg_output.config(state='disabled')
        return
    
    def console_clr(self):
        self.msg_output.config(state='normal')
        self.msg_output.delete('1.0', 'end')
        self.msg_output.config(state='disabled')
    
    def update_img(self, img):
        self.preview_canvas.update_image(img)
        return
    
    def preset_browse(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.preset_path.set(temp_path)
        return
    
    def preset_load(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        return

    def preset_save(self):
        preset_path = self.preset_path.get()
        if os.path.isfile(preset_path):
            chk_overwrite = tk.messagebox.askquestion(title='Confirm Overwrite', message='File already exists, overwrite?')
            if not chk_overwrite:
                return                
        f = open(preset_path, 'w')
        save_preset = self.presets
        json.dump(save_preset, f)
        f.close()
        self.console(f'Preset File: {preset_path} Saved')
        return
    


if __name__=='__main__':
    root = tk.Tk()
    # root.geometry('1680x990')
    nets_frame = NetsFrame(root)
    nets_frame.pack()
    root.mainloop()

