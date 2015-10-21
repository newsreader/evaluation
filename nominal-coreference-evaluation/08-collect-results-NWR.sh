#!/bin/bash 

echo "==== MUC ====\n"
cat $1/*.muc.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > $2/muc.csv
cat $2/muc.csv | awk -F',' '{sum+=$3; ++n} END { print "MUC Avg: "sum"/"n"="sum/n }'

echo "==== BCUB ====\n"
cat $1/*.bcub.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' >$2/bcub.csv
cat $2/bcub.csv | awk -F',' '{sum+=$3; ++n} END { print "BCUB Avg: "sum"/"n"="sum/n }'

echo "==== CEAFE ====\n"
cat $1/*.ceafe.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' >$2/ceafe.csv
cat $2/ceafe.csv | awk -F',' '{sum+=$3; ++n} END { print "CEAFE Avg: "sum"/"n"="sum/n }'
