from textwrap import fill
import tkinter as tk
from turtle import bgcolor
import cv2
import numpy as np
from tkinter.ttk import *
from PIL import Image, ImageTk
from ZoomCanvas import *
import os
import json
from tkinter import filedialog

class NetsFrame(Frame):
    def __init__(self, window, preview_img_size):
        super().__init__(window)
        
        self.preset_path = tk.StringVar()                
        self.presets = None
        self.preview_img_size = preview_img_size
        self.columnconfigure(0, weight=2, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)
        self.rowconfigure(0, weight=1, uniform=1)
        
        # Output container settings
        output = Frame(self, style='Output.TFrame', padding=(10, 10))   
        output.grid(row=0, column=0, sticky="NEWS")
        output.rowconfigure(0, weight=5, uniform=1)
        output.rowconfigure(1, weight=1, uniform=1)
        output.columnconfigure(0, weight=1)
        
        # Preview Image Widget
        img_width = self.preview_img_size[0]
        img_height = self.preview_img_size[1]                     
        preview_frame = LabelFrame(output, text='Preview Image', style='Test.TLabelframe')           
        preview_frame.grid(row=0, column=0, sticky='NEWS', pady=(0, 10))           
        
        img = np.zeros([img_height, img_width, 3], dtype=np.uint8)
        preview_img_text = f'Preview Image ({img_width} x {img_height})'
        
        preview_img_text_size = cv2.getTextSize(preview_img_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
        preview_img_text_pos = (int((img_width - preview_img_text_size[0][0]) * 0.5), int((img_height - preview_img_text_size[0][1]) * 0.5))        
        cv2.putText(img, preview_img_text, preview_img_text_pos, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 0), fontScale=1, thickness=1)        
        
        self.preview_img = Image.fromarray(img)        
        self.preview_canvas = Zoom_Advanced(preview_frame, self.preview_img)             

        # Message Output     
        msg_frame = LabelFrame(output, text='Output Message', style='TLabelframe')  
        msg_frame.grid(row=1, column=0, sticky='NEWS')
                
        self.msg_output = tk.Text(msg_frame, height=10, state='disabled')
        self.msg_output.pack(side=tk.LEFT, expand=True, fill='both')
        msg_scroll = Scrollbar(msg_frame, orient=tk.VERTICAL, command=self.msg_output.yview)
        self.msg_output['yscrollcommand'] = msg_scroll.set
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Settings Container Settings        
        self.settings = Frame(self, style='Settings.TFrame', padding=(10, 10))        
        self.settings.grid(row=0, column=1, sticky='NEW')
                
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
                

        self.preset_save_btn = Button(self.preset_btn_frame, text='Save As...', style='Buttons.TButton', command=self.save_preset)        
        self.preset_save_btn.pack(side='right', padx=2, pady=5)
        self.preset_load_btn = Button(self.preset_btn_frame, text='Load...', style='Buttons.TButton', command=self.load_preset)
        self.preset_load_btn.pack(side='right', padx=2, pady=5)
        self.preset_browse_btn = Button(self.preset_btn_frame, text='Browse...', style='Buttons.TButton', command=self.browse_preset)
        self.preset_browse_btn.pack(side='right', padx=2, pady=5)

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
    
    def browse_preset(self):
        cur_path = os.getcwd()
        temp_path = filedialog.askopenfilename(parent=self, initialdir=cur_path, title='Please select a JSON file', filetypes=[("JSON files","*.json")])
        # if len(temp_path) > 0:
        #     print ("You chose: %s" % tempdir)
        if len(temp_path) > 0:            
            self.preset_path.set(temp_path)
        return
    
    def load_preset(self):
        f = open(self.preset_path.get(), 'r')
        self.presets = json.load(f)
        f.close()
        self.console(f'Preset File: {self.preset_path.get()} Loaded')
        return

    def save_preset(self):
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
    root.geometry('1680x990')
    preview_img_size = (960, 740)
    nets_frame = NetsFrame(root, preview_img_size)
    nets_frame.pack()
    root.mainloop()

