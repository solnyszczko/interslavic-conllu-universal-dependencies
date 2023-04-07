import regex
from copy import deepcopy

from ..constants import inflect_carefully
from .tokenizer import all_token_text_variants

def morphological_flavorise(tokens_data, morph, flavor_rules, debug_indices=set()):
    tokens_data = deepcopy(tokens_data)
    for i, token in enumerate(tokens_data):
        original = token.text[0]
        word = token.text[0].lower()
        if word in flavor_rules["SPECIAL_CASES"]:
            flavorised = flavor_rules["SPECIAL_CASES"][word]
            token.was_force_processed = True
        else:
            flavorised = flavorise(token.text[0].lower(), token.POS, morph, flavor_rules)
        token.text[0] = flavorised
        if original != flavorised and i in debug_indices:
            print(original, flavorised)
            # print(token)
    return tokens_data


def flavorise(word, golden_pos_tag, isv_morph, flavor):
    word = word.replace("đ", "dʒ")
    return __flavorise(word, golden_pos_tag, isv_morph, flavor).replace("dʒ", "đ")

def __flavorise(word, golden_pos_tag, isv_morph, flavor):
    if golden_pos_tag == "PNCT":
        return word
    if golden_pos_tag == "ADVB":
        variants = [
            v for v in isv_morph.parse(word)
            if v.tag.POS == "ADJF"
            and v.tag.number == "sing" and v.tag.gender == "neut" and v.tag.case == "nomn"
        ]
        if not variants:
            return word
    else:
        variants = [v for v in isv_morph.parse(word) if golden_pos_tag in v.tag]

    if not variants:
        return word

    verb_ju = flavor['INFLECTIONS'].get('verb-ju', None)
    if verb_ju is not None:
        if golden_pos_tag == "VERB" and all(v.tag.person == "1per" for v in variants):
            tags = variants[0].tag.grammemes  # no better way to choose
            if verb_ju:
                new_tags = set(tags) - {'V-m'} | {'V-ju'}
            else:
                new_tags = set(tags) - {'V-ju'} | {'V-m'}
            word = inflect_carefully(isv_morph, variants[0], new_tags)[0]

    if flavor['INFLECTIONS'].get('short-pronouns', True) == False:
        if golden_pos_tag == "NPRO" and all("form-short" in v.tag for v in variants):
            tags = variants[0].tag.grammemes  # no better way to choose
            new_tags = set(tags) - {'form-short'} | {'form-regl'}
            word = inflect_carefully(isv_morph, variants[0], new_tags)[0]

    if golden_pos_tag == "ADJF":
        variants = [variants[0]]  # no better way to choose

    flavor_rules = flavor.get(golden_pos_tag, {})
    if golden_pos_tag == "ADVB":
        flavor_rules = {"ADJF": flavor_rules.get('ADVB', (None, ''))}

    for condition_plus, transform in flavor_rules.items():
        if condition_plus == "":
            is_match = True
        else:
            conditions_arr = condition_plus.split("+")
            is_match = all(
                all(cond in v.tag for cond in conditions_arr)
                for v in variants
            )
        if is_match:
            if isinstance(transform, tuple):
                suffix, addition = transform
                return word[:suffix] + addition
            if isinstance(transform, dict):
                for base, replacement in transform.items():
                    if word[-len(base):] == base:
                        return word[:-len(base)] + replacement

    return word



