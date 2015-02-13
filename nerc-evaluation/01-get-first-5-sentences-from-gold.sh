#!/bin/bash

folder=$1

for i in $folder/*; do time cat $i | perl -pe 's/^\n/JAR!!/g' | perl -pe 's/\n/ /g' | perl -pe 's/JAR!!/\n/g' | head -n 6 | perl -pe 's/ /\n/g' > $i.five ; done
