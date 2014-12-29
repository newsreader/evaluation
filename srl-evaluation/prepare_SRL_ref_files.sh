#!/bin/sh
#sh prepare_SRL_ref_files.sh corpus_CAT_ref corpus_CoNLL_output corpus_CoNLL_ref

for entry in "$1"*
do
    echo "$entry"
    fname=`basename $entry`

    fnameConll=$(echo $fname | sed -E -e "s/(\.txt)?\.xml/.conll/")
    echo "$fnameConll"
    
    python CAT_to_evaluation_formats.py "$entry" SRL | cat > /tmp/"$fname"
    
    #paste temp_event temp_event_2 >"$2""$fname"
    cut -f 1-12 <"$2""$fnameConll" >/tmp/srl_syst
    cut -f 13- </tmp/"$fname" >/tmp/srl_gold
    paste /tmp/srl_syst /tmp/srl_gold >"$3""$fnameConll"

done

