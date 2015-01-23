
## Evaluation of Nominal Coreference

In this folder you can find the scripts necessary to evaluate a coreference
system's output, provided you have the gold standard and reference corpus in
CoNLL 2011/2012 format. 

### STEPS

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

### Wikinews Evaluation

In the results folder the wikinews data and evaluation is provided for the inner and outer named entities using a NERC ixa-pipe-nerc model which obtains 90.88 F1 on the testb CoNLL 2003 dataset. Run the conlleval script as specified in step 4. to obtain the phrase- and token-based evaluation. 

````shell
../conlleval.txt < conlleval-3-class-best-inner.txt
../conlleval.txt -r < conlleval-3-class-best-inner.txt
../conlleval.txt < conlleval-3-class-best-outer.txt
../conlleval.txt -r < conlleval-3-class-best-outer.txt
````

### Contact information

````shell
Rodrigo Agerri
IXA NLP Group
University of the Basque Country (UPV/EHU)
E-20018 Donostia-San Sebastián
rodrigo.agerri@ehu.es
````
