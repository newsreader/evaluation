#!/bin/sh
#sh prepare_SRL_ref_files.sh corpus_CAT_ref corpus_CoNLL_output corpus_CoNLL_ref

BASEDIR=$(dirname $0)
#echo $BASEDIR

for entry in "$1"*
do
    #echo "$entry"
    fname=`basename $entry`

    ####fnameConll=$(echo $fname | sed -E -e "s/(\.txt)?\.xml/.naf.conll/")
    #fnameConll=$(echo $fname | sed -E -e "s/\.naf\.naf/\.naf.conll/")
    #fnameConll=$(echo $fname)
    #echo "$fnameConll"
    
    #python "$BASEDIR"/CAT_to_evaluation_formats.py "$entry" SRL /tmp/ #
    #python "$BASEDIR"/CAT_to_evaluation_formats.py "$entry" SRL /tmp/"$fname"
    
    #paste temp_event temp_event_2 >"$2""$fname"
    ####cut -f 1-12 <"$2""$fnameConll" >/tmp/srl_syst
    #echo $2$fname
    cut -f 1-12 <"$2""$fname" >/tmp/srl_syst
    #cut -f 13- </tmp/"$fnameConll" >/tmp/srl_gold #
    cut -f 13- <"$entry" >/tmp/srl_gold
    ####paste /tmp/srl_syst /tmp/srl_gold >"$3""$fnameConll"
    paste /tmp/srl_syst /tmp/srl_gold >"$3""$fname"

    #rm /tmp/"$fnameConll"
    rm /tmp/srl_syst
    rm /tmp/srl_gold

done

