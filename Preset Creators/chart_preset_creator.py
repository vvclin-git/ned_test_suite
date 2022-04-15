import json

reg_file = open('.\\Preset Creators\\regex_def.json')
reg = json.load(reg_file)
reg_file.close()

parser_file = open('.\\Preset Creators\\parser_def.json')
parser = json.load(parser_file)
parser_file.close()

'''
{'Parameter 1': {'value':1, 'type':'value', 'options':None},
                  'Parameter 2': {'value':2, 'type':'value', 'options':None},
                  'Parameter 3': {'value':'a', 'type':'list', 'options':('a', 'b', 'c')},
                  'Parameter 4': {'value':'e', 'type':'list', 'options':('e', 'f', 'g')}}
'''

# dimension = reg['dimension']
# dimension_float = reg['dimension_float']
# coord = reg['coord']
# float = reg['float']
# ufloat = reg['ufloat']
# list = reg['list']
# int = reg['int']
# uint = reg['uint']
# opencv_const = reg['opencv_const']

for k in reg.keys():
    var = k + '_reg'
    exec(var + f"=reg['{k}']")

for k in parser.keys():
    par = k + '_par'
    exec(par + f"=parser['{k}']")    


chart_types = ["Reticle", "Circle Grid", "Checkerboard", "Grille", "Slanted Edge MTF"]

reticle_paras = {"Resolution": {"value": "2560x1440", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
                "Line Color": {"value": "0,255,0", 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
                "Cross Size": {"value": 45, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
                "Marker Size": {"value": 10, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
                "Line Thickness": {"value": 2, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}}

circle_grid = {"Resolution": {"value": "2560x1440", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
                "Grid Dimension": {"value": "32x18", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
                "Marker Size": {"value": 10, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
                "Padding": {"value": "10x10", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}}

checkerboard = {"Resolution": {"value": "2560x1440", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
                "Grid Dimension": {"value": "32x18", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
                "Begin with": {"value": "black", "type": "list", 'regex':str_reg, 'parser':str_par, "options": ["black", "white"]}, 
                "Padding": {"value": "0x0", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}}

grille = {"Resolution": {"value": "2560x1440", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
        "Grille Width": {"value": 4, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
        "Orientation": {"value": "vertical", "type": "list", 'regex':str_reg, 'parser':str_par, "options": ["vertical", "horizontal"]}}

smtf = {"Resolution": {"value": "2560x1440", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
        "Grid Dimension": {"value": "32x18", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
        "Edge Angle": {"value": 5, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
        "Pattern Size": {"value": 80, 'type': 'value', 'regex':int_reg, 'parser':int_par, "options": None}, 
        "Padding": {"value": "10x10", 'type': 'value', 'regex':dim_reg, 'parser':dim_par, "options": None}, 
        "Line Type": {"value": "cv2.LINE_8", "type": "list", 'regex':opencv_const_reg, 'parser':opencv_const_par, "options": ["cv2.LINE_8", "cv2.LINE_4", "cv2.LINE_AA", "cv2.FILLED"]}}

chart_paras = {'Reticle': reticle_paras, 'Circle Grid': circle_grid, 'Checkerboard': checkerboard, 'Grille': grille, 'Slanted Edge MTF': smtf}

chart_chk_paras = {"Reticle": {"value": "Yes", "type": "list", "options": ["Yes", "No"]}, "Circle Grid": {"value": "Yes", "type": "list", "options": ["Yes", "No"]}, "Checkerboard": {"value": "Yes", "type": "list", "options": ["Yes", "No"]}, "Grille": {"value": "Yes", "type": "list", "options": ["Yes", "No"]}, "Slanted Edge MTF": {"value": "Yes", "type": "list", "options": ["Yes", "No"]}}

preset = {'chart_types':chart_types, 'chart_parameters':chart_paras, 'chart_chk_paras': chart_chk_paras}

f = open('.\\Presets\\chart_default.json', 'w')
json.dump(preset, f)
f.close()

f = open('.\\Presets\\chart_default.json', 'r')
loaded = json.load(f)
print(loaded)
f.close()