#!/bin/sh

path=`pwd`
BASEDIR=$(dirname $0)

cd $(echo $BASEDIR)

for entry in "$path"/"$1"*
do
    echo "$entry"
    fname=`basename $entry`
    fnameb=$fname
    fnameb=$(echo $fnameb | sed -e "s/\.naf//")
    java -cp "lib/jdom-2.0.5.jar:lib/kaflib-naf-1.1.8.jar:NAFtoCAT.jar" eu.fbk.newsreader.naf.NAFtoCAT "$entry" "$path"/"$2""$fnameb".xml
done
