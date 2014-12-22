#!/bin/bash

PREDICTION=$1
REFERENCE=$2
awk ' { print $NF } ' $PREDICTION | paste - $REFERENCE | awk ' { print $2" "$NF" "$1 } ' | perl -pe 's/\t//g'
