import conllu
from conllu.parser import parse_dict_value
from io import open
import os
import sys
import string
import json
import jellyfish
from isv_nlp_utils import constants
from isv_data_gathering import translation_aux

PATH = os.path.dirname(sys.argv[0])
punctuation_chars = list(string.punctuation)
punctuation_chars.extend(['‘', '’', '“', '”', '…', '–', '—', '„'])

morph = constants.create_etm_analyzer(PATH)


with open("isvwords.json") as f:
    isvwords = json.load(f)


open("isv_polish.conllu", 'w').close()
total_words = 0
good_inflects = 0
failed_inflects = 0
failed_inflects_set = set()
failed_match_set = set()


inflects_dict = {'verb': {'good':0,'bad':0},'noun': {'good':0,'bad':0},'pron': {'good':0,'bad':0},'adj': {'good':0,'bad':0},
                 'part': {'good':0,'bad':0},'total': {'good':0,'bad':0},'total_isv': {'good':0,'bad':0},
                 "proper_nouns":0}


def try_inflect(pos,token,morph,isvword,processed_token_feats,token_upos_fixed):
         try:

             token_form_original = token["form"]
             inflected = translation_aux.inflect_carefully(morph, isvword["isv"], processed_token_feats, pos=token_upos_fixed)[0]
             print(f"{pos} INFLECT SUCCESS: {token_form_original} -> {inflected}")
             inflects_dict[pos]["good"] +=1
             
             return inflected
         except:
             print("FAIL INFLECT")
             inflects_dict[pos]["bad"] +=1
             return []
             
        
    



data_file = open("pl_pud-ud-train2.conllu", "r", encoding="utf-8")
for tokenlist in conllu.parse_incr(data_file):


    for token in tokenlist:
        if token["form"] not in punctuation_chars:
            total_words = total_words +1

            inflects_dict["total"]["good"]+=1
            isvsimilarity = 0
            isvdeclined = 0
            token_lemma_original = token["lemma"]

# FIX SAMY SIE WIECEJ CASES

            token_upos_fixed = translation_aux.UDPos2OpenCorpora(token["upos"].lower())

            if token["feats"] is not None:

                processed_token_feats = translation_aux.UDFeats2OpenCorpora(token["feats"], "pl")
                token["feats"]["OpenC"] = repr(processed_token_feats)
                
            if token["upos"] == "PROPN":
                inflects_dict["proper_nouns"] +=1
                isvdeclined == 1
                

            else: 
             for isvword in isvwords:
                isvword["isv"] = isvword["isv"].replace( "#", '')  # FIX ALL ISV CLEAN t' and d'

                clean_check = (token_lemma_original in isvword["pl"].split(", ")) and (' ' not in isvword["isv"])

                verb_check = ("verb" in token_upos_fixed) and (isvword["partOfSpeech"].startswith("v."))
                noun_check = ("noun" in token_upos_fixed) and ((isvword["partOfSpeech"].startswith("m.")) or (isvword["partOfSpeech"].startswith("f.")) or (isvword["partOfSpeech"].startswith("n.")))
                adj_check = ("adj" in token_upos_fixed) and (isvword["partOfSpeech"].startswith("adj"))
                pron_check = ("npro" in token_upos_fixed) and (isvword["partOfSpeech"].startswith("pron"))
                conj_check = ("conj" in token_upos_fixed) and (isvword["partOfSpeech"].startswith("conj"))
                part_check = ("part" in token_upos_fixed) and (isvword["partOfSpeech"].startswith("particle"))
                adv_check = ("adv" in token_upos_fixed) and (isvword["partOfSpeech"].startswith("adv"))
                undeclinable_check = conj_check or part_check or adv_check

                similarity_check = jellyfish.jaro_winkler_similarity(token_lemma_original, isvword["isv"]) >= isvsimilarity
                
                if clean_check and similarity_check and (undeclinable_check):
                    token["form"] = isvword["isv"]

                    
                    inflects_dict["part"]["good"] +=1

                if clean_check and similarity_check:
                    print(token["lemma"], token["form"], token["upos"],token["xpos"], token["deprel"], token["feats"], token["misc"])

                    isvdeclined = 1

                # ON FIRST ISV HIT CONVERT POLISH ORTHOGRAPHY OF LEMMA TO INTERSLAVIC FOR BETTER JARO WINKLER

# ADD: USE ALL POSSIBLE matched isv words instead of just the most similar

                    token["lemma"] = isvword["isv"]
#ADVB IS WEIRD or uhh nvm it doesnt exist???

# FIX PROPER NOUN PROPER NOUN
# MAKE SURE TO CHECK PART OF SPEECH BEFORE SENDING LEMMA
# (token["VerbType"] !='Quasi')
                    if verb_check:
                        
                        
                        test = try_inflect("verb",token,morph,isvword,processed_token_feats,token_upos_fixed)
                        
                        if test !=[]:token["form"] = test;isvdeclined = 1
                        else: 

                                failed_inflects_set.add(token_lemma_original)
                                isvdeclined = 0
                                
                                
                                
                    if noun_check:
                        test = try_inflect("noun",token,morph,isvword,processed_token_feats,token_upos_fixed)
                        
                        if test !=[]:token["form"] = test;isvdeclined = 1
                        else: 

                                failed_inflects_set.add(token_lemma_original)
                                isvdeclined = 0
                                
                                
                    if adj_check:
                        test = try_inflect("adj",token,morph,isvword,processed_token_feats,token_upos_fixed)
                        
                        if test !=[]:token["form"] = test;isvdeclined = 1
                        else: 

                                failed_inflects_set.add(token_lemma_original)
                                isvdeclined = 0
                                
                    if pron_check: # 'to'/'toj' is not in ISVWORDS
                        test = try_inflect("pron",token,morph,isvword,processed_token_feats,token_upos_fixed)
                        
                        if test !=[]:token["form"] = test;isvdeclined = 1
                        else: 

                                failed_inflects_set.add(token_lemma_original)
                                isvdeclined = 0
                                
                                
                    
# FIX: VERBS SUCH AS odzyskać WHICH HAVE WEIRD ISV TRANSLATIONS SUCH AS iziskati ponovno

            if isvdeclined == 1:
                inflects_dict["total_isv"]["good"] +=1

    if ((inflects_dict["total_isv"]["good"] + inflects_dict["proper_nouns"]) /inflects_dict["total"]["good"]) > 0.6:
        with open("isv_polish.conllu", 'a') as g:
            g.write(tokenlist.serialize())

print(failed_inflects_set)
print(f"GOOD INFLECTS COUNT: {inflects_dict} ")

#failed inflects: {'USA', 'zająć', 'brać', 'bramka', 'żal', 'raz', 'cud', 'gol'}
g.close()
