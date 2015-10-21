#!/bin/bash 

echo "==== BLANC ====\n"
cat $1/*.blanc.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' >$2/blanc.csv
cat $2/blanc.csv | awk -F',' '{sum+=$3; ++n} END { print "BLANC Avg: "sum"/"n"="sum/n }'
