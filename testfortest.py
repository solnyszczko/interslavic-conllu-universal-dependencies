import conllu
from conllu.parser import parse_dict_value
from io import open
import os
import sys
import string
import json
import jellyfish
from isv_nlp_utils import constants
import udapi

PATH = os.path.dirname(sys.argv[0])

morph = constants.create_etm_analyzer(PATH)

parses = morph.parse("on")
print(parses)
#print(parses[1])
#print(parses[2])

print( constants.inflect_carefully(morph, parses[0], {"NPRO", "datv"}))



parses = morph.parse("pozvaljati")
try:print(parses[0][1])
except:print(parses[1][1])
try:print(parses[2])
except:print(parses[3])

