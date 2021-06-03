
"""
This module creates "functional annotation"
from a CoNLL(-like) treebank.
That is: creates a Mazsola-like database
from verbs and their direct exts.
(ext in {dependent, argument, complement, adjunct})
"""


import argparse
import csv
import sys


# CoNLL fields -- last two added by this module
(ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC,
 FEATS_DIC, SLOT) = range(12)

FEAT_ITEM_SEP = '|'
FEAT_VAL_SEP = '=' # UD v2.4: '=' <--> UD v2.0: '_'

NOSLOT = '_'

ROOT_UPOS = 'VERB'


# ----- language specific tricks to improve annotation

VERB_PARTICLE = [
    'compound:prt', 'compound:preverb', # UD
    'PREVERB' # e-magyar
]

# maybe not needed for other languages (surely not needed for cs and hu)
XCOMP_PARTICLE = {
    'de': 'zu',
    'en': 'to',
    'no': 'å'
}

# from http://fluentu.com/blog/german/german-contractions
DE_CONTRACTIONS = {
    'am': 'an', 'ans': 'an', 'aufs': 'auf', 'beim': 'bei',
    'durchs': 'durch', 'fürs': 'für', 'hinterm': 'hinter',
    'ins': 'in', 'im': 'in', 'übers': 'über', 'ums': 'um',
    'unters': 'unter', 'unterm': 'unter',
    'vom': 'von', 'vors': 'vor', 'vorm': 'vor', 'zum': 'zu', 'zur': 'zu'
}

PRON_LEMMAS = [ # based directly on lemma
    'navzájem', # cs
    'sich', 'einander', # de
    # en(each other) ??? XXX XXX XXX
    'birbiri', # tr
    #'maga', 'egymás' # hu -- is this needed for e-magyar annotation?
]

# ----- end of tricks


def print_token(t):
    print(' '.join(t[ID:DEPS]))


def main():
    """
    Process sentences.
    Take verbs and output them together with info on their direct exts.
    """
    args = get_args()
    filename = args.input_file
    INPUTLANG = args.language

    with open(filename) as fd:
        rd = csv.reader(fd, delimiter="\t", quoting=csv.QUOTE_NONE) # no quoting
        sentence = []
        for row in rd:
            if len(row) == 1 and row[0][0] == "#": # comment line
                continue
            if row: # line is not empty => process this token

                # feats -> feats_dic (specific format -> python data structure)
                feats = row[FEATS]
                if feats == '_':
                    feats_dic = {}
                else:
                    try:
                        feats_dic = {x: y
                            for x, y in (e.split(FEAT_VAL_SEP, 1)
                            for e in feats.split(FEAT_ITEM_SEP))}
                    except ValueError:
                        print("FATAL: " + feats + ' :: {' + '}{'.join(row) + '}')
                        exit(1)
                print(sorted(feats_dic))

                # determine "slot" = the category of the word as an ext
                slot = NOSLOT

                # 0. basic arguments
                #    * UD: we need them here because 'Case' feature is mostly missing
                #    * e-magyar: this step is not needed as we always have 'Case' feature
                if row[DEPREL] in ['nsubj', 'obj', 'iobj', 'obl']:
                    slot = row[DEPREL]

                # 1. if not present: take the 'Case' feature
                #    * UD: needed
                #    * e-magyar: this is the main info on category
                elif 'Case' in feats_dic:
                    slot = feats_dic['Case']

                # 2. if not present: other deprel
                #    * UD: case, xcomp <- http://ud.org/u/dep
                #    * e-magyar: INF
                elif row[DEPREL] in [ 'case', 'xcomp',
                    #'INF',
                ]:
                    slot = row[DEPREL]

                ## 3. if not present: maybe based on part of speech
                ## UPOS = 'ADV' -- omitted based on experiments on Hungarian

                row.append(feats_dic) # 11th field
                row.append(slot)      # 12th field

                sentence.append(row)

            else: # empty line = end of sentence => process the whole sentence

                for tok in sentence:
                    print_token(tok)

                    if tok[UPOS] != ROOT_UPOS:
                        continue

                    # we have the root (=VERB) here
                    verb_lemma = tok[LEMMA]

                    deps = []
                    # exts of the verb -- with simple loops (not slow)
                    for dep in sentence: # direct exts
                        if dep[HEAD] != tok[ID]:
                            continue
                        if dep[SLOT] != NOSLOT:
                            slot = dep[SLOT]
                            # exts of the exts = amend slot with prepositions/postpositions
                            for depofdep in sentence:
                                if depofdep[HEAD] != dep[ID]:
                                    continue
                                if (depofdep[UPOS] == 'ADP' or (
                                    depofdep[UPOS] == 'PART' and
                                    INPUTLANG in XCOMP_PARTICLE and
                                    depofdep[LEMMA] == XCOMP_PARTICLE[INPUTLANG]
                                )):
                                    prep = depofdep[LEMMA].lower()
                                    # 'de': handle german contractions: am -> an
                                    if INPUTLANG == 'de' and prep in DE_CONTRACTIONS:
                                        prep = DE_CONTRACTIONS[prep]
                                    slot += '=' + prep
                            # lemma
                            lemma = dep[LEMMA].lower()
                            # lemma / handle pronouns
                            # -- only reflexive and rcp are needed as lemma
                            if (dep[UPOS] == 'PRON' and
                                dep[FEATS_DIC].get('Reflex', 'notdef') != 'Yes' and # 'itself'
                                dep[FEATS_DIC].get('PronType', 'notdef') != 'Rcp' and # 'each other'
                                dep[LEMMA] not in PRON_LEMMAS
                            ):
                                lemma = "NULL"
                            deps.append(slot + '@@' + lemma)
                        # add verb particle / preverb to the verb lemma
                        # verb particle / preverb must be a NOSLOT!
                        elif dep[DEPREL] in VERB_PARTICLE:
                            verb_lemma = dep[LEMMA] + verb_lemma

                    # handle special 'perverb+verb' format in UD/hu -> delete the '+'
                    verb_lemma = verb_lemma.replace('+', '')

                    # print out the verb centered construction
                    # = verb + exts (in alphabetical order)
                    for x in ['stem@@' + verb_lemma] + sorted(deps):
                        print('', x, end='')
                    print()

                print("\n-----\n")
                sentence = []


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # string-valued argument
    parser.add_argument(
        '-i', '--input-file',
        help='CoNLL(-like) input file',
        required=True,
        type=str,
        default=argparse.SUPPRESS
    )
    # string-valued argument
    parser.add_argument(
        '-l', '--language',
        help='2-letter language code for language specific tricks',
        required=True,
        type=str,
        default=argparse.SUPPRESS
    )

    return parser.parse_args()


if __name__ == '__main__':
        main()
