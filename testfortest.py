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

parses = morph.parse("brati")
print(parses[0][1])
print(parses[1])
print(parses[2])

print( constants.inflect_carefully(morph, parses[2], { "1per", "pres", "sing", "femn"}))


if "NOUN" in parses[0][1]:
  print("YIPPPE")



if "NOUN" in parses[2][1]:
  print("GREEEE")


if "VERB" in parses[2][1]:
  print("weeee")


parses = morph.parse("raz")
print(parses[0][1])
print(parses[1][1])
print(parses[2])