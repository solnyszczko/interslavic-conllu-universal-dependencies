from bs4 import BeautifulSoup
import glob
from urllib.parse import unquote
from collections import defaultdict, Counter
import pickle

from tqdm import tqdm


import pymorphy2
# from normalizacija import fix_esperanto, fix_silmeth, fix_polish, fix_diacritics, fix_russian, fix_soft_etm_russian, convert2MSPlus
from isv_nlp_utils.normalizacija import normalize_and_simple_spellcheck, transliterate_cyr2lat, fix_text
# from example2 import print_spellcheck
from isv_nlp_utils.constants import DISCORD_USERNAME_REGEX, create_analyzers_for_every_alphabet
from langid.langid import LanguageIdentifier, model
lang_guesser = LanguageIdentifier.from_modelstring(model, norm_probs=True)

all_files = glob.glob("C:\\dev\\beseda_arhiv\\*.html")

examples = {}
texts_data = []
all_unknowns = list()
form_data = defaultdict(list)
errors_stats = {}


abecedas = create_analyzers_for_every_alphabet()

i = 0
for fname in all_files[:]:
    print(fname)
    errors_stats[fname] = []
    with open(fname, 'r', encoding="utf8") as f:
        efg = f.read()

    soup = BeautifulSoup(efg, "lxml")
    for entry in soup.find_all("div", {"class": "chatlog__message-group"}):
        author = entry.find_all("span", {"class": "chatlog__author-name"})
        uid = author[0].get("data-user-id")
        aut_nick = author[0].get("title")
        for msg in entry.find_all("div", {"class": "chatlog__content"}):
            if msg.a is not None:
                a_tag = msg.a.extract()
            for span in msg.find_all("span", {"class": "mention"}):
                span.extract()
            if len(msg.text.strip()) < 100 or len(set(msg.text.strip())) < 3:
                continue
            #if aut_nick not in {"silmeth#2378", "grytozło#4895", "bt#0290", "Melac#2576", "Siciliano#2338"}:
            #    continue
            #if aut_nick not in {"silmeth#2378"}:
            #    continue
            # print(msg.text.strip())
            # print("------")
            i += 1
            best_orthography, changed_text, mean_score = normalize_and_simple_spellcheck(msg.text, abecedas)

            lang_guess = [(l, p) for (l, p) in lang_guesser.rank(msg.text) if p > 1e-40]
            errors_stats[fname].append( (mean_score, lang_guess) )
            if mean_score > 0.33 and lang_guess[0][0] != "en":
                for token in best_orthography[2]:
                    razbor = abecedas[best_orthography[0].split("|")[0]].parse(token)
                    lemma_form = razbor[0].normal_form if razbor else token
                    lemma_form = transliterate_cyr2lat(lemma_form)

                    form_data[lemma_form].append(transliterate_cyr2lat(token))
                all_unknowns += best_orthography[2]

            if examples.get(best_orthography[0], 0) < mean_score and mean_score > 0.5:
                #     print(best_orthography, num_tokens, mean_score)
                if examples.get(best_orthography[0], 0) == 0:
                    print(aut_nick, best_orthography[0], mean_score)
                    print(best_orthography[2])
                    # print_spellcheck(msg.text, abecedas['etm'])
                    print(lang_guess)
                    # print_spellcheck(changed_text, abecedas[best_orthography[0].split("|")[0]])
                examples[best_orthography[0]] = mean_score

            if mean_score > 0.6:
                #     print(best_orthography, num_tokens, mean_score)
                texts_data.append({
                    "author": aut_nick,
                    'orth': best_orthography,
                    'score': mean_score,
                    'fixed_text': changed_text,
                    'lang_guess': lang_guess
                })


print(Counter([x for x in all_unknowns if len(x) == 1]).most_common(25))
all_unknowns = [
    transliterate_cyr2lat(x) for x in all_unknowns
    if len(x) > 1 and x not in {
            'the', 'and', 'of', 'is', 'in', 'edited', 'it',
            'antonlandao', 'melac', 'tycho', 'deleted-channel', 'gebrėm', 'giimiks'
        }
]
print(Counter(all_unknowns).most_common(25))

import json

with open("unk_words.txt", "w", encoding="utf8") as f:
    json.dump(all_unknowns, f, ensure_ascii=False)

with open("unk_words_stats.txt", "w", encoding="utf8") as f:
    json.dump(dict(Counter(all_unknowns).most_common()), f, ensure_ascii=False)

with open("kanal_stats.txt", "w", encoding="utf8") as f:
    json.dump(dict(errors_stats), f, ensure_ascii=False)

with open("unk_words_lemmas.txt", "w", encoding="utf8") as f:
    json.dump(dict(form_data), f, ensure_ascii=False)

with open("texts.pkl", "wb") as f:
    pickle.dump(texts_data, f)
