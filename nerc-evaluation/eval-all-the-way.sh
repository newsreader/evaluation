#!/bin/sh

GOLD=$1
NERCMODEL=$2
CONLLEVAL=$3

awk ' { print $1 } ' $GOLD | perl -pe 's/^\n/JAR!!/g' | perl -pe 's/\n/ /g' | perl -pe 's/JAR!!/\n/g' | java -jar ~/javacode/ixa-pipe-tok/target/ixa-pipe-tok-1.8.3.jar tok -l en --notok | java -jar ~/javacode/ixa-pipe-pos/target/ixa-pipe-pos-1.4.5.jar tag -m ~/javacode/ixa-pipe-pos/pos-models-1.4.0/en/en-maxent-100-c5-baseline-dict-penn.bin | java -jar ~/javacode/ixa-pipe-nerc/target/ixa-pipe-nerc-1.5.3.jar tag -m $NERCMODEL -o conll03 | awk ' { print $NF } ' | paste - $GOLD | awk ' { print $2" "$NF" "$1 } ' | perl -pe 's/\t//g' | sed 's/B-/I-/g' | perl $CONLLEVAL

