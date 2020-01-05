#!/bin/bash

for i in result/??_*pVCC
do
  j=$(basename $i | sed "s/\.test\.out3\.pVCC/	/")
  cat $i | sed "s/^/$j/"
done | sort -t '	' -k3,3nr > full_freq_list

