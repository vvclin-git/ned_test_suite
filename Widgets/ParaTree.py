

import tkinter as tk
from tkinter.ttk import *
import json
import re
import cv2
from tkinter import messagebox


class ParaTree(Frame):
    def __init__(self, parent, tree_paras):
        super().__init__(parent)
        
        # self.parameters = parameters
        self.chart_types = tree_paras['chart_types']
        self.chart_parameters = tree_paras['chart_parameters']
        self.chart_chk_paras = tree_paras['chart_chk_paras']
        
        self.tree = Treeview(self)
        self.tree.pack(expand=1, fill='both')        
        self.tree['columns'] = ('Value', 'Export')
                
        self.tree.column('Value', anchor=tk.W)
        self.tree.column('Export', anchor=tk.W)
        self.tree.heading('#0', text='Parameter', anchor=tk.W)
        self.tree.heading('Value', text='Values', anchor=tk.W)
        self.tree.heading('Export', text='Export', anchor=tk.W)

        self.tree.tag_bind('value', '<1>', self.val_edit)
        self.tree.tag_bind('list', '<1>', self.list_edit)
        
        for i, t in enumerate(self.chart_types):
            self.tree.insert('', tk.END, text=t, value=('', self.chart_chk_paras[t]['value']), tags=self.chart_chk_paras[t]['type'], iid=t, open=False)
            for j, k in enumerate(self.chart_parameters[t].keys()):
                self.tree.insert(t, tk.END, text=k, value=self.chart_parameters[t][k]['value'], tags=self.chart_parameters[t][k]['type'], iid=f'{t}_{k}', open=False)

    def val_edit(self, event): # value edit event handler
        if self.tree.identify_region(event.x, event.y) == 'cell':
            # the user clicked on a cell
            column = self.tree.identify_column(event.x)  # identify column
            item = self.tree.identify_row(event.y)  # identify item                
            # print(self.tree.item(item)['tags'])
            if column == '#1': # only value column is allowed for editing
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                
                def ok(event):
                    """Change item value."""
                    # para_name = self.tree.set(item, '#1')
                    chart_type = item.split('_')[0]
                    para_name = item.split('_')[1]
                    regex = re.compile(eval(self.chart_parameters[chart_type][para_name]['regex']))
                    if regex.search(entry.get()):
                        self.tree.set(item, column, entry.get())
                        entry.destroy()
                    else:
                        messagebox.showinfo('Input Validation', 'Wrong input format!')
                        return

            else:
                return
        else:
            return
        # display the Entry   
        entry = Entry(self.tree)  # create edition entry
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
            # if column == '#1':
            #     x, y, width, height = self.tree.bbox(item, column) 
            #     value = self.tree.set(item, column)
            #     # para_name = self.tree.set(item, '#1')
            #     chart_type = item.split('_')[0]
            #     para_name = item.split('_')[1]
            #     options = self.chart_parameters[chart_type][para_name]['options']
            #     def ok(event, dummy_1, dummy_2):
            #         """Change item value."""
            #         self.tree.set(item, column, val.get())
            #         val_list.destroy()
            
            if column == '#1' or (column == '#2' and len(item.split('_')) == 1):
                x, y, width, height = self.tree.bbox(item, column) 
                value = self.tree.set(item, column)
                # para_name = self.tree.set(item, '#1')
                chart_type = item.split('_')[0]
                if len(item.split('_')) > 1:
                    para_name = item.split('_')[1]
                    options = self.chart_parameters[chart_type][para_name]['options']
                else:
                    options = self.chart_chk_paras[chart_type]['options']
                
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
        val_list = OptionMenu(self.tree, val, options[0], *options)  # create drop-down list
        val_list.place(x=x, y=y, width=width, height=height, anchor='nw')  # display drop-down on top of cell
        val.set(value)  # put former value in entry
        val_list.bind('<FocusOut>', lambda e: val_list.destroy())              
        val.trace('w', ok) # drop-down list value change event 
        val_list.focus_set()

    def output_values(self):
        output = {}
        for t in self.tree.get_children():
            if self.tree.item(t)['values'][1] == 'Yes':                
                output[t] = []
                for p in self.tree.get_children(t):
                    output[t].append(self.tree.item(p)['values'][0])
        print(output)
        return output
    
    def output_parsed_vals(self):
        output_vals = self.output_values()
        parsed_paras = []
        for r in output_vals:
            para_name = r[0]
            val = str(r[1])
            parser = self.chart_parameters[para_name]['parser']            
            if len(val.split(',')) > 1:
                parsed = self.list_parser(val, parser)
            else:
                if parser:
                    parsed = eval(parser)
                else:
                    parsed = val
            parsed_paras.append(parsed)
        return parsed_paras


    def list_parser(self, in_str, parser):
        output = []
        in_str_list = in_str.split(',')
        for val in in_str_list:
            if parser:
                parsed = eval(parser)
            else:
                parsed = val
            output.append(parsed)
        return output

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        return
    
    def parameter_chg(self, selected_parameters):
        self.clear()
        self.parameters = selected_parameters
        for p in selected_parameters:
            # print(p)            
            self.tree.insert("", "end", values=(p, selected_parameters[p]['value']), tags=selected_parameters[p]['type'])
        return
    
    def fit_height(self):
        height = len(self.parameters)
        self.tree.configure(height=height)
        return
        
if __name__=='__main__':
    
    chart_json = open('chart_default.json', 'r')
    tree_paras = json.load(chart_json)
    chart_json.close()
    # chart_types = chart_paras['chart_types']
    # chart_parameters = chart_paras['chart_parameters']
    # chart_chk_paras = chart_paras['chart_chk_paras']
    
    root = tk.Tk()
    para_tree = ParaTree(root, tree_paras)
    para_tree.pack(expand=1, fill='both')
    test_btn = Button(root, text='Test', command=para_tree.output_values)
    test_btn.pack(side='top')
    root.mainloop()