import sys
import os
PATH = os.path.dirname(sys.argv[0])
print(PATH)
mypath=os.path.join(PATH,"isv_data_gathering\\")
print(mypath)
sys.path.append("/home/meow/dev/isv_data_gathering/")
#"home/meow/dev/isv_data_gathering/"
#FIX THIS WEIRD PATH STUFF
import conllu
from conllu.parser import parse_dict_value
from io import open


import string
import json
import jellyfish
from isv_nlp_utils import constants
from isv_data_gathering import translation_aux
from isv_data_gathering import isv_translate as it



punctuation_chars = list(string.punctuation)
punctuation_chars.extend(['‘', '’', '“', '”', '…', '–', '—', '„'])

morph = constants.create_etm_analyzer(PATH)

#postprocess_translation_detailss



from isv_nlp_utils import constants
from isv_nlp_utils.slovnik import get_slovnik, prepare_slovnik

dfs = get_slovnik()
slovnik = dfs['words']
prepare_slovnik(slovnik)
etm_morph = constants.create_etm_analyzer(PATH)

sent = "lubię brati ryby z beczki."
lang = "pl"

parsed = it.prepare_parsing(sent, lang)
udpipe_details = it.translate_sentence(parsed, lang, slovnik, etm_morph)

print(udpipe_details.translation_candidates.values.tolist())