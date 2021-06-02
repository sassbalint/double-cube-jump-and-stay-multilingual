import csv
import sys

ID     = 0
FORM   = 1
LEMMA  = 2
UPOS   = 3
XPOS   = 4
FEATS  = 5
HEAD   = 6
DEPREL = 7
DEPS   = 8
MISC   = 9
FEATS_DIC = 10
SLOT   = 11 # ezt én teszem hozzá a FEATS-ból kiszedve

ITEM_SEP     = '|'
FEAT_VAL_SEP = '=' # v2.4: '='
#FEAT_VAL_SEP = '_' # v2.0: '_'

NOSLOT = '_'

# ----- trükkök az annotáció jobbítására

VERB_PARTICLE = [ 'compound:prt', 'compound:preverb', 'PREVERB' ] # utóbbi a magyar...

# a többi nyelvnél tán nem kell (cs, hu: kifejezetten rossz)
XCOMP_PARTICLE = { 
  'de': 'zu',
  'en': 'to',
  'no': 'å'
}

# innen: http://fluentu.com/blog/german/german-contractions
DE_CONTRACTIONS = {
  'am': 'an', 'ans': 'an', 'aufs': 'auf', 'beim': 'bei',
  'durchs': 'durch', 'fürs': 'für', 'hinterm': 'hinter',
  'ins': 'in', 'im': 'in', 'übers': 'über', 'ums': 'um',
  'unters': 'unter', 'unterm': 'unter',
  'vom': 'von', 'vors': 'vor', 'vorm': 'vor', 'zum': 'zu', 'zur': 'zu'
}

PRON_LEMMAS = [ # nincs annot! = csak lemma alapján megy
  'navzájem', # cs
  'sich', 'einander', # de
  # en(each other) ??? XXX XXX XXX
  'birbiri', # tr
]

# ----- trükkök vége

def print_token( t ):
  print( t[ID], t[FORM], t[LEMMA], t[UPOS], t[XPOS],
         t[FEATS], t[HEAD], t[DEPREL] )

# olvassuk be mondatonként
# for szavak: ha ige, írjuk ki a közvetlen bővítményeinek megfelelő infóit

if len( sys.argv ) != 3:
  print( "Usage: python3 ./" + sys.argv[0] + " conll_inputfile 2_letter_language_code" )
  sys.exit( 1 )

filename = sys.argv[1]

INPUTLANG = None
if ( sys.argv[2] ):
  INPUTLANG = sys.argv[2]

with open( filename ) as fd:
  rd = csv.reader( fd, delimiter="\t", quoting=csv.QUOTE_NONE ) # nincs quoting!
  sent = [] # mondat
  for row in rd:
    if len(row) == 1 and row[0][0] == "#": # comment
      continue
    if row: # ha nem üres sor => egy token feldolgozása

      # feats -> feats_dic
      feats = row[FEATS]
      if feats == '_':
        feats_dic = {}
      else:
        try:
          feats_dic = dict( ( x, y )
            for x, y in ( e.split( FEAT_VAL_SEP, 1 )
            for e in feats.split( ITEM_SEP ) ) )
        except ValueError:
          print( "FATAL: " + feats + ' :: {' + '}{'.join( row ) + '}' )
          exit( 1 )
      print( sorted( feats_dic ) )

      # feats_dic -> "slot" megállapítása + hozzárakása
      slot = NOSLOT
      # 0. alap dependenseket az elejére vesszük :)
      if row[DEPREL] in [ 'nsubj', 'obj', 'iobj', 'obl' ]:
        slot = row[DEPREL]
      # 1. ha nincs: a 'Case' feat már tök jó :) -- XXX tutira kell külön?
      elif 'Case' in feats_dic:
        slot = feats_dic['Case']
      # 2. ha nincs: egyéb deprel = minden innen: http://ud.org/u/dep
      elif row[DEPREL] in [
        # -- #1 oszlop
        'case',
        # 'vocative', 'expl', 'dislocated', 'nmod', 'appos', 'nummod',
        # -- #2 oszlop
        # 'csubj', 'ccomp',
        'xcomp',
        # 'advcl', 'acl',
        # -- #3 oszlop
        # 'advmod', 'discourse', 'amod',
        # -- #4 oszlop
        # 'aux', 'cop', 'mark', 'det', 'clf'
        #
        # -- e-magyar révén
        #'INF'
      ]:
        slot = row[DEPREL]
      ## 3. ha az sincs, akkor esetleg még szófaj alapon :)
      #elif row[UPOS] in [ 'ADV' ]: # ha ez sincs, akkor hozzá: 'ADV'
      #  slot = row[UPOS]
      ## az első magyar tesztek alapján: inkább ne legyen ADV! :)

      row.append( feats_dic ) # ez pontosan a 10-es (11.) mező legyen!
      row.append( slot )     # ez pontosan a 11-es (12.) mező legyen!
      sent.append( row )

    else: # üres sor = mondat vége => teljes mondat feldolgozása

      for tok in sent:
        print_token( tok )

        if tok[UPOS] == 'VERB':
          verb_lemma = tok[LEMMA]

          deps = []
          # ige bővítményei
          # XXX ciklusok helyett: vmi jobb (dict?) adatszerk itt! :)
          for dep in sent: # ige közvetlen bővítményei
            # XXX alább esetleg (debug!) a NOSLOT-t is meg lehet engedni...
            if dep[HEAD] == tok[ID] and dep[XPOS] != 'Punct' and dep[SLOT] != NOSLOT:
              slot = dep[SLOT]
              # bővítmény bővítményei = elöljárók berakása
              for depofdep in sent:
                if ( depofdep[HEAD] == dep[ID] and (
                     depofdep[UPOS] == 'ADP' or (
                       depofdep[UPOS] == 'PART' and
                       INPUTLANG in XCOMP_PARTICLE and
                       depofdep[LEMMA] == XCOMP_PARTICLE[INPUTLANG]
                     ) ) ):
                  prep = depofdep[LEMMA].lower()
                  # 'de': német kontrakciók kezelése: am -> an :)
                  if INPUTLANG == 'de' and prep in DE_CONTRACTIONS:
                    prep = DE_CONTRACTIONS[prep]
                  slot += '=' + prep
              # lemma -- névmások kezelése -- csak ez kell: 'maga', 'egymás'
              lemma = dep[LEMMA].lower() if (
                dep[UPOS] != 'PRON' or
                dep[FEATS_DIC].get( 'Reflex', 'notdef' ) == 'Yes' or # 'maga'
                dep[FEATS_DIC].get( 'PronType', 'notdef' ) == 'Rcp' or # 'egymás'
                dep[LEMMA] in PRON_LEMMAS ) else "NULL"
              deps.append( slot + '@@' + lemma )
            # ik hozzáadása
            elif dep[HEAD] == tok[ID] and dep[DEPREL] in VERB_PARTICLE:
              verb_lemma = dep[LEMMA] + verb_lemma
              
          # ige (+ik!) kiírása
          # '+'-t le kell cserélni, mert csak a magyarban így van: ik+ige
          print( 'stem@@' + verb_lemma.replace( '+', ''), end='' )
          # bővítmények kiírása -- betűrendben
          for x in sorted(deps):
            print( '', x, end='' )
          print()

      print( "\n-----\n" )
      sent = []

