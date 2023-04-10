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

parses = morph.parse("pozvaljavša")
print(parses)
#print(parses[1])
#print(parses[2])
#Aspect=Imp|Case=Nom|Gender=Fem|Number=Sing|Polarity=Pos|VerbForm=Part|Voice=Act	
print(translation_aux.inflect_carefully(morph, "pozvaljati", {'accs', 'sing', 'actv', 'impf', 'femn', 'V-ju'}))


