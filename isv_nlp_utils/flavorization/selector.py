from random import choice
import lingua  # lingua-language-detector
from hunspell import Hunspell  # cypyhunspell
from .tokenizer import tokens_to_string, all_token_text_variants
from copy import deepcopy

SLAVIC_LANGS = [
    'bel', 'ukr', 'rue', 'rus', 'bos', 'hrv', 'srp', 'cnr', 'slv', 'bul', 'mkd', 'chu', 'wen', 'dsb', 'hsb', 'pol', 'szl', 'csb', 'pox', 'ces', 'czk', 'slk',
]

LANGS_DICT = {
    l.upper(): getattr(lingua.isocode.IsoCode639_3, l.upper())
    for l in SLAVIC_LANGS
    if l.upper() in dir(lingua.isocode.IsoCode639_3)
}


def init_detector():
    detector = lingua.LanguageDetectorBuilder.from_iso_codes_639_3(*LANGS_DICT.values()).build()
    return detector


def init_hunspell(lang, hunspell_data_dir=r'C:/dev/hunspell_dicts'):
    h = Hunspell(lang, hunspell_data_dir=hunspell_data_dir)
    return h


def get_conf(confs, lang):
    if lang not in confs:
        return 0
    the_sum = sum(dict(confs).values())
    return {k: v / the_sum for (k, v) in confs}[lang]


def filter_good_spellings(tokens, h):
    tokens = deepcopy(tokens)
    for token in tokens:
        w = all_token_text_variants(token)
        if len(w) > 1:
            # print(w)
            known_words = [cand for cand in w if h.spell(cand)]
            # print(known_words)
            if len(known_words) != 0:
                for variant in token.variants:
                    variant.text_variants = [v for v in variant.text_variants if v in known_words]
                token.variants = [v for v in token.variants if len(v.text_variants)]
                # for cand in w:
                #    print(f'    {h.suggest(cand)}')
    return tokens


def filter_lingua(tokens, detector, lang):
    LANG_OBJ = LANGS_DICT[lang.upper()]
    tokens = deepcopy(tokens)
    for token in tokens:
        w = all_token_text_variants(token)
        if len(w) > 1:
            scores = {}
            for cand in w:
                if cand:
                    confs = detector.compute_language_confidence_values(cand)
                    scores[cand] = get_conf(confs, LANG_OBJ)
            # TODO: internals changed, update this
            best_word = [max(scores, key=lambda x: scores[x])]
            for variant in token.variants:
                variant.text_variants = [v for v in variant.text_variants if v == best_word]
            token.variants = [v for v in token.variants if len(v.text_variants)]
    return tokens

def produce_string(tokens, hunspell_lang, iso_lang):
    h = init_hunspell(hunspell_lang)
    detector = init_detector()
    tokens = filter_good_spellings(tokens, h)
    tokens = filter_lingua(tokens, detector, iso_lang)
    return tokens_to_string(tokens)

