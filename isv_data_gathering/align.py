import numpy as np
from scipy.spatial import distance
from matplotlib import pyplot as plt
import seaborn as sbn

from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
# model = SentenceTransformer('sentence-transformers/LaBSE')
model = SentenceTransformer('sentence-transformers/paraphrase-xlm-r-multilingual-v1')

ISV_text = """Tut jest anglijsky kurs gramatiky.
Preporučajemo vsegda koristati toj slovnik medžuslovjanskogo jezyka za učenje slov i gramatiky.
(Až "najstarějši" govoritelji jego često koristajut)
Ako li potrěbno vam prěvoditi tekst na drugy alfabet (iz kirilice do latinice i naopak), možete koristati transliterator:
Slovnik ukazuje sklanjanje slov, a daže konkretno slovo možno najdti, koristajuči jego sklanjeny variant, napriměr, ne potrěbno iskati slovo "dělati" ale možno pokušati najdti slovo "dělaju". 
Čto vyše: tut sut linky za deklinatory i konjungatory, kake sut koristne vo fleksiji slov, ne jestvujučih vo medžuslovjanskom slovniku:
Razširjeny etimologičny alfabet na sajtu Jana van Steenbergena:
Dobry dokument ob etimologičnom izgovoru:
Na tutom serveru jestvuje trend daby pisati etimologičnym pravopisom.
To ne jest obvezno.
Ne trěbujete trvožiti se ako li ne znajete etimologičnogo pravopisa.
Ako li něčto jest za vas težko, preporučajemo čitati "čudne bukvy" kako jih najblizši, vizualny ekvivalent (ę jest prosto e, ć jest č, đ jest dž, ų jest u, å jest a, i tako dalje).
Tut takože brza pouka za kiriličske bukvy:
Vyše ob etimologiji možno pročitati v linkah v točkě 1.5.
Medžuslovjanska Besěda sbiraje mnogo različnyh ljudij, ale često sut to fanati jezykov, jezykoljubci i lingvisti.
Zato na tom serveru često sut dělajeme někake "lingvistične eksperimenty", kake mogut poněkogda izgledati čudno za ljudi kaki tut prihodet.
Medžuslovjansky ima prěd vsim byti razumlivy i my vsi to znajemo.
Naše eksperimenty sut dělane glavno zato aby tu razumlivost ulěpšati.
Vse veliko nerazumlive "standardy" imajut drugy cělj ili često sut ironične i sut jedino zasměški.
Daby uprostiti učenje jezyka novakam, kaki prihodžet na server jesmo ukryli eksperimentalne kanaly.
Ako li jeste interesovani tymi lingvističnymi eksperimentami tako možete idti vo kanal #deleted-channel i tam dodati odgovornu reakciju.
Na serveru pokušajemo tvoriti něčto, čto imenujemo Najvyše Razumlivym Standardom.
Razumlivost togo standarda jest v srědnom smyslu i znajemo, že medžuslovjansky ima mnogu kolikost variantov kaka jest koristna za govoriteljev.
Najvyše Razumlivy Standard jest hipotetičny variant medžuslovjanskogo jezyka kaky v srědnom smyslu jest najvyše razumlivy za najvysšu kolikost slovjanogovorečih ljudij voobče.
Preporučenja do Najvyše Razumlivogo Standarda sut v drugom kanalu (#deleted-channel) kaky jest dostupny za ljudi so rolju govoreči.
Ljudam so rolju učeči ne jest potrěbno měšati vo glavě, itak prosto prěporučajemo učiti se medžuslovjansky so osnovnyh iztokov, kake sut napisane vo prvoj poukě.
Dobra metoda učenja medžuslovjanskogo jezyka jest komunikacija so vyše izkušenymi govoriteljami, itak prizyvajemo vsih do učestvovanja vo besědah na glasovyh kanalah.
Medžuslovjansky jest jezyk kaky koristaje cělu bogatost slovjanskyh jezykov, daby dostaviti koristniku najvysšu možnu razumlivost. Jest to veliky pljus medžuslovjanskogo: samo tuto dělaje jezyk vyše prirodnym za vsakogo Slovjanina. Ale samo tuto takože iztvarjaje maly problem za ljudij kaki počeli koristati medžuslovjansky, zatože učeči medžuslovjanskogo mogut imati težky čas kogda dělo ide do izbora slov. Kako izbrati slovo kako bude razumlivo za najveliku možnu kolikost Slovjanov?
Najprvo, mnogo koristno bude prěgleděti naš fraznik (tutčas ješče pri njem rabotajemo)
Ako li fraznik ne byl mnogo pomočny v tutom slučaju, s velikoju věrojetnostju bude pomogti interaktivny slovnik medžuslovjanskogo za adresom https://interslavic-dictionary.com/
Daby najdti potrěbno slovo tam, jedino imajete njego dodati do iskalnogo reda. Možno, že slovnik bude dati dost veliku kolikost variantov za jedino slovo. Situacija izgledaje težko, ale slovnik ima mnogo dobru funkciju: vsako slovo iz rezultata iskanja bude imati klavišu kaka dozvoljaje prěgledati prěklady tutogo slova na druge slovjanske jezyky i izbrati najlěpši variant.
Poněkogda imamo problem, kogda sut několiko ravnyh variantov. Aby rěšiti tutoj problem, možno izkoristati dost banalnu věč: iskalnik diskorda na serveru.
Napriměr, hčemo najdti slovo za «thank you». Ako li prověriti slovo «dekuju», imamo jedino 56 rezultatov v iskalniku, ale ako li budemo gledeti na serveru slovo «hvala», možno primětiti, že imamo za njego 737 rezultatov. Dakle, vyše dobry variant može byti «hvala».
Ale, poněkogda sųt situacije kogda ne imamo někakoj leksiky v slovniku. Čto potrěbno dělati v tutom slučaju? Někaki Karuni za te slučaje koristajut znanu onlajn-enciklopedijų — wikipedia.org
Jedino potrěbno najdti v vikipedije članok. «Wikipedia» ima možnost glednuti verzije članka na drugyh jezykah i časom to mnogo pomogaje v izboru slov.
Prěgledali jeste vsě možlive varianty i vse ješče ničto ne razuměte i ne znajete kako slovo potrěbno koristati? Dobrodošli do #slověňský-словєньскъí! Može byti, v rěšenju tutogo pytanja vam budut pomogti drugi koristniki tutogo servera.
Jestvuje ješče opcija daby izkoristati sajt Wikidata. Napriměr:
    Hču prěklasti "cerebellum" na MS
    1) idu do Vikipediji: napr., na https://en.wikipedia.org/wiki/Cerebellum
    2) klikaju na "Wikidata item" (Element Vikidanyh)
    3) odvorjaju link: https://www.wikidata.org/wiki/130983
    4) gledaju na dol stranicy
    5) čitaju spis, išču slovjanske jezyky (to je zaisto najvyše komplikovana čest, zatože toj spis ima mnogo jezykov):
Daby pisati na medžuslovjanskom možno koristati mnogo različnyh klavjatur. Tuta pouka jest jih list.
Narodne klavjatury za latinsky alfabet:
Narodne klavjatury za kiriličsky alfabet:
Jestvujut takože specijalne klavjatury za kompjuterne sistemy:
razširjena MS latinica na medžunarodnyh latiničnyh klaviaturah (kako napriměr hrvatska v variantu unicodeus). Polna kiriličska klavjatura jest na standardnoj ukrainskoj klavjaturě.
V tom poslanju od Roberta jest mnogo informaciji itak tuta pouka jest jedino jego skračenje:
(pytanje 3 v tom poslanju)
""".split('\n')
EN_text = """Here is grammar course of Interslavic Language.
We recommend always using this Interslavic dictionary for learning words and grammar.
(Even the "oldest" speakers use it often)
If you need to switch text to the second alphabet (from cyrrilic to latin and vice versa), you can use this transliterator:
The dictionary shows the flexion of of words, and you can even find a certain word by using it's inflected variant, for example, there is no need to search for the word "dělati" ("to do"), but you may choose to look for "dělaju" ("I do"). 
What more: here are links to declinators and conjugators, which are useful for inflecting words that aren't in the Interslavic dictionary:
The extended etimological alphabet on Jan van Steenbergen's site:
Good document about the etimological pronounciation:
There is a trend to write in the etimological alphabet on this server.
It is not necessary.
You don't need to be upset if you don't know the etimological alphabet.
If something is hard for you, we recommend reading "the weird letters" as their closest, visual equivalent (ę is simply e, ć is č, đ is dž, ų jest u, å is a, and so on).
Here's also a quick lesson on cyrrilic letters:
You can read more about etimology in the links gived in lesson 1.5
Medžuslovjanska Besěda ("Interslavic Conversation") gathers a lot of different people, but they are often languages fanatics and linguists.
Because of this there often are certain "linguistic expermiments”, which can sometimes look weird for people who come here.
First of all, Interslavic is supposed understandable and we all know it.
Our experiments are done mainly to improve this understandability.
All not understandable „standards” have a different purpose, or are often ironic and are only jokes.
To simplify teaching the language to newcomers who come to the server, we have hidden the experimental channels.
If you’re interested in these linguistic experiments, you can enter the #rolje (roles) channel and add a reaction.
We try to create something we call the Most Understandable Standard on this server.
The understandability of this standard has a central meaning and we know that Interslavic has a lot of variants which are useful for speakers.
The Most Understandable Standard is a hypothetical variant of the Interslavic language, which, in the central sense, is generally the most understandable to the highest number of Slavic speakers.
Recommendations for the Most Understandable Standard are in another channel (#deleted-channel), which is available to people with the govoreči role.
There is no need to confuse people with the učeči, so we simply recommend learning Interslavic from basic sources, which are written in the first lesson.
A good method for learning the Interslavic languages is communication with more experienced speakers, so we invite you to participate in conversations in voice channels. 
Interslavic is a language which uses the richness of the Slavic languages to give the user the biggest possible understandability. It’s a big plus of Interslavic: just this makes the language more natural for every Slav. But this also creates a small problem for people who began using Interslavic, because Interslavic learners may have a hard time when it comes to choosing words. How does one choose a word that will be most understandable to the biggest possible number of Slavs?
First, many users will check our phrasebook (we’re still working on it)
If the phrasebook wasn’t very useful in this case, the interactive Interslavic dictionary with the adress https://interslavic-dictionary.com/ will surely help.
To find a word there, you simply have to add it to the searchbar. It is possible that the dictionary will give a lot of variants for a single word. The situation is looking bad, but the dictionary has a good function: each word from the results of the search will have a button which allows you to look up the translations of this word to other Slavic languages and choose the best option. 
Sometimes we have a problem when there are a few equal options. To solve this problem, you can use a pretty simple thing: the discord searchbar on this server.
For example, we want to find a word for "thank you". If we serch the word »dekuju«, we will only get 56 results, but if we will check the word »hvala«, we can see that we have 737 results for it. And so, the better variant can be »hvala«.
But sometimes there are situations when we don’t have a bit of lexicon in the dictionary. What does one do in such a situation? Some Karuni (Admins basically) use a known online encyclopedia — wikipedia.org.
All you need to do is find a Wikipedia article. Wikipedia has an option to check versions of the article in other languages and sometimes it helps in choosing words.
You have checked all possible variants, and still don’t understand anything and don’t know how to use a word? Welcome to #slověňský-словєньскъí! Other users can help you in answering this question.
You have also option to use the Wikidata. For instance:
    I'd like to translate "cerebellum" to Interslavic.
    1) I go to Wikipedia: e.g. to https://en.wikipedia.org/wiki/Cerebellum
    2) I click on "Wikidata item"
    3) I open a link: https://www.wikidata.org/wiki/130983
    4) I go to the bottom of the site
    5) I read the list, search for slavic languages (that's the most complicated part, cause the list has a lot of languages):
To write in Interslavic, you can use many different keyboard layouts. This lesson is a list of them.
There are also special layouts for computer systems:
    extended Interslavic latin on international latin layouts (for example Croatian in the unicodeus variant). The full cyrrylic keyboard is in the standard Ukrainian one.
There is a lot of information in this message made by Roberto , and so this lesson is simply a shorter version of it.
    (in Interslavic, question 3 in the message)
""".split("\n")

