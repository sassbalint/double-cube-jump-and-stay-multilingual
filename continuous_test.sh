#!/bin/bash

if [ "$1" == "small" ]
then
    DATA1=ns30
    VERB1=játszik
    SUBJ1=Nom

    DATA2=hu
    VERB2=kerül
    SUBJ2=nsubj
else
    DATA1=ns3s
    VERB1=megmutat
    SUBJ1=Nom

    DATA2=de
    VERB2=schreiben
    SUBJ2=nsubj
fi

make INPUTLANG=$DATA1 SUBJECT_SLOT=$SUBJ1
make INPUTLANG=$DATA2 SUBJECT_SLOT=$SUBJ2

rm -f result/*out3

echo
echo -n "    >>> "
diffvi result_backup result

echo
echo "--- $DATA1 / $VERB1"
cat result/${DATA1}_$VERB1.test.out3.pVCC

echo
echo "--- $DATA2 / $VERB2"
cat result/${DATA2}_$VERB2.test.out3.pVCC

