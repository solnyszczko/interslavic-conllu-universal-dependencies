import argparse
from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS, cross_origin
import pymorphy2
from isv_nlp_utils.constants import create_analyzers_for_every_alphabet
from isv_nlp_utils.spellcheck import perform_spellcheck
import time

from translation_aux import LANGS
from isv_translate import translate_sentence, translation_candidates_as_html, get_slovnik, prepare_parsing, postprocess_translation_details


def create_app(etm_morph, slovnik):
    """Create and configure an instance of the Flask application."""
    # TODO: fix diacritics in slovnik
    etm_morph.char_substitutes['e'.encode()] = ("ė".encode(), 'ė')
    print(etm_morph.char_substitutes)

    app = Flask(__name__)
    cors = CORS(app)
    app.config["JSON_AS_ASCII"] = False
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route('/<lang>/<text>', methods=['GET'])
    def as_html(lang, text):
        lang, _, postfix = lang.partition("_")
        if lang not in LANGS or postfix not in {"", "debug"}:
            abort(404)

        parsed = prepare_parsing(text, lang)
        if lang == "ru_slovnet":
            lang = "ru"
        debug_details = translate_sentence(parsed, lang, slovnik, etm_morph)
        html = translation_candidates_as_html(debug_details)
        if postfix == 'debug':
            html += debug_details.to_html()
        return html

    @app.route('/api/', methods=['POST'])
    def as_json():
        text = request.json['text']
        lang = request.json['lang']
        if lang not in LANGS:
            abort(404)

        parsed = prepare_parsing(text, lang)
        translation_details = translate_sentence(parsed, lang, slovnik, etm_morph)
        result = {"translation": postprocess_translation_details(translation_details)}
        if request.json.get("debug"):
            result['details'] = translation_details.to_json()

        return jsonify(result)
 
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
       '--port', type=int, default=2901,
       help='The port to listen on (defaults to 2901).')
    parser.add_argument(
        '-p', '--path', help="path to DAWG dictionary files (a format that pymorphy2 uses)",
        default="./"
    )
    args = parser.parse_args()
    slovnik = get_slovnik()['words']
    etm_morph = create_analyzers_for_every_alphabet(args.path)['etm']

    app = create_app(etm_morph, slovnik)

    app.run(host='localhost', port=args.port, debug=True)

