#!/bin/bash

RAWTEST=$1
NERCMODEL=$2

cat $RAWTEST | java -jar ~/javacode/ixa-pipe-tok/target/ixa-pipe-tok-1.7.0.jar tok -l en --notok | java -jar ~/javacode/ixa-pipe-pos/target/ixa-pipe-pos-1.3.3.jar tag -m ~/javacode/ixa-pipe-pos/pos-models-1.3.0/en/en-maxent-100-c5-baseline-dict-penn.bin | java -jar ~/javacode/ixa-pipe-nerc/target/ixa-pipe-nerc-1.3.3.jar tag -m $NERCMODEL -o conll03