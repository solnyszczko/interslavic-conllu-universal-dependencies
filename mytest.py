import conllu
from conllu.parser import parse_dict_value
from io import open
import os
import sys
import string
import json
import jellyfish
from isv_nlp_utils import constants
#import udapi

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
        token_upos_fixed = None
        token_xpos = token["xpos"] 
        token_feats = token["feats"]
        token_deprel = token["deprel"]

        print(token_lemma, token["form"], token_upos, token_feats, token_xpos, token_deprel)
        
        
        if token_upos == "ADJ": token_upos_fixed = "ADJF"
        elif token_upos == "ADV": token_upos_fixed = "ADVB"
        elif token_upos == "PART": token_upos_fixed = "PRCP"
        else: token_upos_fixed = token_upos


        

        if token["form"] not in string.punctuation:

          wordcount = wordcount+1
          token_verbtype = None
          processed_token_feats = set()
          token_aspect = None
          token_person = None
          token_verbform = None
          token_gender = None
          token_tense = None
          token_verbtype = None
          token_number = None
          token_mood = None
          token_case = None
          token_animacy = None

        print(f"token_feats::::::: {token_feats}")
        if token_feats is not None:
          if "Case" in token_feats:


            if token_feats["Case"] == 'Gen': token_case = 'gent'
            elif token_feats["Case"] == 'Acc': token_case = 'accs'
            elif token_feats["Case"] == 'Loc': token_case = 'loct'
            elif token_feats["Case"] == 'Dat': token_case = 'datv'
            elif token_feats["Case"] == 'Nom': token_case = 'nomn'
            elif token_feats["Case"] == 'Ins': token_case = 'inst'
            elif token_feats["Case"] == 'Abl': token_case = 'ablt'
            elif token_feats["Case"] == 'Voc': token_case = 'voct'

            else: token_case = token_feats["Case"].lower()
      
          if "Animacy" in token_feats:
    
            if token_feats["Animacy"] =="Hum": token_animacy = "anim"
            elif token_feats["Animacy"] =="Inan": token_animacy = "inan"
            elif token_feats["Animacy"] =="Nhum": token_animacy = "inan"






          # {token_aspect, token_person, token_verbform, token_gender, token_tense, token_verbtype, token_number, token_mood}

          if "Aspect" in token_feats:

              if token_feats["Aspect"] == "Imp": token_aspect = "imperfect"
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
          if "Number" in token_feats:
              token_number = token_feats["Number"].lower() 
          if "Mood" in token_feats:
              if token_feats["Mood"] == "Imp": token_mood = "impr"
              elif token_feats["Mood"] == "Cnd": token_mood = "cond"
              

          #    else: token_mood = token_feats["Mood"].lower() 


          for x in {token_aspect, token_person, token_verbform, token_gender, token_tense, token_verbtype, token_number, token_mood, token_case, token_animacy}:
              if x is not None:
                processed_token_feats.add(x)

            




        for isvword in isvwords:
            
            if (token["form"] == isvword["pl"]) and (' ' not in isvword["isv"]): token["form"] = isvword["isv"]
            elif (token_lemma == isvword["pl"]) and (' ' not in isvword["isv"]):
           #     print(token_lemma, token["form"], token_upos, token_feats)
                isvhit =1
                #ON FIRST ISV HIT CONVERT POLISH ORTHOGRAPHY OF LEMMA TO INTERSLAVIC FOR BETTER JARO WINKLER
#ADD: USE ALL POSSIBLE matched isv words instead of just the most similar                
                if jellyfish.jaro_winkler_similarity(token_lemma, isvword["isv"]) >= isvsimilarity:
              #      print(jellyfish.jaro_winkler_similarity(token["lemma"] , isvword["isv"]))
                    token["lemma"] = isvword["isv"]
                    parses = morph.parse(token["lemma"])


                    proper_parse = None

                    if "VerbForm" in token_feats:
                        token["form"] = constants.inflect_carefully(morph, parses[0], processed_token_feats)[0]

                        
                    elif (token_verbtype !='Quasi'):
                        for parse in parses:
                          print(parse)
                          if token_upos_fixed in parse[1]: 
                            proper_parse = parse
                            print(proper_parse)
                            print("meow")
                          if proper_parse == None:
                            proper_parse =parses[0]

                        token["form"] = constants.inflect_carefully(morph, proper_parse, processed_token_feats)[0]

#FIX: VERBS SUCH AS odzyskać WHICH HAVE WEIRD ISV TRANSLATIONS SUCH AS iziskati ponovno
                   
                      

                
             #   print(token_lemma,' ', token["form"],' ', token["lemma"])
        if isvhit==1:
            isvwordcount = isvwordcount+1    

    if (isvwordcount/wordcount) > .7:
        print(tokenlist.serialize())  

    #    print('  ')

 #   print(f"WORDS IN SENTENCE: {wordcount}")
  #  print(f"ISV WORDS IN SENTENCE: {isvwordcount}")

   # print(tokenlist[0]["lemma"])
  #  print('\n')




#print(new_file)


