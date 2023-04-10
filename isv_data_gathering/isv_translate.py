import pandas as pd
from isv_nlp_utils import constants

import ujson
from translation_aux import inflect_carefully, UDFeats2OpenCorpora, infer_pos, iskati2, prepare_slovnik

from rapidfuzz.string_metric import levenshtein
from isv_nlp_utils.normalizacija import transliterate_cyr2lat

import conllu
import requests
import os
import argparse


def download_slovnik():
    dfs = pd.read_excel(
        io='https://docs.google.com/spreadsheets/d/e/2PACX-1vRsEDDBEt3VXESqAgoQLUYHvsA5yMyujzGViXiamY7-yYrcORhrkEl5g6JZPorvJrgMk6sjUlFNT4Km/pub?output=xlsx',
        engine='openpyxl',
        sheet_name=['words']
    )
    dfs['words']['id'] = dfs['words']['id'].fillna(0.0).astype(int)
    dfs['words']['pos'] = dfs['words'].partOfSpeech.astype(str).apply(infer_pos)
    return dfs

def get_slovnik(save=True):
    if os.path.isfile("slovnik.pkl"):
        print("Found 'slovnik.pkl' file, using it")
        dfs = {"words": pd.read_pickle("slovnik.pkl")}
    else:
        print("Downloading dictionary data from Google Sheets...")
        dfs = download_slovnik()
        if save:
            dfs['words'].to_pickle("slovnik.pkl")
        print("Download is completed succesfully.")
    prepare_slovnik(dfs['words'])
    return dfs



def udpipe2df(data):
    parsed = conllu.parse(data)

    result = []
    for i, udpipe_sent in enumerate(parsed):
        df = pd.DataFrame(udpipe_sent)
        df['sent_id'] = i
        df = df.set_index(["sent_id", "id"])
        result.append(df)
    res_df = pd.concat(result)
    if "upos" in res_df.columns:
        res_df = res_df.rename(columns={"upos": "pos"})
    if "upostag" in res_df.columns:
        res_df = res_df.rename(columns={"upostag": "pos"})

    return res_df.drop(columns=["xpos", "deps"], errors="ignore")

def slovnet2df(markup, vocab):
    from natasha.norm import inflect_words, recover_shapes
    def normalize(vocab, tokens):
        words = inflect_words(vocab, tokens)
        words = recover_shapes(words, tokens)
        return words

    result = []
    for i, natasha_sent in enumerate(markup):
        df = pd.DataFrame(natasha_sent.tokens)
        df.columns = ["form", "pos", "feats"]
        df['sent'] = i
        df['lemma'] = list(normalize(vocab, natasha_sent.tokens))
        result.append(df)
    res = pd.concat(result)
    res['head'] = float("nan")
    res['deprel'] = float("nan")
    res['misc'] = float("nan")
    return res

def prepare_parsing(text, model_name):
    if model_name == "ru_slovnet":

        from razdel import sentenize, tokenize
        from slovnet import Morph
        # from slovnet import Syntax
        from navec import Navec
        from natasha import MorphVocab

        navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
        morph = Morph.load('slovnet_morph_news_v1.tar', batch_size=4)
        # syntax = Syntax.load('slovnet_syntax_news_v1.tar')

        # syntax.navec(navec)
        morph.navec(navec)

        chunk = []
        for sent in sentenize(text):
            tokens = [_.text for _ in tokenize(sent.text)]
            chunk.append(tokens)
        markup = morph.map(chunk)
        df = slovnet2df(markup, MorphVocab())
        return df
    else:
        r = requests.post(
            url="http://lindat.mff.cuni.cz/services/udpipe/api/process",
            data={
                "data": text,
                "tagger": "",
                "parser": "",
                "tokenizer": "",
                "model": model_name
            }
        )
        data = ujson.loads(r.text)['result']
        return udpipe2df(data)


def reverse_flavorize(word, pos, feats, src_lang):
    pass
    return word


