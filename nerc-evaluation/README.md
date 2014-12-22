
## Named Entity Recognition and Classification: Evaluation

The evaluation of the Named Entity Recognition and Classification (NERC)
systems is usually done following the CoNLL 2002 and CoNLL 2003 shared tasks
methodology. Those tasks also distribute an official evaluation script which we
will be using to evaluate the performance of the NERC taggers in the Newsreader
pipeline. 

In this folder you can find the scripts necessary to evaluate a NERC tagger
system's output, provided you have the gold standard or reference corpus in
CoNLL 2002 format and the model and tagger to be evaluated.

In the results folder the wikinews data and evaluation is also provided.

### STEPS

* If you only have the gold standard dataset in CoNLL 2002 format follow all the steps.
* If you have both the gold standard and the prediction in CoNLL 2002 format **go directly to step 3.**
* If you have either the gold standard or reference in NAF you can use the [ixa-pipe-convert](https://github.com/ragerri/ixa-pipe-convert) tool to obtain the CoNLL format required: 

    java -jar ixa-pipe-convert-$version.jar --nafToCoNLL02 corpus-nerc.naf > corpus-nerc.conll02

    ...and then go directly to **step 3.**

#### 1. **Extract raw test data** from gold standard by executing 

````shell
./01-get-text-from-gold-conll.sh wiki-news-gold.conll02 > wikinews-test-raw.txt
````

#### 2. **Annotate raw test data**

This step annotates the raw gold standard corpus with a specific model:

````shell
./02-annotate-raw-test-with-ixa-pipe-nerc.sh wikinews-test-raw.txt nerc-model.bin > test-nerc-model.txt
````
**NOTE** This step depends on the model and tagger you used. The script in this step is just an illustration of what is required, but if you do not use the [ixa-pipe-nerc](http://ixa2.si.ehu.es/ixa-pipes) tagger you would need to do the annotation differently.

#### 3. **Prepare data for conlleval script** 

This step prepares the file required to use the conlleval script for evaluation:

````shell
./03-setup-test-for-conll02-script.sh test-nerc-model.txt wiki-news-gold.conll02 > conlleval-test-nerc-model.txt
````

#### 4. **Run conlleval script**:

The official conlleval script is used to obtain the results of the nerc tagger/model used. For phrase based F1, run the script like this: 

````shell
./conlleval < conlleval-test-nerc-model.txt
````

If you use the -r option the token-based F1 is provided:

````shell
./conlleval -r < conlleval-test-nerc-model.txt
````
