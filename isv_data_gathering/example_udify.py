import os
import shutil
import logging
import argparse
import tarfile
from pathlib import Path

from allennlp.common import Params
from allennlp.common.util import import_submodules
from allennlp.models.archival import archive_model


import sys

sys.path.insert(0, "C:\\dev\\udify\\")
from udify import util

import_submodules("udify")
archive_path = "C:\\dev\\udify\\udify-model.tar.gz"


archive_dir = Path(archive_path).resolve().parent

if not os.path.isfile(archive_dir / "weights.th"):
    with tarfile.open(args.archive) as tar:
        tar.extractall(archive_dir)

config_file = archive_dir / "config.json"

overrides = {}
if device is not None:
    overrides["trainer"] = {"cuda_device": device}
#if args.lazy:
#    overrides["dataset_reader"] = {"lazy": args.lazy}
configs = [Params(overrides), Params.from_file(config_file)]
params = util.merge_configs(configs)

predictor = "udify_text_predictor"

# predictor.output_conllu = True 




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

from allennlp.predictors.predictor import Predictor

archive = load_archive(archive_dir,
                       cuda_device=cuda_device)

from allennlp.models.archival import load_archive

predictor = Predictor.from_archive(archive, predictor)


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