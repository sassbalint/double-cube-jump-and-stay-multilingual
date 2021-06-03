#!/bin/bash

cat input/ns3s | grep -v "^#" | grep -v "	VERB	" | cols 3,6,8 | grep -v "Case=" | egrep -v "	(PREVERB|MODE|TO|LOCY|FROM|TTO|TLOCY|TFROM)" | sstat | sstat2tsv | colsort 4 | awk '$1 >= 10' | wcless > v ; vi -c ':set ts=32' v
