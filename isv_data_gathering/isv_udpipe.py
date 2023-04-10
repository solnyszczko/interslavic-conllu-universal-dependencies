# THIS IS A HORRIBLE PROTOTYPE
# DO NOT TOUCH

from pandas import read_excel
from isv_nlp_utils import constants


transliteration = {
    "ru": lambda x: x.replace("ё", "е")
}

dfs = read_excel(
    io='https://docs.google.com/spreadsheets/d/e/2PACX-1vRsEDDBEt3VXESqAgoQLUYHvsA5yMyujzGViXiamY7-yYrcORhrkEl5g6JZPorvJrgMk6sjUlFNT4Km/pub?output=xlsx',
    engine='openpyxl',
    sheet_name=['words', 'suggestions']
)

dfs['words']['id'] = dfs['words']['id'].fillna(0.0).astype(int)

print(dfs['words'].head(2).T)

def UDFeats2OpenCorpora(feats):
    result = []
    for key, value in feats.items():
        if key == "Animacy":
            # fukken TODO
            pass
        if key == 'Case':
            CASES_MAP = {
                "Nom": 'nomn',
                "Gen": 'gent',
                "Dat": 'datv',
                "Acc": 'accs',
                "Ins": 'ablt',
                "Loc": 'loct',
                "Voc": 'voct',
            }
            result.append(CASES_MAP[value])
        if key == 'Gender':
            if value.lower() == "fem": 
                value = "femn"
            result.append(value.lower())
        if key == 'Number':
            result.append(value.lower())
        if key == 'Tense':
            result.append(value.lower())
        if key == 'Person':
            result.append(value.lower() + 'per')
        # {'Aspect': 'Imp', 'Mood': 'Ind', 'Tense': 'Past', 'VerbForm': 'Fin', 'Voice': 'Act'}
    return set(result)


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


dfs['words']['pos'] = dfs['words'].partOfSpeech.apply(infer_pos)

def iskati(jezyk, slovo, sheet):
    najdene_slova = []
    for i in range(1, len(sheet['isv'])):
        cell = str( sheet[jezyk][i] )
        cell = str.replace( cell, '!', '')
        cell = str.replace( cell, '#', '')
        cell = cell.lower()
        cell = transliteration[jezyk](cell)
        if slovo in str.split( cell, ', ' ):
            najdene_slova.append(i)
    return najdene_slova

def iskati2(jezyk, slovo, sheet, pos=None):
    if pos is not None:
        pos = pos.lower()
    najdene_slova = []
    # could be done on loading
    sheet['isv'] = sheet['isv'].str.replace("!", "").str.replace("#", "").str.lower()
    sheet[jezyk] = sheet[jezyk].apply(transliteration[jezyk])

    # lang-specific logic

    for i, stroka in sheet.iterrows():
        cell = stroka[jezyk]

        if slovo in stroka[jezyk].split(", "):
            if pos is not None:
                if pos == stroka["pos"]:
                    najdene_slova.append(i)
                else:
                    print("~~~~", stroka['isv'], pos, ' != ', stroka['pos'])
            else:
                najdene_slova.append(i)
    # najdene_slova = reversed(sorted(najdene_slova, key=lambda x: x['type']))
    # return [x['isv'] for x in najdene_slova]
    return najdene_slova


found = iskati2("ru", 'знать', dfs['words'], 'noun')
print(found)
print(dfs['words'].loc[found, ['isv', 'ru']])

found = iskati2("ru", 'знать', dfs['words'], 'verb')
print(found)
print(dfs['words'].loc[found, ['isv', 'ru']])

found = iskati2("ru", 'на', dfs['words'])
print(found)
print(dfs['words'].loc[found, ['isv', 'ru', 'type', 'partOfSpeech']])
'''
found = iskati2("ru", 'понимать', dfs['words'])
print(found)
print(dfs['words'].loc[found, ['isv', 'ru']])

found = iskati2("ru", 'большой', dfs['words'])
print(found)
print(dfs['words'].loc[found, ['isv', 'ru']])
'''

import conllu

with open(r"C:\Users\bt\Downloads\processed.conllu", "r", encoding="utf8") as f:
    data = f.read()


def inflect_carefully(morph, isv_lemma, inflect_data):
    parsed = morph.parse(isv_lemma)[0]
    inflected = parsed.inflect(inflect_data)
    if inflected:
        return inflected
    print("have trouble in finding ", inflect_data)
    lexeme = parsed.lexeme
    candidates = {form[1]: form.tag.grammemes & inflect_data for form in lexeme}
    # rank each form according to the size of intersection
    best_fit = sorted(candidates.items(), key=lambda x: len(x[1]))[-1]
    print("best_fit: ", best_fit)
    print("candidates: ", {k: v for k, v in candidates.items() if len(v) == len(best_fit[1])})
    if best_fit[1] == 0:
        return None
    return parsed.inflect(best_fit[0].grammemes)

morph = constants.create_analyzers_for_every_alphabet()['etm']


result = []

parsed = conllu.parse(data)
for sent in parsed[1:]:
    for token in sent:
        if token['upos'] in {"PROPN", "PUNCT"}:
            print("####", token)
            result.append(token['form'])
            continue
        lemma = token['lemma']
        found = iskati2("ru", lemma, dfs['words'])
        rows_found = dfs['words'].loc[found, :].sort_values(by='type')
        if not found:
            print("####????", token, lemma, token['upos'])
            result.append("<?" + token['form'] + "?>")
            continue
        else:
            understandable_best_translation = rows_found.head(1).isv.values[0]

        if token['feats']:
            # print(token['deprel'], token['upos'])
            print("-----")
            # print(token, lemma, token['upos'], token['deprel'])
            # print(dfs['words'].loc[found, ['isv', 'partOfSpeech', 'type']])

            # TODO: select one; split multi-entries
            isv_lemma = understandable_best_translation
            print(isv_lemma)
            print(token['feats'])
            inflect_data = UDFeats2OpenCorpora(token['feats'])
            print(inflect_data)
            inflected = inflect_carefully(morph, isv_lemma, inflect_data)
            if not inflected:
                print("####", token, isv_lemma, inflect_data, token['feats'])
                result.append("<?" + isv_lemma + "?>")
                continue
            print("####", inflected.word)
            result.append(inflected.word)
            print("-----")
        else:
            print("####", understandable_best_translation)
            result.append(understandable_best_translation)
    break
print(" ".join(result))
