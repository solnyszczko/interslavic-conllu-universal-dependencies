import conllu
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
        
        

        

        if token["form"] not in string.punctuation:

            wordcount = wordcount+1





        for isvword in isvwords:
            
            if token_lemma == isvword["pl"]:
                isvhit =1
                if jellyfish.jaro_winkler_similarity(token_lemma, isvword["isv"]) >= isvsimilarity:
              #      print(jellyfish.jaro_winkler_similarity(token["lemma"] , isvword["isv"]))
                    token["lemma"] = isvword["isv"]
                    parses = morph.parse(token["lemma"])
                    token["form"] = constants.inflect_carefully(morph, parses[0], {"sing", "masc","past"})[0]
                    

                
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


