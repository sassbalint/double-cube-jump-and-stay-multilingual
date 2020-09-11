#!/bin/bash

if [ $# -ne 1 ]
then
  echo "1 paraméter kötelező: input fájl (conll treebank)"
  exit 1;
fi

INPUTFILE=$1
INPUTLANG=$(basename $INPUTFILE)
# inputfile nevek kétbetűs nyelvazonosítók kellenek, hogy legyenek!

ODIR=mazsdb

BASE=$(basename $INPUTFILE)

O1=${BASE}.verbose
O2=${BASE}

python3 ./process_conll.py $INPUTFILE $INPUTLANG > $ODIR/$O1
cat $ODIR/$O1 | grep "stem@@" | sed "s/ _@@[^ ][^ ]*//g" | sort | uniq -c | sort -nr > $ODIR/$O2