def special_case(token_row_data, src_lang):
    # if token_row_data.pos == "PROPN":
    #     return reverse_flavorize(token_row_data.form, token_row_data.pos, token_row_data.feats, src_lang)
    if token_row_data.pos == "PUNCT":
        return token_row_data.form

    if token_row_data.pos == "VERB" and token_row_data.form == "нет":
        return "ne jest"  # TODO: ne sut?
    if token_row_data.lemma == "это":
        return "tuto"
    '''
    if token_row_data.lemma == "что" and token_row_data.pos == "SCONJ":
        return "že"
    if token_row_data.lemma == "что" and token_row_data.pos == "PRON":
        return "čto"
    '''
    return None


import re
REFL_REMOVER = re.compile(" sę$")

def translate_sentence(sent, src_lang, slovnik, etm_morph):
    result = []
    inflect_data_array = []
    isv_lemmas_array = []
    types_array = []
    for idx, token_row_data in sent.iterrows():
        subresult = []
        special_translation = special_case(token_row_data, src_lang)
        if special_translation is not None:
            subresult.append(special_translation)
            result.append(subresult)
            inflect_data_array.append([])
            isv_lemmas_array.append([])
            types_array.append("valid")
            continue

        lemma = token_row_data['lemma']

        found, found_type = iskati2(src_lang, lemma, slovnik, pos=token_row_data['pos'])
        rows_found = slovnik.loc[found, :].sort_values(by='type')
        if not found:
            shallow_translated = reverse_flavorize(token_row_data.form, token_row_data.pos, token_row_data.feats, src_lang)
            subresult.append(shallow_translated)
            translation_cands = []
            found_type = "error"
            # TODO: or try to work with lemma instead?
            # shallow_translated = reverse_flavorize(token_row_data.lemma, token_row_data.pos, token_row_data.feats, src_lang)
            # translation_cands = [shallow_translated]
        else:
            translation_cands = rows_found.isv.values

        translation_cands = sum(
            [lemma_entry.split(",") for lemma_entry in translation_cands],
            []
        )
        translation_cands = [
            # remove "sę" and trailing space left after splitting
            REFL_REMOVER.sub("", lemma_with_trailing_space.strip())
            for lemma_with_trailing_space in translation_cands
        ]

        inflect_data = UDFeats2OpenCorpora(token_row_data.feats or dict(), src_lang)
        inflect_data_array.append(inflect_data)
        isv_lemmas_array.append(translation_cands)
        for isv_lemma in translation_cands:
            if token_row_data.feats:
                if token_row_data.pos not in {"ADV", "ADP", "PART"}:
                    inflected = inflect_carefully(etm_morph, isv_lemma, inflect_data)
                else:
                    inflected = [isv_lemma]

                if inflected:
                    subresult += inflected
                else:
                    subresult += [ "[?" + isv_lemma + "?]"]
                    found_type = "error"
            else:
                subresult.append(isv_lemma)

        # remove duplicates
        subresult = list(set(subresult))
        result.append(subresult)
        types_array.append(found_type)
    # print(["/".join(x).replace(", ", "/") for x in result])
    details_df = sent.copy()
    details_df["opencorpora_tags"] = inflect_data_array
    details_df["isv_lemmas"] = isv_lemmas_array
    details_df["translation_candidates"] = result
    details_df["translation_type"] = types_array
    return details_df


def translation_candidates_as_html(translation_details):
    html_result = ""
    # html_result += '<form action="#">'
    html_result += '<p>'
    translation_array = translation_details['translation_candidates']
    for i, cand in enumerate(translation_array):
        if len(cand) == 1:
            html_result += (cand[0] + " ")
        else:
            html_result += (f'<select name="word_{i}_select" id="word_{i}_select">')
            for j, word in enumerate(cand):
                html_result += (f'<option value="word_{i}_{j}">{word}</option>')
            html_result += ('</select> ')
    html_result += ('</p>')
    # html_result += ('<input type="submit" value="Submit" />')
    # html_result += ('</form>')
    return html_result


