from .parsing import parse_multireplacer_rules
from .tokenizer import compute_annotated_tokens
from .replacer import process_multireplacing, morphological_flavorise
# from .selector import select_randomly, select_lingua

from isv_nlp_utils import constants
from isv_nlp_utils.slovnik import get_slovnik
# from isv_translate import translate_sentence, postprocess_translation_details, prepare_parsing

from ast import literal_eval
import os
import glob


if __name__ == "__main__":
    Src = (
        "každy ščęstlivy pės uměje graciozno padati v ćuđų, hlådnų vodų: vzęti rybu fugu iz vȯzduha. Hćų prěporųčiti: ględi pěše Troicky most v grådu Čeljabinsku, žęđam foto za ženų. " + 
        "Kromě togo, kȯgda sědite v problematikě MS, v glåvě sę vam skladaje taky sistem kako maly domȯk iz kostȯk Lego. V mojej glåvě jest po tutom principu vȯznikla bogatějša forma MS, ktorų råboće, sam za sebę, nazyvajų srědnoslovjańsky. Čisty MS jest posvęćeny ljud́am i komunikaciji, zato trěbuje byti universaĺno råzumlivy tako mnogo, kako jest možno. Iz drugoj stråny bogatějši međuslovjańsky, teoretično upotrěblivy v literaturě ili pěsnjah, jest na tutčas glåvno za prijateljev językov. K drugym ljud́am on ne progovori, zatože on v sobě imaje bogat́stvo vsih slovjańskyh językov, a vśaky slovjańskojęzyčny člověk znaje jedino tų čęst́, ktorų v sobě imaje jegovy język."
    )

    slovnik = get_slovnik()
    slovnik = slovnik['words']

    morph = constants.create_etm_analyzer(r"C:\dev\ISV_data_gathering\\")

    for LANG in [os.path.basename(l).partition(".")[0] for l in glob.glob(r"C:\dev\razumlivost\src\flavorizers\*.ts")]:

        if LANG == "index":
            continue
        print(LANG)
        rules_struct = parse_multireplacer_rules(
            r"C:\dev\razumlivost\src\flavorizers\{}.ts".format(LANG)
        )

        try:
            with open(r"C:\dev\razumlivost\src\flavorizers\morpho_{}.txt".format(LANG), "r", encoding="utf8") as f:
                flavor_rules = literal_eval(f.read())
            # TODO: store `ju` in file
            ju = True
        except FileNotFoundError:
            print("no morphology for " + LANG)
            flavor_rules = None
            ju = None
            pass

        tokens = compute_annotated_tokens(Src, morph, slovnik)
        if flavor_rules:
            morphological_flavorise(tokens, morph, flavor_rules, ju)
        res = process_multireplacing(tokens, rules_struct)
        print(res)
        # print(tokens)

