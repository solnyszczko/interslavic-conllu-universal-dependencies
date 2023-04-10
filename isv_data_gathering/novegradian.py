import requests
from time import sleep
import json


headers = {'accept': 'application/json'}

entries = requests.get("https://veche.net/lexicon/novegradian/entries/", headers=headers).json()
print(entries.keys(), entries["total_matches"])

data_from_lexicon = []

for entry_name in entries["results"]:
    print(entry_name)
    entry = requests.get(f"https://veche.net/lexicon/novegradian/entries/{entry_name}", headers=headers).json()
    print(entry['notes'])
    print(entry['etymology'])
    print(entry['cognates'])
    data_from_lexicon.append(entry)
    sleep(1)

with open("NV.json", "w") as f:
    json.dump(data_from_lexicon, f)

