#!/bin/bash
GOLDDIR=$1
for i in $GOLDDIR/*.key; do time cat $i | sed '/^#/d' | awk ' { print $4 } ' | perl -pe 's/^\n/JAR!!/g' | perl -pe 's/\n/ /g' |  perl -pe 's/JAR!!/\n/g' > $i.txt ; done
