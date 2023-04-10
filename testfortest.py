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
from isv_data_gathering import translation_aux

PATH = os.path.dirname(sys.argv[0])

morph = constants.create_etm_analyzer(PATH)
print("a" in "také, stejně, rovněž, taky, taktéž".split(", "))
parses = morph.parse("posvętiti")
for parse in parses:
  print(parse)

#print(parses[1])
#print(parses[2])
#Aspect=Imp|Case=Nom|Gender=Fem|Number=Sing|Polarity=Pos|VerbForm=Part|Voice=Act	
print(translation_aux.inflect_carefully(morph, "posvętiti", {'perf', 'pssv', 'past','neut'},pos="verb"))

#umiarkowanej 
#uměrjeny
#poświęcono
#posvętiti {'perf', 'pssv', 'past', '~pssv', '~actv', 'actv', '0per'}
#w 2007 r., loc
#z iz ze
#się	sę	PRON


