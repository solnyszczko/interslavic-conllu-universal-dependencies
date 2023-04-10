"""
semi-local usage (using UDPipe REST API and locally downloaded dictionaries)
"""
from translation_aux import prepare_slovnik
from isv_translate import get_slovnik, download_slovnik

from isv_nlp_utils import constants
from isv_translate import translate_sentence, postprocess_translation_details, prepare_parsing


PATH = r"C:\dev\ISV_data_gathering\\"
sent = "Brusel nám diktuje informovat vás, že zatímco si čtete tento text, šmírujeme váš pohyb na webu. Taky využíváme 69 % výkonu vaší grafické karty k těžbě Bitcoinů a do historie prohlížeče vám ukládáme odkazy na porno."
lang = "cs"

dfs = get_slovnik()
slovnik = dfs['words']
prepare_slovnik(slovnik)
etm_morph = constants.create_analyzers_for_every_alphabet(PATH)['etm']

parsed = prepare_parsing(sent, lang)
udpipe_details = translate_sentence(parsed, lang, slovnik, etm_morph)

print("".join(x['str'] for x in postprocess_translation_details(udpipe_details)))
