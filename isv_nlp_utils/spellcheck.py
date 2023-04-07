from .constants import BASE_ISV_TOKEN_REGEX, ALPHABET_LETTERS, downgrade_diacritics
from .constants import DEFAULT_UNITS, ETM_DIACR_SUBS
# from .normalizacija import transliterate_cyr2lat
from .normalizacija import fix_text, convert2MSPlus

import argparse
import pymorphy2


def dodavaj_bukvy(word, etm_morph):
    corrected = [f.word for f in etm_morph.parse(word)]
    if len(set(corrected)) == 1:
        return corrected[0]
    if len(set(corrected)) == 0:
        return word + "/?"
    return "/".join(set(corrected))


def edit_distance_1(letters, word):
    """
    Compute all strings that are one edit away from `word` using only
    the letters in the corpus
    Args:
        word (str): The word for which to calculate the edit distance
    Returns:
        set: The set of strings that are edit distance one from the \
        provided word
    """

    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def create_set_if_known(word, morph):
    razbor = morph.parse(word)
    if not razbor:
        return set()
    diacr_form = razbor[0].word
    if morph.word_is_known(diacr_form):
        return {diacr_form}
    return set()


def spellcheck_text(
    paragraph, abeceda_name, morph,
    strict=True, consider_edit_distance=True, homonyms=True, treat_missing_diacritics_as_errors=True
):

    delimiters = BASE_ISV_TOKEN_REGEX.finditer(paragraph)
    proposed_corrections = []
    token_candidates_cache = {}
    for delim in delimiters:
        token = delim.group().lower()
        is_word = any(c.isalpha() for c in delim.group())
        is_correct = None
        corrected = None
        confident_correction = None
        add_info = []

        if is_word:
            candidates = set([f.word for f in morph.parse(token)])
            is_known = morph.word_is_known(token)
            is_correct = is_known

            # e.g. consider "čest": it is known, but
            # "čest" not in {česť, čęsť}
            if treat_missing_diacritics_as_errors and token not in candidates:
                is_correct = False
                add_info.append("D")

            # e.g. consider "česť": it is known and correct, but
            # there are two possible parses: {česť, čęsť}
            if homonyms and len(candidates) > 1:
                is_correct = False
                add_info.append("H")

            # what if adding diacritics is not enough to make word's spelling known?
            # for starters, we will not suggest diacritic-fixed variant as the solution

            # WARNING:
            # this will mess with the pymorphy2's ability to process unknown words by analogy:
            # e.g. "superkrasivoju" -> "superkrasivojų"
            if strict and not is_known:
                add_info.append(tuple(candidates))
                candidates = set()
            # secondly, let's attempt to fix that token
            if not is_known:
                for fixer_name, fixer_func in fix_text.items():
                    changed_token = fixer_func(token)
                    if changed_token not in token_candidates_cache:
                        local_candidates = set()
                        local_candidates |= create_set_if_known(changed_token, morph)
                        if consider_edit_distance:
                            near_tokens = edit_distance_1(
                                ALPHABET_LETTERS[abeceda_name], changed_token
                            )
                            for near_token in near_tokens:
                                local_candidates |= create_set_if_known(near_token, morph)
                        token_candidates_cache[changed_token] = local_candidates
                    candidates |= token_candidates_cache[changed_token]
            if len(set(candidates)) >= 1:
                corrected = "/".join(set(candidates))

        markup = "" if is_correct or not is_word else "^" * len(token)
        if corrected and corrected != token:
            proposed_corrections.append(corrected)
            confident_correction = corrected
            markup = str(len(proposed_corrections))
        span_data = (delim.start(), delim.end(), markup, add_info)
        yield span_data, confident_correction


def perform_spellcheck(text, abeceda_name, selected_morph):
    text = convert2MSPlus(text)
    if abeceda_name == "lat":
        text = text.translate(downgrade_diacritics)
    data = list(spellcheck_text(text, abeceda_name, selected_morph))
    spans = [entry[0] for entry in data if entry[0][2]]
    proposed_corrections = [entry[1] for entry in data if entry[1]]
    return text, spans, proposed_corrections


if __name__ == '__main__':
    from flake8.formatting.default import Default
    from flake8 import style_guide

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--homonyms', default=True, help=(
            """
            """
        )
    )
    parser.add_argument(
        '-s', '--suggest', action="count", default=0, help=(
            """Is it needed to suggest corrections for mistaken words? Affects performance."""
            """0 - Just output spelling problems"""
            """1 - Suggest diacritics"""
            """2 - Levenstein's distance of 1"""
        )
    )
    parser.add_argument(
        '-z', '--exit_zero',
        help="Always halt with the exit code 0 (even if there are spelling errors found)",
        default=False
    )
    parser.add_argument(
        '-p', '--path', help="path to DAWG dictionary files (a format that pymorphy2 uses)"
    )
    parser.add_argument(
        '-f', '--file', help="path to file that needs spellchecking"
    )
    namespace = parser.parse_args()

    etm_morph = pymorphy2.MorphAnalyzer(
        namespace.path+"out_isv_etm",
        units=DEFAULT_UNITS,
        char_substitutes=ETM_DIACR_SUBS
    )

    def options(**kwargs):
        """Create an argparse.Namespace instance."""
        kwargs.setdefault("output_file", None)
        kwargs.setdefault("format", 'default')
        return argparse.Namespace(**kwargs)

    formatter = Default(options=options())
    result_count = 0
    with open(namespace.file, 'r', encoding="utf8") as f:
        for i, line in enumerate(f):

            data = list(spellcheck_text(
                line, 'etm', etm_morph,
                strict=True,
                consider_edit_distance=namespace.suggest,
                homonyms=namespace.homonyms
            ))
            line_number = i + 1

            for entry in data:
                span = entry[0]
                word = line[span[0]: span[1]]
                proposed_correction = entry[1]
                error_type = span[2]
                add_data = span[3]
                if error_type:
                    result_count += 1
                    error_text = f"unknown word: {word}"
                    error_code = "E111"
                    if "H" in add_data and proposed_correction:
                        error_code = "H111"
                        error_text = f"possible homonym: {proposed_correction} for '{word}'"
                    if proposed_correction and len(proposed_correction.split("/")) == 1:
                        error_text = (
                            f"""unknown word: '{word}', have you meant '{proposed_correction}'?"""
                        )
                    error = style_guide.Violation(
                        error_code, namespace.file, line_number, span[0], error_text, line
                    )
                    print(formatter.format(error))

    if not namespace.exit_zero and result_count > 0:
        raise SystemExit(1)
