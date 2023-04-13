import sys
import os
PATH = os.path.dirname(sys.argv[0])
sys.path.append("/home/meow/mytest/isv_data_gathering/")
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
#print(slovnik)
etm_morph = constants.create_etm_analyzer(PATH)

sent = "Północna Algieria leży w strefie umiarkowanej i cieszy się łagodnym, śródziemnomorskim klimatem."
lang = "pl"

parsed = it.prepare_parsing(sent, lang)
print(parsed)
udpipe_details = it.translate_sentence(parsed, lang, slovnik, etm_morph)

print(udpipe_details.translation_candidates.values.tolist())
