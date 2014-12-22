#!/bin/bash

GOLD=$1
awk ' { print $1 } ' $GOLD | perl -pe 's/^\n/JAR!!/g' | perl -pe 's/\n/ /g' | perl -pe 's/JAR!!/\n/g'
