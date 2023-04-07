from .constants import BASE_ISV_TOKEN_REGEX
from .constants import iterate_over_text
import unicodedata

diacr_letters = "žčšěйćżęųœ"
plain_letters = "жчшєjчжеуо"


lat_alphabet = "abcčdeěfghijjklmnoprsštuvyzž"
cyr_alphabet = "абцчдеєфгхийьклмнопрсштувызж"


save_diacrits = str.maketrans(diacr_letters, plain_letters)
cyr2lat_trans = str.maketrans(cyr_alphabet, lat_alphabet)
lat2cyr_trans = str.maketrans(lat_alphabet, cyr_alphabet)


# --- for each orthography variant ---

# for each word we check if it is known.
# if not, we try to apply every conversion
# for every conversion, we calculate if it does (strictly?) improve text
# that is, if each word is known to *this* morph_analyzer
# (then try to autoadd diacritics, if only it helps then +1/2 word)
# then select the best option overall for this message group

def convert2MSPlus(thestring):
    # "e^" -> "ê"
    # 'z\u030C\u030C\u030C' -> 'ž\u030C\u030C'
    thestring = unicodedata.normalize(
        'NFKC',
        thestring
    )
    # TODO: do the same for upper case
    thestring = (
        thestring
        .replace("ň", "ń").replace("ĺ", "ľ")
        .replace("d\u0301", "ď").replace("t\u0301", "ť")
        .replace("l\u0301", "ľ").replace("n\u0301", "ń")
        .replace("ò", "ȯ").replace("è", "ė")
        .replace("đ", "dʒ")
    )
    return thestring


def fix_silmeth(word):
    return word.replace('x', 'h')


def fix_esperanto(word):
    return word.replace('cx', 'č').replace('sx', 'š').replace('zx', 'ž').replace("ex", "ě")


def fix_polish(word):
    return (
        word
        # ASCII-replacements for ISV symbols
        .replace('cz', 'č').replace('sz', 'š').replace('zs', 'ž').replace("ie", "ě")
        # letters that are available on the polish keyboard and could be used together with the replacements
        .replace('ż', 'ž').replace("ć", "č").replace("ę", "e")
    )


def fix_diacritics(word):
    # TODO
    return word


def fix_russian(word):
    return (
        word
        .replace("нь", "њ").replace("ль", "љ")
        .replace("я", "йа").replace("ю", "йу")
        .replace("ь", "j").replace("й", "j").replace("j", "ј").replace("ѣ", "є")
    )


def fix_soft_etm_russian(word):
    return transliterate_cyr2lat(
        word.lower().replace("нь", "ń").replace("ль", "ľ").
        replace("рь", "ŕ").replace("ть", "ť").
        replace("дь", "ď").replace("сь", "ś").replace("зь", "ź").

        replace("ь", "j").replace("й", "j").replace("j", "ј").
        replace("ѣ", "є").replace("ѫ", "ų").replace("ѧ", "ę").replace("ъ", "ȯ").replace("ђ", "đ").replace("ћ", "ć").
        replace("я", "йа").replace("ю", "йу").replace("ё", "йо")
    ).replace("đ", "dʒ")


def transliterate_cyr2lat(text):
    return text.translate(cyr2lat_trans).replace("љ", "lj").replace("њ", "nj").replace("ј", "j")


fix_text = {
        "None": lambda x: x,
        "silmeth": fix_silmeth,
        "esperanto": fix_esperanto,
        "polish": fix_polish,
        # "diacritics": fix_diacritics,
        "russian": fix_russian,
        "soft_etm_russian": fix_soft_etm_russian,
}


def normalize_and_simple_spellcheck(text, abecedas):
    text = convert2MSPlus(text)
    best_orthography = ("?", 0, [])
    fixed_text = ""
    for abeceda, morph in abecedas.items():
        for fixer_name, fixer_func in fix_text.items():
            # TODO: add some sort of sanity check here to skip some
            # options that are irrelevant because of alphabet mismatch:
            # if not set(ALPHABET_LETTERS[abeceda]) & set(text):
            #    continue
            unknown_words = []
            num_tokens = 0
            score = 0
            changed_text = fixer_func(text)
            finalized_text = list(changed_text)
            for delim in iterate_over_text(changed_text, extended=True):
                token = delim.group()
                razbor = morph.parse(token)
                diacr_form = razbor[0].word if razbor else ""
                is_known = 0
                num_tokens += 1
                if morph.word_is_known(token):
                    is_known = 1
                elif "" != diacr_form != token and morph.word_is_known(diacr_form):
                    is_known = 0.5
                else:
                    unknown_words.append(token)
                if "" != diacr_form != token:
                    finalized_text[delim.start():delim.end()] = diacr_form

                score += is_known
            if score > best_orthography[1]:
                best_orthography = (abeceda + "|" + fixer_name, score, list(unknown_words))
                fixed_text = ''.join(finalized_text)

        mean_score = best_orthography[1]/num_tokens
    return best_orthography, fixed_text, mean_score


def dodavaj_bukvy(word, etm_morph):
    corrected = [f.word for f in etm_morph.parse(word)]
    if len(set(corrected)) == 1:
        return corrected[0]
    if len(set(corrected)) == 0:
        return word + "/?"
    return "/".join(set(corrected))


def spellcheck_text(paragraph, std_morph):
    delimiters = BASE_ISV_TOKEN_REGEX.finditer(paragraph)
    proposed_corrections = []
    for delim in delimiters:
        token = delim.group().lower()
        is_word = any(c.isalpha() for c in delim.group())
        is_known = None
        corrected = None
        confident_correction = None

        if is_word:
            is_known = True
            candidates = set([f.word for f in std_morph.parse(token)])
            if candidates != {token} or not std_morph.word_is_known(token):
                is_known = False
            if len(set(candidates)) >= 1:
                corrected = "/".join(set(candidates))

        markup = "" if is_known or not is_word else "^" * len(token)
        if corrected and corrected != token:
            proposed_corrections.append(corrected)
            confident_correction = corrected
            markup = str(len(proposed_corrections))
        span_data = (delim.start(), delim.end(), markup)
        yield span_data, confident_correction


def perform_spellcheck(text, std_morph):
    data = list(spellcheck_text(text, std_morph))
    spans = [entry[0] for entry in data if entry[0][2]]
    proposed_corrections = [entry[1] for entry in data if entry[1]]
    return text, spans, proposed_corrections
