
import tkinter as tk
from tkinter import Button, ttk
import re

regex_dim = re.compile(r'^\d+x\d+$')
regex_dim_float = re.compile(r'^\d+.\d+x\d+.\d+$')
regex_coord = re.compile(r'^\d+,\d+$')
regex_color = re.compile(r'^\d+,\d+,\d+$')
regex_float = re.compile(r'^[-]*\d+[.]\d+$')
regex_list = re.compile(r'(.+?)(?:,|$)')
regex_int = re.compile(r'^[-]*[1-9]\d*$')

class ParameterTab(ttk.Frame):
    def __init__(self, parent, parameters):
        super().__init__(parent)
        self.parameters = parameters     
        self.tree = ttk.Treeview(self, show='headings', columns=("1", "2"))
        self.tree['show'] = 'headings'

        self.tree.column("1")
        self.tree.heading("1", text="Parameter")
        self.tree.column("2")
        self.tree.heading("2", text="Value")
        
        for p in self.parameters:            
            self.tree.insert("", "end", values=(p, self.parameters[p]['value']), tags=self.parameters[p]['type'])              
        
        self.tree.tag_bind('value', '<1>', self.val_edit)
        self.tree.tag_bind('list', '<1>', self.list_edit)
        self.tree.pack(fill='x', expand=True)        
    
    def val_edit(self, event): # value edit event handler
        if self.tree.identify_region(event.x, event.y) == 'cell':
            # the user clicked on a cell
            column = self.tree.identify_column(event.x)  # identify column
            item = self.tree.identify_row(event.y)  # identify item                
            # print(self.tree.item(item)['tags'])
            if column == '#2': # only value column is allowed for editing
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                def ok(event):
                    """Change item value."""
                    self.tree.set(item, column, entry.get())
                    entry.destroy()
            else:
                return
        else:
            return
        # display the Entry   
        entry = ttk.Entry(self.tree)  # create edition entry
        entry.place(x=x, y=y, width=width, height=height, anchor='nw')  # display entry on top of cell
        entry.insert(0, value)  # put former value in entry
        entry.bind('<FocusOut>', lambda e: entry.destroy())  
        entry.bind('<Return>', ok)  # validate with Enter
        entry.focus_set()

    def list_edit(self, event): # drop-down list edit event handler
        if self.tree.identify_region(event.x, event.y) == 'cell':
            # the user clicked on a cell
            column = self.tree.identify_column(event.x)  # identify column
            item = self.tree.identify_row(event.y)  # identify item                
            # print(self.tree.item(item)['tags'])
            if column == '#2':
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                para_name = self.tree.set(item, '#1')
                options = self.parameters[para_name]['options']
                def ok(event, dummy_1, dummy_2):
                    """Change item value."""
                    self.tree.set(item, column, val.get())
                    val_list.destroy()
            else:
                return
        else:
            return
        # display the drop-down list   
        val = tk.StringVar()
        val_list = ttk.OptionMenu(self.tree, val, options[0], *options)  # create drop-down list
        val_list.place(x=x, y=y, width=width, height=height, anchor='nw')  # display drop-down on top of cell
        val.set(value)  # put former value in entry
        val_list.bind('<FocusOut>', lambda e: val_list.destroy())              
        val.trace('w', ok) # drop-down list value change event 
        val_list.focus_set()

    def output_values(self):
        output = []
        for p in self.tree.get_children():
            output.append(self.tree.item(p)['values'])
        return output
    
    def output_parsed_vals(self):
        output_vals = self.output_values()
        parsed_paras = []
        for p in output_vals:
            parsed = p[1]
            if type(p[1]) == str:
                if len(p[1].split(',')) > 1:
                    parsed = self.list_parser(p[1])
                else: 
                    if regex_color.search(p[1]):                    
                        parsed_str = p[1].split(',')
                        parsed = (int(parsed_str[0]), int(parsed_str[1]), int(parsed_str[2]))
                    elif regex_dim.search(p[1]):
                        parsed_str = p[1].split('x')
                        parsed = (int(p[1].split('x')[0]), int(p[1].split('x')[1]))               
                    elif regex_coord.search(p[1]):
                        parsed_str = p[1].split(',')
                        parsed = (int(parsed_str[0]), int(parsed_str[1]))
                    elif p[0] == 'Line Type':
                        parsed = {'filled':cv2.FILLED, 'line_4':cv2.LINE_4, 'line_8':cv2.LINE_8, 'line_AA':cv2.LINE_AA}[p[1]] 
                    elif regex_dim_float.search(p[1]):
                        parsed = (float(p[1].split('x')[0]), float(p[1].split('x')[1]))
                    elif regex_float.search(p[1]):
                        parsed = float(p[1])
            
            parsed_paras.append(parsed)
        return parsed_paras

    
    def list_parser(self, in_str):        
        output = []
        in_str_list = in_str.split(',')
        for s in in_str_list:
            if regex_color.search(s):                    
                parsed_str = s.split(',')
                parsed = (int(parsed_str[0]), int(parsed_str[1]), int(parsed_str[2]))
            elif regex_dim.search(s):
                parsed_str = s.split('x')
                parsed = (int(s.split('x')[0]), int(s.split('x')[1]))               
            elif regex_coord.search(s):
                parsed_str = s.split(',')
                parsed = (int(parsed_str[0]), int(parsed_str[1]))              
            elif regex_float.search(s):
                parsed = float(s)
            elif regex_dim_float.search(s):
                parsed = (float(s.split('x')[0]), float(s.split('x')[1]))            
            elif regex_int.search(s):
                parsed = int(s)
            else:
                parsed = s
            output.append(parsed)
        return output

    # def output_parsed_vals(self):
    #     output_vals = self.output_values()
    #     parsed_paras = []
    #     for p in output_vals:
    #         parsed = p[1]
    #         if type(p[1]) == str: 
    #             if regex_color.search(p[1]):                    
    #                 parsed_str = p[1].split(',')
    #                 parsed = (int(parsed_str[0]), int(parsed_str[1]), int(parsed_str[2]))
    #             elif regex_dim.search(p[1]):
    #                 parsed_str = p[1].split('x')
    #                 parsed = (int(p[1].split('x')[0]), int(p[1].split('x')[1]))               
    #             elif regex_coord.search(p[1]):
    #                 parsed_str = p[1].split(',')
    #                 parsed = (int(parsed_str[0]), int(parsed_str[1]))
    #             elif p[0] == 'Line Type':
    #                 parsed = {'filled':cv2.FILLED, 'line_4':cv2.LINE_4, 'line_8':cv2.LINE_8, 'line_AA':cv2.LINE_AA}[p[1]]  
    #             elif regex_float.search(p[1]):
    #                 parsed = float(p[1])
    #             elif regex_dim_float.search(p[1]):
    #                 parsed = (float(p[1].split('x')[0]), float(p[1].split('x')[1]))
            
    #         parsed_paras.append(parsed)
    #     return parsed_paras

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        return
    
    def parameter_chg(self, selected_parameters):
        self.clear()
        self.parameters = selected_parameters
        for p in selected_parameters:
            print(p)            
            self.tree.insert("", "end", values=(p, selected_parameters[p]['value']), tags=selected_parameters[p]['type'])
        return
    
    def fit_height(self):
        height = len(self.parameters)
        self.tree.configure(height=height)
        return

if __name__ == '__main__':
    root = tk.Tk()
    parameters = {'Parameter 1': {'value':1, 'type':'value', 'options':None},
                  'Parameter 2': {'value':2, 'type':'value', 'options':None},
                  'Parameter 3': {'value':'a', 'type':'list', 'options':('a', 'b', 'c')},
                  'Parameter 4': {'value':'e', 'type':'list', 'options':('e', 'f', 'g')},
                  'Parameter 5': {'value':0.001, 'type':'value', 'options':None}}
    
    para_tab = ParameterTab(root, parameters)
    para_tab.pack()
        
    def print_parsed_vals():
        parsed = para_tab.output_parsed_vals()
        for v in parsed:
            print(f'Type: {type(v)}, Value: {v}')
    
    parse_test_btn = Button(root, text='Print Parsed Values', command=print_parsed_vals)
    parse_test_btn.pack()
    root.mainloop()