#!/bin/bash

folder=$1

for i in $folder/*; do cat $i | perl -pe 's/^\n/JAR!!/g' | perl -pe 's/\n/ /g' | perl -pe 's/JAR!!/\n/g' | head -n 6 | perl -pe 's/ /\n/g' | perl -pe 's/[BI]-MISC/O/g' > $i.five ; done
