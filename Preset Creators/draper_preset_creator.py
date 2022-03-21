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

pupil_mesh_paras = {'Blur Kernel Size': {'value':9, 'type':'value', 'options':None},
                    'Threshold Value': {'value':0, 'type':'value', 'options':None},
                    'Max Threshold Value': {'value':65535, 'type':'value', 'options':None},
                    'Contour Approx Epsilon': {'value':0.0015, 'type':'value', 'options':None},
                    }

far_mesh_paras = {'Blur Kernel Size': {'value':9, 'type':'value', 'options':None},
                  'Threshold Value': {'value':0.5, 'type':'value', 'options':None},
                  'Max Threshold Value': {'value':1, 'type':'value', 'options':None},
                  'Contour Approx Epsilon': {'value':0.001, 'type':'value', 'options':None},
                 }

draper_paras = {'Sensor Resolution': {'value':'2250x1305', 'type':'value', 'options':None},
                'Sensor Size': {'value':'7.46x4.14', 'type':'value', 'options':None},
                'Camera Eff': {'value':8, 'type':'value', 'options':None},
                'Far Mesh Distance': {'value':200, 'type':'value', 'options':None},
               }

eyebox_view_paras = {'Project Plane Grid': {'value':'-10,10,21', 'type':'value', 'options':None},
                     '3D View Angle': {'value':'35,135', 'type':'value', 'options':None},
                     'Aperture Depth': {'value':'2,10,5', 'type':'value', 'options':None}              
                    }

# preset = {'dist_grid_paras':dist_grid_paras, 'grid_extract_paras':grid_extract_paras, 'grid_sort_paras':grid_sort_paras}
preset = {'pupil_mesh_paras':pupil_mesh_paras, 'far_mesh_paras':far_mesh_paras, 'draper_paras':draper_paras, 'eyebox_view_paras':eyebox_view_paras}

f = open('draper_default.json', 'w')
json.dump(preset, f)
f.close()

f = open('draper_default.json', 'r')
loaded = json.load(f)
print(loaded)
f.close()