vectors1, vectors2 = [], []

lat_alphabet = "abcčdeěfghijjklmnoprsštuvyzž"
cyr_alphabet = "абцчдеєфгхийьклмнопрсштувызж"


cyr2lat_trans = str.maketrans(cyr_alphabet, lat_alphabet)
lat2cyr_trans = str.maketrans(lat_alphabet, cyr_alphabet)


def transliterate_lat2cyr(text):
    return text.translate(cyr2lat_trans)

print(len(ISV_text))
print(len(EN_text))
for line_isv, line_en in zip(ISV_text[:50], EN_text[:50]):
    # vectors1.append(model.encode(transliterate_lat2cyr(line_isv)))
    vectors1.append(model.encode(line_isv))
    vectors2.append(model.encode(line_en))

def get_sim_matrix(vec1, vec2, window=10):
    sim_matrix=np.zeros((len(vec1), len(vec2)))
    k = len(vec1)/len(vec2)
    for i in range(len(vec1)):
        for j in range(len(vec2)):
            if (j*k > i-window) & (j*k < i+window):
                sim = 1 - distance.cosine(vec1[i], vec2[j])
                sim_matrix[i,j] = sim
    return sim_matrix

sim_matrix = get_sim_matrix(vectors1, vectors2, window=50)

threshold = None
plt.figure(figsize=(6,5))
sbn.heatmap(sim_matrix, cmap="Greens", vmin=threshold)
plt.xlabel("interslavic", fontsize=9)
plt.ylabel("english", fontsize=9)
plt.show()


