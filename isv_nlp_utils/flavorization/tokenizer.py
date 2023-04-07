import pandas as pd
from razdel import tokenize
import re
import unicodedata
from string import punctuation

from natasha.record import Record

#class AnnotatedToken(Record):
#    __attributes__ = ['text', 'capitalization', 'space_after', 'features', 'POS', 'slovnik_pos', 'lemma', 'isv_id', 'genesis', 'is_processed']

class AnnotatedToken(Record):
    __attributes__ = ['variants', 'capitalization', 'space_after']


class ParseVariant(Record):
    __attributes__ = ['text_variants', 'features', 'slovnik_pos', 'lemma', 'isv_id', 'genesis', 'was_force_processed']
'''

class TokenVariant(Record):
    __attributes__ = ['text', 'parse_data', 'space_after', 'features', 'POS', 'slovnik_pos', 'lemma', 'isv_id', 'genesis', 'is_processed']
'''

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
        .replace("ǉ", "lj").replace("ĳ", "ij").replace("ǌ", "nj").replace("t́", "ť").replace("d́", "ď")
    )
    return thestring


def extract_stem_prefix_suffix(word, word_parse, isv_dict):

    paradigm_num = word_parse[4][0][2]
    form_num = word_parse[4][0][3]
    paradigm = isv_dict.build_paradigm_info(paradigm_num)
    stem = isv_dict.build_stem(isv_dict.paradigms[paradigm_num], form_num, word)

    pref = paradigm[form_num][0]
    suff = paradigm[form_num][2]
    return pref, stem, suff


def compute_annotated_tokens(src, morph, slovnik, fix_diacritics=True):
    isv_dict = morph._units[0][0].dict

    src = convert2MSPlus(src)
    tokens = list(tokenize(src))

    tokens_data = []

    for i, t in enumerate(tokens):
        if i + 1 < len(tokens):
            space_after = src[t.stop: tokens[i+1].start]
        else:
            space_after = ""
        cap = "title" if t.text.istitle() else "upper" if t.text.isupper() else False
        orig_word = t.text.replace("đ", "dʒ")
        parses = morph.parse(orig_word)
        if parses:
            # word, paradigm_id, parse_data
            unique_forms = [(f.word, f[4][0][2], f) for f in parses]
            if not fix_diacritics and morph.word_is_known(orig_word):
                unique_forms = [
                    (f_word, f_para_num, parse_data)
                    for (f_word, f_para_num, parse_data) in unique_forms
                    if f_word.lower() == orig_word.lower()
                ]
            unique_forms = [(f_word.replace("dʒ", "đ"), f_para_num, parse_data) for (f_word, f_para_num, parse_data) in unique_forms]

            variants = []

            known = set()
            for form in unique_forms:
                # consider only unique pairs of stem/lemmas and paradigm_id
                if form[:2] in known:
                    continue
                known.add(form[:2])
                parse_data = form[2]
                isv_lemma = parse_data.normal_form
                tag = parse_data.tag
                entry = slovnik[slovnik.isv == isv_lemma]
                if len(entry):
                    isv_id = entry.index[0]
                    isv_genesis = entry.genesis.values[0]
                    slovnik_pos = entry.partOfSpeech.values[0]
                    #if len(entry) > 1:
                    #    print("AMBIGUITY")
                else:
                    isv_id = -1
                    isv_genesis = ""
                    slovnik_pos = ""
                extracted = extract_stem_prefix_suffix(form[0], parse_data, isv_dict)
                partitioned_word = (
                    (extracted[0] + "’") if extracted[0] else ""
                    + extracted[1] + "፨" + extracted[2]
                )
                new_variant = ParseVariant(
                    [partitioned_word],
                    tag, slovnik_pos, isv_lemma,
                    isv_id, isv_genesis, 
                    False
                )
                variants.append(new_variant)

        else:
            tag = None
            # pos = "PUNCT" if t.text in punctuation else "UNKNOWN"
            isv_lemma = None
            isv_id = -1
            isv_genesis = ""
            slovnik_pos = ""
            only_variant = ParseVariant(
                [t.text],
                tag, slovnik_pos, isv_lemma,
                isv_id, isv_genesis,
                False
            )
            variants = [only_variant]
        ann_token = AnnotatedToken(
            variants,
            cap, space_after,
        )
        tokens_data.append(ann_token)
    return tokens_data

def stringify_token_text(t):

    all_texts = sum((v.text_variants for v in t.variants), [])
    all_texts = list(set(all_texts))
    # if len(t.variants) == 1 and len(t.variants.text_variants) == 1:
    if len(all_texts) == 1:
        return t.variants[0].text_variants[0] + t.space_after
    else:
        return f"[{'|'.join(all_texts)}]" + t.space_after

def pretty_stringify(tokens_data):
    final = "".join(
        stringify_token_text(t) for t in tokens_data
    )
    return final

def tokens_to_string(tokens):
    final = [
        token.variants[0].text_variants[0] + token.space_after
        for token in tokens
    ]
    return "".join(final)

def all_token_text_variants(token):
    return list(set(sum((v.text_variants for v in token.variants), [])))
    
def tokens_to_string_randomly(tokens):
    final = [
        choice(all_token_text_variants(token)) + token.space_after
        for token in tokens
    ]
    return "".join(final)


from itertools import product

from isv_nlp_utils.flavorization.tokenizer import all_token_text_variants

def tokens_to_exhaustive_string_list(tokens):
    all_texts_for_each_token = [all_token_text_variants(token) for token in tokens]
    spaces = [token.space_after for token in tokens]
    variants = [
        [text_var + space_after for text_var in token_variants]
        for (token_variants, space_after) in zip(all_texts_for_each_token, spaces)
    ]
    return product(*variants)


if __name__ == "__main__":
    Src = "Kromě togo, kȯgda sědite v problematikě MS, v glåvě sę vam skladaje taky sistem kako maly domȯk iz kostȯk Lego. V mojej glåvě jest po tutom principu vȯznikla bogatějša forma MS, ktorų råboće, sam za sebę, nazyvajų srědnoslovjańsky. Čisty MS jest posvęćeny ljud́am i komunikaciji, zato trěbuje byti universaĺno råzumlivy tako mnogo, kako jest možno. Iz drugoj stråny bogatějši međuslovjańsky, teoretično upotrěblivy v literaturě ili pěsnjah, jest na tutčas glåvno za prijateljev językov. K drugym ljud́am on ne progovori, zatože on v sobě imaje bogat́stvo vsih slovjańskyh językov, a vśaky slovjańskojęzyčny člověk znaje jedino tų čęst́, ktorų v sobě imaje jegovy język."
    compute_annotated_tokens(Src)

