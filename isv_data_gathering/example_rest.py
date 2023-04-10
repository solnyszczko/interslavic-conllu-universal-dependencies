# as server

import json, requests
URL = "https://d5dek8rqp8b9isnc331l.apigw.yandexcloud.net/api/"


TEXT = "Pójdźże, kiń tę chmurność w głąb flaszy!"
LANG = "pl"


def decode_translation(r, only_first=True):
    answer = json.loads(r.text)
    if only_first:
        return "".join([entry['str'] for entry in answer['translation']])
    else:
        return [entry.get("forms", [entry['str']]) for entry in answer['translation']]

r = requests.post(URL, data=json.dumps({"lang": LANG, "text": TEXT}).encode("utf8"), headers = {"Content-Type": "application/json"})
print(decode_translation(r))


# locally


            parsed = prepare_parsing(sent, lang)
            udpipe_details = translate_sentence(parsed, lang, slovnik, etm_morph)

from conllu.parser import parse_dict_value
from translation_aux import prepare_slovnik
from isv_translate import get_slovnik, download_slovnik

from isv_nlp_utils import constants
from isv_translate import translate_sentence, postprocess_translation_details, prepare_parsing

PATH = r"C:\dev\ISV_data_gathering\\"

dfs = get_slovnik()
slovnik = dfs['words']
prepare_slovnik(slovnik)
etm_morph = constants.create_analyzers_for_every_alphabet(PATH)['etm']



# with udify
def parse_with_udify(predictor, src_lang, text):
    parsed = predictor.predict_json({"sentence": text})
    df = pd.DataFrame()

    cols1 = ['words', 'upos', 'feats', 'lemmas', 'predicted_heads', 'predicted_dependencies']
    cols2 = ["form", "pos", "feats", "lemma", "head", "deprel"]

    for col_src, col_dst in zip(cols1, cols2):
        df[col_dst] = parsed[col_src]

    df['misc'] = ""
    df['feats'] = df['feats'].apply(parse_dict_value)
    df['misc'] = df['misc'].apply(parse_dict_value)
    return df

def translate_with_udify(predictor, slovnik, etm_morph, src_lang, text):
    df = parse_with_udify(predictor, src_lang, text)
    translation_details = translate_sentence(df, src_lang, slovnik, etm_morph)
    return translation_details


        details = translate_with_udify(predictor, slovnik, etm_morph, lang, sent)
        print("".join(x['str'] for x in postprocess_translation_details(details)))
