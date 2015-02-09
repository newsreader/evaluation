#!/bin/bash

file=$1
cat $file | awk ' { print $1"\t"$2 } ' | sed 's/I-PER/PERSON/g' | sed 's/I-LOC/LOCATION/g' | sed 's/I-ORG/ORGANIZATION/g' | sed 's/B-PER/PERSON/g' | sed 's/B-LOC/LOCATION/g' | sed 's/B-ORG/ORGANIZATION/g'