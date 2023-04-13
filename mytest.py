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
punctuation_chars = list(string.punctuation)
punctuation_chars.extend(['‘', '’', '“', '”', '…', '–', '—','„'])

morph = constants.create_etm_analyzer(PATH)


with open("isvwords.json") as f:
    isvwords = json.load(f)
  #  print(d)


open("isv_polish.conllu", 'w')


print(isvwords[123]['pl'])


data_file = open("pl_pud-ud-train2.conllu", "r", encoding="utf-8")
for tokenlist in conllu.parse_incr(data_file):

    wordcount = 0
    isvwordcount = 0
  #  print(tokenlist)

    for token in tokenlist:
      if token["form"] not in punctuation_chars:

        wordcount = wordcount+1
        isvhit=0
        isvsimilarity=0

        if token["lemma"] == 'sam': token["lemma"] = "samy"
        if token["lemma"] == 'sę': token["lemma"] = "się"
        if 'więcej' in token["lemma"]: token["upos"] = "PART"
     #   if token["lemma"] == 'więcej': token["feats"] = None
        




        token_lemma = token["lemma"]
        token_upos = token["upos"]
        token_upos_fixed = None
        token_xpos = token["xpos"] 
        token_feats = token["feats"]
        token_deprel = token["deprel"]

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
        token_voice = None
        token_prontype = None
        token_reflex = None
        token_polarity = None






        



      #  print(f"token_feats::::::: {token_feats}")
        if token_feats is not None:

          if "Reflex" in token_feats:
            if token_feats["Reflex"]=="Yes": token_reflex="Refl"

          if "Polarity" in token_feats:
            if token_feats["Polarity"]=="Neg": token_reflex="neg"


          if "PronType" in token_feats:
            if token_feats["PronType"]=="Int":token_prontype='int'
            if token_feats["PronType"]=="Dem":token_prontype='dem'
            if token_feats["PronType"]=="Rel":token_prontype='rel'
            if token_feats["PronType"]=="Prs":token_prontype='pers'
            if token_feats["PronType"]=="Ind":token_prontype='indef'



          if "Voice" in token_feats:
            if token_feats["Voice"] == "Act": token_voice = "actv"
            elif token_feats["Voice"] == "Pass": token_voice = "pssv"


          if "Case" in token_feats:


            if token_feats["Case"] == 'Gen': token_case = 'gent'
            elif token_feats["Case"] == 'Acc': token_case = 'accs'
            elif token_feats["Case"] == 'Loc': token_case = 'loct'
            elif token_feats["Case"] == 'Dat': token_case = 'datv'
            elif token_feats["Case"] == 'Nom': token_case = 'nomn'
            elif token_feats["Case"] == 'Ins': token_case = 'ablt'
            elif token_feats["Case"] == 'Voc': token_case = 'voct'

            else: token_case = token_feats["Case"].lower()
      
          if "Animacy" in token_feats:
    
            if token_feats["Animacy"] =="Hum": token_animacy = "anim"
            elif token_feats["Animacy"] =="Inan": token_animacy = "inan"
            elif token_feats["Animacy"] =="Nhum": token_animacy = "inan"


          if "Aspect" in token_feats:

              if token_feats["Aspect"] == "Imp": token_aspect = "impf"
              elif token_feats["Aspect"] == "Perf": token_aspect = "perf"
          if "Person" in token_feats: token_person = token_feats["Person"] + 'per'
          if "VerbForm" in token_feats: 
              if token_feats["VerbForm"] == "Inf": token_verbform = "infn"
              if token_feats["VerbForm"] == "Fin": token_verbform = "fin"
              if token_feats["VerbForm"] == "Part": token_verbform = "part"
          if "Gender" in token_feats:
              if token_feats["Gender"] == "Fem": token_gender = "femn"
              else: token_gender = token_feats["Gender"].lower()
          if "Tense" in token_feats:
              if token_feats["Tense"] == 'Fut': token_tense='futr'
              else: token_tense = token_feats["Tense"].lower() 
          if "VerbType" in token_feats:
              token_verbtype = token_feats["VerbType"] 
          if "Number" in token_feats:

              if token_feats["Number"]=='Ptan': token_number="plur"
              else: token_number = token_feats["Number"].lower() 
          if "Mood" in token_feats:
              if token_feats["Mood"] == "Imp": token_mood = "impr"
              elif token_feats["Mood"] == "Cnd": token_mood = "cond"
              elif token_feats["Mood"] == "Ind": token_mood = "cond"
              

          #    else: token_mood = token_feats["Mood"].lower() 




        
        
        if token_upos == "ADJ": token_upos_fixed = "ADJF"
        elif "VERB" in token_upos: token_upos_fixed = "VERB"
        elif token_upos == "DET": token_upos_fixed = "NPRO"
        elif token_upos == "PRON": token_upos_fixed = "NPRO"
        elif token_upos == "NUM": token_upos_fixed = "NUMR"
        elif (token_upos == "AUX") and (token_xpos == "part"): token_upos_fixed = "PART"
        elif (token_upos == "AUX") and (token_xpos != "part"): token_upos_fixed = "VERB"
        
        else: token_upos_fixed = token_upos



                 

          for x in {token_aspect,token_reflex, token_case, token_gender, token_number,token_polarity, token_person, token_verbform, token_tense, token_verbtype, token_mood, token_animacy,token_voice,token_prontype}:
              if x is not None:
                processed_token_feats.add(x)

          if (token_verbform == "Part") and (token["upos"] == "ADJ"):
            token_upos = "VERB"
            token_upos_fixed = "VERB"
            token["upos"] = "VERB"



        print(token_lemma, token["form"], token_upos, token_feats, token_xpos, token_deprel)

            




        for isvword in isvwords:
            isvword["isv"] = isvword["isv"].replace("#",'')
            isvword["isv"] = isvword["isv"].replace("t́","ť")
            isvword["isv"] = isvword["isv"].replace("ď","ď")
            
            
            if (token_lemma in isvword["pl"].split(", ")) and (' ' not in isvword["isv"]):
                print(token_lemma, token["form"], token_upos, token_feats)
                isvhit =1

                
                #ON FIRST ISV HIT CONVERT POLISH ORTHOGRAPHY OF LEMMA TO INTERSLAVIC FOR BETTER JARO WINKLER