def select_by_naive_levenshtein(candidates, original_word):
    return min(
                candidates,
                key=lambda x: levenshtein(transliterate_cyr2lat(original_word), x)
    )

def postprocess_translation_details(translation_details):
    result_array = []
    pos = 0
    for idx, token_row_data in translation_details.iterrows():
        original_word = token_row_data.form
        cur_len = len(original_word)
        translation_candidates = token_row_data.translation_candidates
        if original_word.upper() == original_word:
            translation_candidates = [x.upper() for x in translation_candidates]
        elif original_word[0].upper() == original_word[0]:
            translation_candidates = [x[0].upper() + x[1:] for x in translation_candidates]

        if token_row_data.pos == "PUNCT":
            result_array.append({
                "str": translation_candidates[0],
                "type": "space",
            })
        elif token_row_data.pos == "PROPN":
            result_array.append({
                "str": select_by_naive_levenshtein(translation_candidates, original_word),
                "forms": translation_candidates,
                "type": "space",
                "start": pos,
                "end": pos + cur_len,
            })
        else:
            result_array.append({
                "str": select_by_naive_levenshtein(translation_candidates, original_word),
                "forms": translation_candidates,
                "type": token_row_data.translation_type,
                "start": pos,
                "end": pos + cur_len,
            }) 
        pos += cur_len

        if token_row_data.misc:
            space_after = token_row_data.misc.get("SpaceAfter") or token_row_data.misc.get("SpacesAfter")
            if space_after is None:
                space_after = " "
            space_after = space_after.encode('utf8').decode('unicode-escape')
        else:
            space_after = " "
        if space_after != "No":
            result_array.append({
                "str": space_after,
                "type": "space",
            })
            pos += len(space_after)

    return result_array

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('lang', choices=[
       'en',
       'ru', 'be', 'uk', 'pl', 'cs', 'sk', 'bg',
       'mk', 'sr', 'hr', 'sl', 'cu', 'de', 'nl', 'eo',
       'ru_slovnet'
    ])
        # Вообще, между естественными языками и межславянским нет чёткой грани. Можно бы было построить учебник, который бы показывал, как поступательно сделать межславянский из родного языка. И каждый бы мог остановиться где хочет.

        # Вообще, между природными языками и межславянским не есть ясной границы. Можно бы было написать учебник, который бы показывал, как поступательно сделать межславянский из родного языка. И всякий бы мог остановиться где он хочет.

        # Вообче, меджу природными језыками и меджусловјанскым не јест јасной граници. Можно бы было написати учебник, кторы бы показывал, како поступно сдєлати меджусловјанскы из родного језыка. И всякы бы могл обстановити се там, кде он хче. 

    parser.add_argument(
       '--text', type=str, default="Этот текст стоит тут для примера.",
       help='The text that should be translated'
    )

    parser.add_argument(
        '-p', '--path', help="path to DAWG dictionary files (a format that pymorphy2 uses)",
        default="."
    )

    parser.add_argument('--outfile', '-o', nargs='?',
        type=argparse.FileType('w', encoding="utf8"),
        # default=sys.stdout,
        default="test.html",
        help='The output file'
    )

    args = parser.parse_args()

    dfs = get_slovnik()
    slovnik = dfs['words']
    prepare_slovnik(slovnik)

    parsed = prepare_parsing(args.text, args.lang)
    lang = args.lang
    if args.lang == "ru_slovnet":
        lang = "ru"
    etm_morph = constants.create_analyzers_for_every_alphabet(args.path)['etm']
    translation_details = translate_sentence(parsed, lang, dfs["words"], etm_morph)
    if args.format == "html":
        html = translation_candidates_as_html(translation_details)
        if args.debug:
            html += translation_details.to_html()
        args.outfile.write(html)
    if args.format == "json":
        result = {"translation": postprocess_translation_details(translation_details)}
        if args.debug:
            result['details'] = translation_details.to_json()
