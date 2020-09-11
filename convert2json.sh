#!/bin/bash

if [ $# -ne 1 ]
then
  echo "1 paraméter kötelező: input fájl (processed conll = sentskel)"
  exit 1;
fi

INPUTFILE=$1
INPUTLANG=$(basename $INPUTFILE)
# inputfile nevek kétbetűs nyelvazonosítók kellenek, hogy legyenek!

ODIR=json

OUTPUT=$(basename $INPUTFILE)

# 20 esetén már pár magyar ige is akad... :)
FQTH=20

cat $INPUTFILE | sed "s/.*stem@@//;s/ .*//" | sort | uniq -c | sort -nr | \
  awk -v fqth="$FQTH" '$1 >= fqth' | sed "s/^ *[0-9]* *//" \
  > $ODIR/${INPUTLANG}.verbs

for VERB in `cat $ODIR/${INPUTLANG}.verbs`
do
  cat $INPUTFILE | egrep "stem@@$VERB( |$)" | sed "s/stem@@$VERB *//" | \
    sed 's/^ *//;s/^\([0-9][0-9]*\)/{"fq": \1/;s/ @@[^ ][^ ]*//g;s/\([^ ][^ ]*\)@@\([^ ][^ ]*\)/, "\1": "\2"/g;s/$/}/;s/ *,/,/g;s/POSS//g' \
    > $ODIR/${INPUTLANG}_${VERB}.test.json
done

