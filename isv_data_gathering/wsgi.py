from isv_nlp_utils.constants import create_analyzers_for_every_alphabet
from isv_translate import get_slovnik

from server import create_app

# Read-only file system
slovnik = get_slovnik(save=False)['words']
etm_morph = create_analyzers_for_every_alphabet("./")['etm']
app = create_app(etm_morph, slovnik)

