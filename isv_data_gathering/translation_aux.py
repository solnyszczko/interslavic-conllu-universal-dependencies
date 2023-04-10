from collections import defaultdict

LANGS = {
       'en',
       'ru', 'be', 'uk', 'pl', 'cs', 'sk', 'bg',
       'mk', 'sr', 'hr', 'sl', 'cu', 'de', 'nl', 'eo',
}

def UDPos2OpenCorpora(pos):
    if pos == "aux":
        return ["verb", "part"]
    if pos == "adj":
        return ["verb", "adjf"] #for participles treated as adjectives
    if pos == "det":
        return ["npro", "adjf","adv"] #added 'adv' for vęće-> wiecej
    if pos == "adp":
        return ["prep"]
    if pos == "cconj":
        return ["conj"]
    if pos == "sconj":
        return ["conj", "adv"]
    if pos == "part":
        return ["part", "interjection", "conj", "adv"]
    if pos == "propn":
        return ["noun"]
    if pos == "pron":
        return ["npro"]
    return [pos]

def UDFeats2OpenCorpora(feats, src_lang):
    result = []
    for key, value in feats.items():
        if key == "Animacy":
            if value =="Hum": value = "anim"
            if value =="Inan": value = "inan"
            if value =="Nhum": pass #value = "inan" idk yet this one is pretty random
            result.append(value)
           
        if key == 'Case':
            CASES_MAP = {
                "Nom": 'nomn',
                "Gen": 'gent',
                "Dat": 'datv',
                "Acc": 'accs',
                "Ins": 'ablt',
                "Loc": 'loct',
                "Voc": 'voct',
                "Acc,Nom": 'accs',  # TODO: handle this case better (sometimes happens with Bulgarian)
            }
            result.append(CASES_MAP[value])
        if key == 'Gender':
            if value.lower() == "fem": 
                value = "femn"
            result.append(value.lower())
        if key == 'Number':
            if value.lower() =='ptan': value="Pltm"; result.append(value)
            elif value.lower() == 'coll': value = "Sgtm"; result.append(value)
            else: result.append(value.lower())
        if key == 'Tense':
            if value.lower() == 'fut': value ='futr'
            result.append(value.lower())
        if key == 'Person':
            if value.lower() =='0': result.append("pssv")#FIXW
            result.append(value.lower() + 'per')
        if key == 'Aspect':
            if value.lower() == "imp": 
                value = "impf"
            result.append(value.lower())
        if key == 'Degree':
            if value.lower() == "pos": 
                value = ""
            if value.lower() == "cmp": 
                value = "comp"
            if value.lower() == "sup": 
                value = "supr"
            result.append(value.lower())
        if key == 'VerbForm':
            if value.lower() == "fin": 
                result += ["~actv", "~pssv"]
            if value.lower() == "inf": 
                result += ["infn"]
            if value.lower() == "part": 
                result += ["V-ju"]#helps distinguish participle from normal past tense verbs
            pass  # https://universaldependencies.org/ru/feat/VerbForm.html
        if key == 'Voice':
            if value.lower() == "act" and feats["VerbForm"] == "Part": 
                if src_lang != "cs":
                    result.append("actv")
            if value.lower() == "pass": 
                result.append("pssv")
        # {'Mood': 'Ind', 'Tense': 'Past', 'VerbForm': 'Fin'}
        if key == 'Polarity' and value == 'Neg':
            result.append("neg")
    if False and len(result) < len(feats):
        print(f"Info loss? {feats} -> {result}")
    return set([x for x in result if x])


def infer_pos(details_string):
    arr = [
        x for x in details_string
        .replace("./", '/')
        .replace(" ", '')
        .split('.')
        if x != ''
    ]

    if 'adj' in arr:
        return 'adj'
    if set(arr) & {'f', 'n', 'm', 'm/f'}:
        return 'noun'
    if 'adv' in arr:
        return 'adv'
    if 'conj' in arr:
        return 'conj'
    if 'prep' in arr:
        return 'prep'
    if 'pron' in arr:
        return 'pron'
    if 'num' in arr:
        return 'num'
    if 'intj' in arr:
        return 'interjection'
    if 'v' in arr:
        return 'verb'

ryba = lambda x: x

transliteration = defaultdict(lambda: ryba)
transliteration['ru'] = lambda x: x.replace("ё", "е")
transliteration['uk'] = lambda x: x.replace('ґ', 'г')
transliteration['be'] = lambda x: x.replace('ґ', 'г')


def prepare_slovnik(slovnik):
    for lang in LANGS:
         assert slovnik[slovnik[lang].astype(str).apply(lambda x: "((" in sorted(x))].empty
    import re
    brackets_regex = re.compile(" \(.*\)")
    for lang in LANGS:
        slovnik[lang] = slovnik[lang].str.replace(brackets_regex, "").astype(str)
        slovnik[lang] = slovnik[lang].apply(transliteration[lang])
        slovnik[lang + "_set"] = slovnik[lang].str.split(", ").apply(lambda x: set(x))
    slovnik['isv'] = slovnik['isv'].str.replace("!", "").str.replace("#", "").str.lower()
    slovnik['type'] = slovnik['type'].astype(str)


def iskati2(jezyk, slovo, sheet, pos=None):
    if pos is not None:
        pos = UDPos2OpenCorpora(pos.lower())
    najdene_slova = []
    slovo = transliteration[jezyk](slovo)

    candidates = sheet[sheet[jezyk + "_set"].apply(lambda x: slovo in x)]
    if pos is not None:
        for i, stroka in candidates.iterrows():
            if stroka["pos"] in pos:
                najdene_slova.append(i)
    else:
        najdene_slova = candidates.index.tolist()
    if najdene_slova:
        return najdene_slova, 'valid'
    else:
        return candidates.index.tolist(), 'maybe'


def inflect_carefully(morph, isv_lemma, inflect_data, pos=[] ,verbose=False):
    if verbose:
        print(isv_lemma, inflect_data)
    parses = morph.parse(isv_lemma)#parsed gets set twice?
    parsed = None
    if not parses:
        # some sort of error happened
        if verbose:
            print("ERROR:", isv_lemma, inflect_data)
        return []
    if pos!=[]: #added optional POS option, for me helped fix conjugation of the word "brati"
        for parse in parses:
            if parse[1].POS.lower() in pos: parsed = parse
    if parsed == None: parsed = morph.parse(isv_lemma)[0]
    lexeme = parsed.lexeme
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
    if len(best_fit[1]) != len(inflect_data):
        if verbose:
            print("have trouble in finding ", inflect_data, " for ", isv_lemma)
            print("best_fit: ", best_fit)
            print("candidates: ", {k: v for k, v in candidates.items() if len(v) == len(best_fit[1])})
            print([parsed.inflect(cand.grammemes) for cand in best_candidates])

    result = [parsed.inflect(cand.grammemes) for cand in best_candidates]
    result = [x.word for x in result]
    if is_negative:
        result = ["ne " + x for x in result]
    return result


