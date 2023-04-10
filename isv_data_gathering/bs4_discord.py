from bs4 import BeautifulSoup
import glob
from urllib.parse import unquote
from collections import defaultdict

import pandas as pd
from tqdm import tqdm

all_files = glob.glob(unquote("/home/bt/dev/Med%C5%BAuslovjanska%20bes%C4%9Bda.%20Arhiv%20od%2023-08/*.html"))
all_files = glob.glob("C:\dev\Medźuslovjanska besěda. Arhiv od 23-08\*.html")

koristniki = defaultdict(dict)

i = 0
for fname in all_files:
    print(fname)
    #if "novi-ljudi" not in fname:
    #    print("SKIP")
    #    continue
    i += 1
    with open(fname, 'r', encoding="utf8") as f:
        efg = f.read()

    soup = BeautifulSoup(efg)
    for entry in tqdm(soup.find_all("div", {"class": "chatlog__message-group"})):
        author = entry.find_all("span", {"class": "chatlog__author-name"})
        uid = author[0].get("data-user-id")
        aut_nick = author[0].get("title")
        # koristniki[aut_nick]["title"] = aut_nick
        if koristniki[aut_nick].get("uid", uid) != uid:
            raise NameError(f"duplicate! '{koristniki[aut_nick]['uid']}' and '{uid}' for '{aut_nick}'")
        koristniki[aut_nick]["uid"] = uid
        for msg in entry.find_all("div", {"class": "chatlog__message"}):
            msg_timestamp = msg.get('title')
            if "novi-ljudi" in fname and aut_nick == "MEE6#4876":
                for enter_mention in msg.find_all("span", {"class": "mention"}):
                    if enter_mention.text[0] != "@":
                        continue
                    aut_nick = enter_mention.get("title")

                    if "joined" not in koristniki[aut_nick]:
                        koristniki[aut_nick]["joined"] = msg_timestamp
                for leave_mention in msg.find_all("strong"):
                    if "#" not in leave_mention.text:
                        continue
                    aut_nick = leave_mention.text
                    koristniki[aut_nick]["left"] = msg_timestamp
            koristniki[aut_nick]["total_len"] = koristniki[aut_nick].get("total_len", 0) + len(msg.text)
            koristniki[aut_nick]["num_messages"] = koristniki[aut_nick].get("num_messages", 0) + 1

    #if i > 5:
    #    break

result_df = pd.DataFrame.from_dict(koristniki)
print(result_df.T.head())
i = 0
for koristnik, data in koristniki.items():
    i += 1
    if i == 10:
        break
    print(koristnik)
    print(data)

result_df.to_csv("koristniki.csv")
