
Named Entity Recognition and Classification: Evaluation
=======================================================

The evaluation of the Named Entity Recognition and Classification (NERC)
systems is usually done following the CoNLL 2002 and CoNLL 2003 shared tasks
methodology. Those tasks also distribute an official evaluation script which we
will be using to evaluate the performance of the NERC taggers in the Newsreader
pipeline. 

In this folder you can find the scripts necessary to evaluate a NERC tagger
system's output, provided you have the gold standard or reference corpus in
CoNLL 2002 format.

## STEPS

1. **Extract raw test data** from gold standard by executing 

````shell
01-get-text-from-gold-conll.sh wiki-news-gold.conll02 > wikinews-test-raw.txt
````
