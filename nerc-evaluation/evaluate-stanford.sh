#!/bin/bash

model=$1
file=$2
java -cp stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier $model -testFile $file
