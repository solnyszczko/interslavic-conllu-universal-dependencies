import pandas as pd
import os


# TODO: https://github.com/gorlatoff/Mashina-bot/blob/main/isv_tools.py

LANGS = {
       'en',
       'ru', 'be', 'uk', 'pl', 'cs', 'sk', 'bg',
       'mk', 'sr', 'hr', 'sl', 'cu', 'de', 'nl', 'eo',
}


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


def download_slovnik():
    dfs = pd.read_excel(
        io='https://docs.google.com/spreadsheets/d/e/2PACX-1vRsEDDBEt3VXESqAgoQLUYHvsA5yMyujzGViXiamY7-yYrcORhrkEl5g6JZPorvJrgMk6sjUlFNT4Km/pub?output=xlsx',
        engine='openpyxl',
        sheet_name=['words', 'suggestions']
    )
    dfs['words']['id'] = dfs['words']['id'].fillna(0.0).astype(int)
    dfs['words']['pos'] = dfs['words'].partOfSpeech.apply(infer_pos)
    dfs['words'].to_pickle("slovnik.pkl")
    return dfs

def get_slovnik():
    if os.path.isfile("slovnik.pkl"):
        print("Found 'slovnik.pkl' file, using it")
        dfs = {"words": pd.read_pickle("slovnik.pkl")}
    else:
        print("Downloading dictionary data from Google Sheets...")
        dfs = download_slovnik()
        dfs['words'].to_pickle("slovnik.pkl")
        print("Download is completed succesfully.")
    prepare_slovnik(dfs['words'])
    return dfs


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



def prepare_slovnik(slovnik):

    transliteration = {}
    transliteration['ru'] = lambda x: x.replace("ё", "е")
    transliteration['uk'] = lambda x: x.replace('ґ', 'г')
    transliteration['be'] = lambda x: x.replace('ґ', 'г')

    for lang in LANGS:
        assert slovnik[slovnik[lang].astype(str).apply(lambda x: "((" in sorted(x))].empty
    import re
    brackets_regex = re.compile(" \(.*\)")
    for lang in LANGS:
        slovnik[lang].str.replace(brackets_regex, "", regex=True)
        if lang in transliteration:
            slovnik[lang] = slovnik[lang].apply(transliteration[lang])
        slovnik[lang + "_set"] = slovnik[lang].str.split(", ").apply(lambda x: set(x))
    slovnik['isv'] = slovnik['isv'].str.replace("!", "").str.replace("#", "").str.lower()

