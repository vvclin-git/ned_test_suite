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

se_paras =  {             
            "Edge Angle": {"value": 5, "type": "value", 'regex':int_reg, 'parser':int_par, "options": None}, 
            "Pattern Size": {"value": 80, "type": "value", 'regex':uint_reg, 'parser':uint_par,"options": None},            
            "Line Type": {"value": "cv2.LINE_8", "type": "list", 'regex':opencv_const_reg, 'parser':opencv_const_par, "options": ['cv2.LINE_4', 'cv2.LINE_8', 'cv2.LINE_AA']},
            "Reverse": {"value": "True", "type": "list", "regex": bool_reg, "parser": bool_par, "options": ["True", "False"]},
            "Extract Method": {"value": 'cv2.TM_CCOEFF_NORMED', "type": "list", 'regex':opencv_const_reg, 'parser':opencv_const_par, "options": ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']},
            "Threshold": {"value": 0.95, "type": "value", 'regex':ufloat_reg, 'parser':ufloat_par, "options": None},
            "IoU Threshold": {"value": 0.01, "type": "value", 'regex':ufloat_reg, 'parser':ufloat_par, "options": None}
            }

mtf_paras = {
            'Sensor Pixel Size (µm)': {'value':'1.85', 'type':'value', 'regex':ufloat_reg, 'parser':ufloat_par,  'options':None},
            'Threshold': {'value':'0.55', 'type':'value', 'regex':ufloat_reg, 'parser':ufloat_par, 'options':None},
            'MTF Contrast (10-90)': {'value':'30', 'type':'value', 'regex':uint_reg, 'parser':uint_par, 'options':None},
            }


output_paras = {
                'Grid Dimension': {'value':'32x18', 'type':'value', 'regex':dim_reg, 'parser':dim_par,  'options':None},
                'Mesh Resolution': {'value':'64x36', 'type':'value', 'regex':dim_reg, 'parser':dim_par,  'options':None},
                'Interpolation': {'value':'linear', 'type':'list', 'regex':str_reg, 'parser':str_par, 'options':['linear', 'nearest', 'cubic']}                
                }

preset = {'se_paras':se_paras, 'mtf_paras':mtf_paras, 'output_paras': output_paras}

f = open('.\\Presets\\smtf_default.json', 'w')
json.dump(preset, f)
f.close()

f = open('.\\Presets\\smtf_default.json', 'r')
loaded = json.load(f)
print(loaded)
f.close()