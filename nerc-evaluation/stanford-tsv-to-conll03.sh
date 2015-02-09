#!/bin/bash

file=$1
cat $file |sed 's/PERSON/I-PER/g' | sed 's/LOCATION/I-LOC/g' | sed 's/ORGANIZATION/I-ORG/g' | sed 's/MISC/I-MISC/g' | sed 's/\t/ /g' 