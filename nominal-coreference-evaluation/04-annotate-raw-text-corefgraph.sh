#!/bin/bash
RAWTESTDIR=$1
NERCMODEL=$2

for i in $RAWTESTDIR/*.txt; do time cat $i | java -jar ~/javacode/ixa-pipe-tok/target/ixa-pipe-tok-1.6.6.jar tok -l en --notok | java -jar ~/javacode/ixa-pipe-pos/target/ixa-pipe-pos-1.3.2.jar tag -m ~/javacode/ixa-pipe-pos/pos-models-1.3.0/en/en-maxent-100-c5-baseline-dict-penn.bin | java -jar ~/javacode/ixa-pipe-nerc/target/ixa-pipe-nerc-1.3.3.jar tag -m ~/javacode/ixa-pipe-nerc/target/ixa-pipe-nerc-1.3.3.jar -m $NERCMODEL | java -jar ~/javacode/ixa-pipe-parse/target/ixa-pipe-parse-1.0.2.jar parse -g sem | python -m corefgraph.process.file --reader NAF --writer NAF --singleton > $i.naf ; done