#ADD: USE ALL POSSIBLE matched isv words instead of just the most similar                
                if jellyfish.jaro_winkler_similarity(token_lemma, isvword["isv"]) >= isvsimilarity:
              #      print(jellyfish.jaro_winkler_similarity(token["lemma"] , isvword["isv"]))
                    token["lemma"] = isvword["isv"]
                    #print("DESUSUSUSUSU")
                    parses = morph.parse(token["lemma"])
                    
                    try: advb_in_parses = ("ADVB" in parses[0][1])
                    except: advb_in_parses = False


                    proper_parse = []
#FIX PROPER NOUN PROPER NOUN
                    if (token_upos_fixed=="ADV") or (token_upos_fixed == "PART") or (token_upos_fixed == "ADP") or (token_upos_fixed == "CCONJ") or (token_upos_fixed == "X") or (token_upos_fixed == "SCONJ") or advb_in_parses:
                      
                      token["form"] = token["lemma"]
                    elif (token_upos_fixed == "PROPN"):
                      token["form"]=token["form"]
                    else:


                      #if "VerbForm" in token_feats:
                      #    token["form"] = constants.inflect_carefully(morph, parses[0], processed_token_feats)[0]

                          
                      if (token_verbtype !='Quasi'):
                          
                            for parse in parses:
                         #     print(parse) 

                              if proper_parse == []:
                                proper_parse.append(parses[0])
                              
                         #       print(parse[1])
                                 
                              if token_upos_fixed == parse[1].POS: 
                                    proper_parse.append(parse)
                         #           print(f"PROPER_REALLLLLLLLL  {proper_parse[0]}")
                         #           print("meow")
                                  
                          #    print(proper_parse)
                          #    print(processed_token_feats)
                          #    print( constants.inflect_carefully(morph, parses[0], processed_token_feats))
                            try:token["form"] = constants.inflect_carefully(morph, proper_parse[1], processed_token_feats)[0]
                            except:token["form"] = constants.inflect_carefully(morph, proper_parse[0], processed_token_feats)[0]

#FIX: VERBS SUCH AS odzyskać WHICH HAVE WEIRD ISV TRANSLATIONS SUCH AS iziskati ponovno
                   
                      

                
             #   print(token_lemma,' ', token["form"],' ', token["lemma"])
        if isvhit==1:
            isvwordcount = isvwordcount+1    

    if (isvwordcount/wordcount) > .7:
      with open("isv_polish.conllu", 'a') as g:
        g.write(tokenlist.serialize())  

    #    print('  ')

 #   print(f"WORDS IN SENTENCE: {wordcount}")
  #  print(f"ISV WORDS IN SENTENCE: {isvwordcount}")

   # print(tokenlist[0]["lemma"])
  #  print('\n')



g.close()
#print(new_file)


