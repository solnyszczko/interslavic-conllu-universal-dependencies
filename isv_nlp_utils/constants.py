import pymorphy2
import re

VERB_PREFIXES = [
    'do', 'iz', 'izpo', 'nad', 'na', 'ne', 'ob', 'odpo', 'od', 'o', 'prědpo',
    'pod', 'po', 'prě', 'pre', 'pri', 'pro', 'råzpro', 'razpro', 'råz', 'raz',
    'sȯ', 's', 'u', 'vȯ', 'vo', 'v', 'vȯz', 'voz', 'vy', 'za',
]

CYR_LETTER_SUBS = {
    "н": "њ", "л": "љ", "е": "є", "и": "ы"
}

SIMPLE_DIACR_SUBS = {
    'e': 'ě', 'c': 'č', 'z': 'ž', 's': 'š',
}

TOTAL_DIACR_SUBS = {
        'a': 'å', 'u': 'ų', 'e': ['ě', 'ę', 'ė'], 'č': 'ć', 'c': ['č', 'ć'],
        'o': 'ȯ',
        'n': 'ń', 'r': 'ŕ', 'l': 'ľ',
        'd': 'ď', 's': ['ś', 'š'], 't': 'ť', 'z': ['ź', 'ž'],
        # hack with dʒ = "đ"
        'ž': 'ʒ'  # đ ne funguje
}

ETM_DIACR_SUBS = {
        'a': 'å', 'u': 'ų', 'e': ['ě', 'ę', 'ė'], 'č': 'ć',
        'o': 'ȯ', 
        'n': 'ń', 'r': 'ŕ', 'l': 'ľ',
        'd': 'ď', 's': 'ś', 't': 'ť', 'z': 'ź',
        # hack with dʒ = "đ"
        'ž': 'ʒ'  # đ ne funguje
}


ALPHABET_LETTERS = {
    'lat': "abcdefghijklmnoprstuvyzěčšž",
    'cyr': "абвгдежзиклмнопрстуфхцчшыєјљњ",
    'etm': "abcdefghijklmnoprstuvyzåćčďėęěľńŕśšťųźžȯʒ",
}

ADDITIONAL_ETM_LETTERS = "åćďėęľńŕśťųźȯʒ"
DOWNGRADED_ETM_LETTERS = "ačdeelnrstuzož"

downgrade_diacritics = str.maketrans(ADDITIONAL_ETM_LETTERS, DOWNGRADED_ETM_LETTERS)


letters = "a-zа-яёěčžšåųćęđŕľńĺťďśźʒėȯђјљєњ"
alphanum = f"[0-9{letters}_]"

BASE_ISV_TOKEN_REGEX = re.compile(
    f'''(?:-|[^{letters}\\s"'""«»„“-]+|{alphanum}+(-?{alphanum}+)*)''',
    re.IGNORECASE | re.UNICODE
)

DISCORD_USERNAME_REGEX = re.compile(
    r'''@((.+?)#\d{4})''',
    re.IGNORECASE | re.UNICODE
)


# from collections import namedtuple
# _dummy = namedtuple('mock', 'dictionary')
# pymorphy2.units.DictionaryAnalyzer(_dummy(None))

DEFAULT_UNITS = [
    [
        pymorphy2.units.DictionaryAnalyzer()
    ],
    pymorphy2.units.KnownPrefixAnalyzer(known_prefixes=VERB_PREFIXES),
    [
        pymorphy2.units.UnknownPrefixAnalyzer(),
        pymorphy2.units.KnownSuffixAnalyzer()
    ]
]


def iterate_over_text(paragraph, extended=False):
    delimiters = BASE_ISV_TOKEN_REGEX.finditer(paragraph)
    for delim in delimiters:
        if any(c.isalpha() for c in delim.group()):
            token = delim.group()
            if extended:
                yield delim
            else:
                yield token


def create_analyzers_for_every_alphabet(path="C:\\dev\\pymorphy2-dicts\\"):

    std_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_lat",
        units=DEFAULT_UNITS,
        char_substitutes=SIMPLE_DIACR_SUBS
    )

    etm_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_etm",
        units=DEFAULT_UNITS,
        char_substitutes=ETM_DIACR_SUBS
    )

    cyr_morph = pymorphy2.MorphAnalyzer(
        path+"out_isv_cyr",
        units=DEFAULT_UNITS,
        char_substitutes=CYR_LETTER_SUBS
    )
    abecedas = {"lat": std_morph, "etm": etm_morph, "cyr": cyr_morph}
    return abecedas


def create_etm_analyzer(path="C:\\dev\\pymorphy2-dicts\\"):
    return pymorphy2.MorphAnalyzer(
        path+"out_isv_etm",
        units=DEFAULT_UNITS,
        char_substitutes=ETM_DIACR_SUBS
    )


def inflect_carefully(morph, parsing, inflect_data, verbose=0):
    if verbose > 1:
        print(parsing, inflect_data)

    lexeme = parsing.lexeme
    is_negative = False

    forbidden_tags = {tag[1:] for tag in inflect_data if tag[0] == "~"}
    inflect_data = {tag for tag in inflect_data if tag[0] != "~"}
    if "neg" in inflect_data:
        is_negative = True
        inflect_data = {tag for tag in inflect_data if tag != "neg"}

    candidates = {
            form[1]: form.tag.grammemes & inflect_data for form in lexeme
            if not(form.tag.grammemes & forbidden_tags)
    }
    # rank each form according to the size of intersection
    best_fit = sorted(candidates.items(), key=lambda x: len(x[1]))[-1]
    best_candidates = {k: v for k, v in candidates.items() if len(v) == len(best_fit[1])}
    if len(best_fit[1]) == 0 and len(inflect_data) > 0:
        if verbose:
            print("have trouble in finding anything like ", inflect_data, " for ", isv_lemma)
        return []
    if len(best_fit[1]) != len(inflect_data) and verbose > 1:
        print("have trouble in finding ", inflect_data, " for ", isv_lemma)
        print("best_fit: ", best_fit)
        print("candidates: ", {k: v for k, v in candidates.items() if len(v) == len(best_fit[1])})
        print([parsing.inflect(cand.grammemes) for cand in best_candidates])

    result = [parsing.inflect(cand.grammemes) for cand in best_candidates]
    result = [x.word for x in result]
    if is_negative:
        result = ["ne " + x for x in result]
    return result
