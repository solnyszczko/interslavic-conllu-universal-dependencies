import conllu
from conllu.parser import parse_dict_value
from io import open
import os
import sys
import string
import json
import jellyfish
from isv_nlp_utils import constants
import udapi

PATH = os.path.dirname(sys.argv[0])

morph = constants.create_etm_analyzer(PATH)


with open("isvwords.json") as f:
    isvwords = json.load(f)
  #  print(d)

print(isvwords[123]['pl'])


data_file = open("pl_pud-ud-train.conllu", "r", encoding="utf-8")
for tokenlist in conllu.parse_incr(data_file):

    wordcount = 0
    isvwordcount = 0
  #  print(tokenlist)

    for token in tokenlist:
        isvhit=0
        isvsimilarity=0
        token_lemma = token["lemma"]
        token_upos = token["upos"]
        token_xpos = token["xpos"] 
        token_feats = token["feats"]
        token_deprel = token["deprel"]
       # print(token_deprel, token_feats, token_upos, token_xpos)
        print(token_lemma, token["form"], token_upos, token_feats)
        
        
        

        

        if token["form"] not in string.punctuation:

            wordcount = wordcount+1

        if token_upos == "NOUN":

          if token_feats["Case"] == 'Gen': token_case = 'gent'
          elif token_feats["Case"] == 'Acc': token_case = 'accs'
          elif token_feats["Case"] == 'Loc': token_case = 'loct'
          elif token_feats["Case"] == 'Dat': token_case = 'datv'
          elif token_feats["Case"] == 'Nom': token_case = 'nomn'
          elif token_feats["Case"] == 'Ins': token_case = 'inst'
          elif token_feats["Case"] == 'Abl': token_case = 'ablt'
          else: token_case = token_feats["Case"].lower()
          token_gender = token_feats["Gender"].lower()
          token_number = token_feats["Number"].lower()
     #     print(token_case)
       #   print(token_number)
          if "Animacy" in token_feats:
            token_animacy = token_feats["Animacy"].lower()
       #     print(token_animacy)

        if token_upos == "VERB":
          token_verbtype = ""
          

          if "Aspect" in token_feats:

            if token_feats["Aspect"] == "Imp": token_aspect = "impf"
            elif token_feats["Aspect"] == "Perf": token_aspect = "perf"
          if "Person" in token_feats: token_person = token_feats["Person"] + 'per' 
          if "VerbForm" in token_feats: 
            if token_feats["VerbForm"] == "Inf": token_verbform = "infn"
            if token_feats["VerbForm"] == "Fin": token_verbform = "fin"
          if "Gender" in token_feats:
            if token_feats["Gender"] == "Fem": token_gender = "femn"
            else: token_gender = token_feats["Gender"].lower()
          if "Tense" in token_feats:
            token_tense = token_feats["Tense"].lower() 
          if "VerbType" in token_feats:
            token_verbtype = token_feats["VerbType"] 




        for isvword in isvwords:
            
            if (token_lemma == isvword["pl"]) and (' ' not in isvword["isv"]):
           #     print(token_lemma, token["form"], token_upos, token_feats)
                isvhit =1
#ADD: USE ALL POSSIBLE matched isv words instead of just the most similar                
                if jellyfish.jaro_winkler_similarity(token_lemma, isvword["isv"]) >= isvsimilarity:
              #      print(jellyfish.jaro_winkler_similarity(token["lemma"] , isvword["isv"]))
                    token["lemma"] = isvword["isv"]
                    parses = morph.parse(token["lemma"])

                    if token_upos == "NOUN":
                      #for pos in parses
                      if "VerbForm" in token_feats:
                        try: token["form"] = constants.inflect_carefully(morph, parses[0], {token_case, token_gender,token_number, "V2NOUN"})[0]
                        except: token["form"] = constants.inflect_carefully(morph, parses[1], {token_case, token_gender,token_number, "V2NOUN"})[0]
                      else:

                        try: token["form"] = constants.inflect_carefully(morph, parses[0], {token_upos, token_case, token_gender,token_number})[0]
                        except: token["form"] = constants.inflect_carefully(morph, parses[1], {token_upos, token_case, token_gender,token_number})[0]
#FIX: VERBS SUCH AS odzyskać WHICH HAVE WEIRD ISV TRANSLATIONS SUCH AS iziskati ponovno
                    if token_upos == "VERB" :
                      if token_feats["VerbForm"] == "Inf": token["form"] = constants.inflect_carefully(morph, parses[0], {token_verbform})[0]
                      elif (token_feats["VerbForm"] == "Fin") and (token_feats["Tense"] == "Pres") and (token_verbtype !='Quasi'):
                        try: token["form"] = constants.inflect_carefully(morph, parses[0], {token_person, token_tense, token_gender})[0]
                        except: token["form"] = constants.inflect_carefully(morph, parses[1], {token_person, token_tense})[0]
                      


                    

                
             #   print(token_lemma,' ', token["form"],' ', token["lemma"])
        if isvhit==1:
            isvwordcount = isvwordcount+1    

    if (isvwordcount/wordcount) > .9:
        print(tokenlist.serialize())  

    #    print('  ')

 #   print(f"WORDS IN SENTENCE: {wordcount}")
  #  print(f"ISV WORDS IN SENTENCE: {isvwordcount}")

   # print(tokenlist[0]["lemma"])
  #  print('\n')




#print(new_file)


