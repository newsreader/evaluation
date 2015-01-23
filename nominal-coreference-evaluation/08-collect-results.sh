#!/bin/bash 

cat corefgraph-conll-wikinews/corpus_airbus/*.muc.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/muc/airbus-muc.csv
cat corefgraph-conll-wikinews/corpus_apple/*.muc.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/muc/apple-muc.csv
cat corefgraph-conll-wikinews/corpus_gm_chrysler_ford/*.muc.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/muc/gm-muc.csv
cat corefgraph-conll-wikinews/corpus_stock_market/*.muc.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/muc/stock-muc.csv
cat corefgraph-conll-wikinews/muc/*.csv | awk -F',' '{sum+=$3; ++n} END { print "MUC Avg: "sum"/"n"="sum/n }'

cat corefgraph-conll-wikinews/corpus_airbus/*.bcub.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/bcub/airbus-bcub.csv
cat corefgraph-conll-wikinews/corpus_apple/*.bcub.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/bcub/apple-bcub.csv
cat corefgraph-conll-wikinews/corpus_gm_chrysler_ford/*.bcub.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/bcub/gm-bcub.csv
cat corefgraph-conll-wikinews/corpus_stock_market/*.bcub.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/bcub/stock-bcub.csv
cat corefgraph-conll-wikinews/bcub/*.csv | awk -F',' '{sum+=$3; ++n} END { print "BCUB Avg: "sum"/"n"="sum/n }'

cat corefgraph-conll-wikinews/corpus_airbus/*.ceafe.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/ceafe/airbus-ceafe.csv
cat corefgraph-conll-wikinews/corpus_apple/*.ceafe.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/ceafe/apple-ceafe.csv
cat corefgraph-conll-wikinews/corpus_gm_chrysler_ford/*.ceafe.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/ceafe/gm-ceafe.csv
cat corefgraph-conll-wikinews/corpus_stock_market/*.ceafe.result | sed -r '/(^Coreference)/!d' | awk ' { print $6","$11","$13 } ' > corefgraph-conll-wikinews/ceafe/stock-ceafe.csv
cat corefgraph-conll-wikinews/ceafe/*.csv | awk -F',' '{sum+=$3; ++n} END { print "CEAFE Avg: "sum"/"n"="sum/n }'