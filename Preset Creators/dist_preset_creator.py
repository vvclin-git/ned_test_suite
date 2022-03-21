import json


'''
{'Parameter 1': {'value':1, 'type':'value', 'options':None},
                  'Parameter 2': {'value':2, 'type':'value', 'options':None},
                  'Parameter 3': {'value':'a', 'type':'list', 'options':('a', 'b', 'c')},
                  'Parameter 4': {'value':'e', 'type':'list', 'options':('e', 'f', 'g')}}
'''

# dist_grid_paras = {'Test Grid Dimension': {'value':'16x9', 'type':'value', 'options':None},
#                    'Test Chart Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
#                    'Test Chart Padding': {'value':'0x0', 'type':'value', 'options':None},
#                    }

grid_extract_paras = {'Test Chart Resolution': {'value':'2560x1440', 'type':'value', 'options':None},
                      'Test Grid Dimension': {'value':'16x9', 'type':'value', 'options':None},
                      'Test Chart Padding': {'value':'0x0', 'type':'value', 'options':None},
                      'Low Threshold': {'value':25, 'type':'value', 'options':None},
                      'High Threshold': {'value':255, 'type':'value', 'options':None},
                      'Median Kernel Size': {'value':5, 'type':'value', 'options':None},
                     }

grid_sort_paras = {'Path Angle': {'value':30, 'type':'value', 'options':None},
                   'Radius Ratio': {'value':1.5, 'type':'value', 'options':None},                   
                   }

# preset = {'dist_grid_paras':dist_grid_paras, 'grid_extract_paras':grid_extract_paras, 'grid_sort_paras':grid_sort_paras}
preset = {'grid_extract_paras':grid_extract_paras, 'grid_sort_paras':grid_sort_paras}

f = open('dist_default.json', 'w')
json.dump(preset, f)
f.close()

f = open('dist_default.json', 'r')
loaded = json.load(f)
print(loaded)
f.close()