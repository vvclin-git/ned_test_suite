import json


'''
{'Parameter 1': {'value':1, 'type':'value', 'options':None},
                  'Parameter 2': {'value':2, 'type':'value', 'options':None},
                  'Parameter 3': {'value':'a', 'type':'list', 'options':('a', 'b', 'c')},
                  'Parameter 4': {'value':'e', 'type':'list', 'options':('e', 'f', 'g')}}
'''

grille_grid_paras = {'Field of View Anchor': {'value':'120,67', 'type':'value', 'options':None},
                   'Field of View Dimension': {'value':'2010x1170', 'type':'value', 'options':None},
                   'Merit Grid Dimension': {'value':'67x39', 'type':'value', 'options':None},
                   }


preset = {'grille_grid_paras':grille_grid_paras}

f = open('grille_default.json', 'w')
json.dump(preset, f)
f.close()

f = open('grille_default.json', 'r')
loaded = json.load(f)
print(loaded)
f.close()