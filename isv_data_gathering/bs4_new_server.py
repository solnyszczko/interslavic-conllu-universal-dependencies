from bs4 import BeautifulSoup
import glob
from urllib.parse import unquote
from collections import defaultdict

import pandas as pd
from tqdm import tqdm

koristniki_df = pd.read_csv("koristniki.csv", index_col=0).T.copy()
koristniki = defaultdict(dict)

fname = "C:/Users/bt/Downloads/Telegram Desktop/Medžuslovjansky_•_Меджусловјанскы_•_Interslavic_Pozdråv_•_Поздрав.html"
with open(fname, 'r', encoding="utf8") as f:
    efg = f.read()

soup = BeautifulSoup(efg)
for entry in tqdm(soup.find_all("div", {"class": "chatlog__message-group"})):
    author = entry.find_all("span", {"class": "chatlog__author-name"})
    aut_nick = author[0].get("title")
    msg_timestamp = entry.find("span", {"class": "chatlog__timestamp"}).text
    for msg in entry.find_all("div", {"class": "chatlog__message"}):
        if aut_nick == "MEE6#4876":
            for enter_mention in msg.find_all("span", {"class": "mention"}):
                if enter_mention.text[0] != "@":
                    continue
                aut_nick = enter_mention.get("title")

                if "new_server" not in koristniki[aut_nick]:
                    koristniki[aut_nick]["new_server"] = msg_timestamp

fname = "C:/Users/bt/Downloads/Telegram Desktop/Medžuslovjansky_•_Меджусловјанскы_•_Interslavic_Glåvne_•_Главне.html"
with open(fname, 'r', encoding="utf8") as f:
    efg = f.read()

soup = BeautifulSoup(efg)
for entry in tqdm(soup.find_all("div", {"class": "chatlog__message-group"})):
    author = entry.find_all("span", {"class": "chatlog__author-name"})
    aut_nick = author[0].get("title")
    msg_timestamp = entry.find("span", {"class": "chatlog__timestamp"}).text
    for msg in entry.find_all("div", {"class": "chatlog__message"}):
        for content in msg.find_all("span", {"class": "preserve-whitespace"}):
            if content.text == "Joined the server.":
                koristniki[aut_nick]["new_server"] = msg_timestamp
        if "new_server" not in koristniki[aut_nick]:
            koristniki[aut_nick]["new_server"] = "At least " + msg_timestamp


indices = []
joined = []

NS_index = set(koristniki_df.index)

n_in = 0
n_not_in = 0
for koristnik, data in koristniki.items():
    if koristnik in NS_index:
        n_in += 1
    else:
        n_not_in += 1
    if koristnik in NS_index:
        indices.append(koristnik)
        joined.append(data.get('new_server'))
        # koristniki_df.loc[koristnik, "joined_new_server"] = data['new_server']
        # print(koristniki_df.loc[koristnik, "joined_new_server"])
        # print(koristnik, "joined_new_server", data['new_server'])

print(n_in, n_not_in)

koristniki_df.loc[indices, "joined_new_server"] = joined

print(koristniki_df.head())

print(koristniki_df.joined_new_server.unique())

koristniki_df.num_messages = koristniki_df.num_messages.astype(int)
koristniki_df.sort_values(by="num_messages", ascending=False).to_csv("koristniki_comparision.csv")