def check_constraint(parse_variant, constraint):
    if parse_variant.was_force_processed:
        return False
    for single_constraint in constraint:
        if single_constraint[0] == "morphologyTags":
            if not parse_variant.features:
                return False
            conditions_arr = single_constraint[1].split("+")
            is_match = all(cond in parse_variant.features for cond in conditions_arr)
            if not is_match:
                return False
        if single_constraint[0] == "partOfSpeech":
            if not parse_variant.features:
                return False
            # TODO
            # allowed_pos = single_constraint[1].replace("noun", "n.,f.,m.").split(",")
            allowed_pos = single_constraint[1].split(",")
            allowed_pos = [p.strip() for p in allowed_pos]
            #if len(allowed_pos) > 1:
            #    print(allowed_pos)
            #    print(token.slovnik_pos)
            #    print(all(p not in token.slovnik_pos for p in allowed_pos), any(p in token.slovnik_pos  for p in allowed_pos))

            # TODO: https://github.com/medzuslovjansky/razumlivost/blob/main/src/customization/predicates/PartOfSpeechFilter.ts
            if all(p not in parse_variant.slovnik_pos for p in allowed_pos):
                return False
        if single_constraint[0] == "genesis":
            this_negated = "!" in single_constraint[1]
            this_approximate = "?" in single_constraint[1]
            this_value = single_constraint[1].strip("?!")
            unknown_genesis = (parse_variant.genesis != parse_variant.genesis) or not parse_variant.genesis
            does_apply = (parse_variant.genesis == this_value) or (this_approximate and unknown_genesis)

            # does_apply and this_negated -> False
            # not does_apply and not this_negated -> False
            if does_apply == this_negated:
                return False
    return True


def process_multireplacing(tokens_data, rules, debug_indices=set()):
    tokens_data = deepcopy(tokens_data)
    for rule in rules:
        #print(rule)
        name, typ = rule[:2]
        if "lowerCase" in typ:
            for i in range(len(tokens_data)):
                for j, v in enumerate(tokens_data[i].variants):
                    for k, w in enumerate(v.text_variants):
                        tokens_data[i].variants[j].text_variants[k] = w.lower()
        if "restoreCase" in typ:
            for i in range(len(tokens_data)):
                cap = tokens_data[i].capitalization
                if cap:
                    for j, v in enumerate(tokens_data[i].variants):
                        for k, w in enumerate(v.text_variants):
                            tokens_data[i].variants[j].text_variants[k] = w.title() if cap == "title" else w.upper()

        if typ == "r.map":
            if len(rule) == 3:
                mapping = rule[2]
                constraint = [("", "")]
            else:
                mapping = rule[2]
                constraint = rule[3]
                constraint = [(con_type, con_cond) for con_type, con_cond in constraint.asList()]

            for (a, b) in mapping:
                for i in range(len(tokens_data)):
                    prev_words = all_token_text_variants(tokens_data[i])
                    for j, v in enumerate(tokens_data[i].variants):
                        is_constraint_satisfied = check_constraint(v, constraint)
                        if not is_constraint_satisfied:
                            continue
                        for k, w in enumerate(v.text_variants):
                            tokens_data[i].variants[j].text_variants[k] = w.replace(a, b)

                    cur_words = all_token_text_variants(tokens_data[i])
                    has_notable_change = False
                    if i in debug_indices:
                        has_notable_change = set(cur_words) != set(prev_words)
                    if has_notable_change:
                        print(name)
                        print(prev_words, " => ", cur_words)

        if typ == "r.regexp":
            if len(rule) == 4:
                name, typ, pattern, subst = rule
                constraint = [("", "")]
            else:
                name, typ, pattern, subst, constraint = rule
                constraint = [(con_type, con_cond) for con_type, con_cond in constraint.asList()]
            subst = subst.asList()
            subst = [s.replace("$", "\\") for s in subst]
            pattern = pattern.replace("\x08", "$")
            try:
                compiled = regex.compile(pattern)
            except regex.error as e:
                print(e, "in", name)
                continue
            #if ("፨" in rule[2]):
            #    # if ("Stem" in name):
            #    raise NameError
            for i in range(len(tokens_data)):
                prev_words = all_token_text_variants(tokens_data[i])
                for j, v in enumerate(tokens_data[i].variants):
                    is_constraint_satisfied = check_constraint(v, constraint)
                    if not is_constraint_satisfied:
                        continue

                    prev_words = list(v.text_variants)
                    candidates = []
                    for k, w in enumerate(v.text_variants):
                        for one_subst in subst:
                            cand = compiled.sub(one_subst, w)
                            candidates.append(cand)
                    v.text_variants = list(set(candidates))
                if i in debug_indices:
                    cur_words = all_token_text_variants(tokens_data[i])
                    has_notable_change = set(cur_words) != set(prev_words)
                    if has_notable_change:
                        print(name)
                        print(prev_words, " => ", cur_words)

    return tokens_data
