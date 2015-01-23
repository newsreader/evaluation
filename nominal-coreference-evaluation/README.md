
## Evaluation of Nominal Coreference

In this folder you can find the scripts necessary to evaluate a coreference
system's output, provided you have the gold standard and reference corpus in
CoNLL 2011/2012 format. 

### STEPS

#### 1. **Convert CAT to CoNLL format** 

````shell
./01-convert-gold-cat-to-conll.sh
````

#### 2. **Remove sentences without annotation**

````shell
./02-reduce-gold-to-annotated-data.sh
````
#### 3. **Obtain plain text from gold for annotation** 

````shell
./03-get-raw-text-from-gold.sh gold-standard/corpus_apple/
````

#### 4. **Annotate gold raw plain text with Corefgraph**:

The official conlleval script is used to obtain the results of the nerc tagger/model used. For phrase based F1, run the script like this: 

````shell
./04-annotate-raw-text-corefgraph.sh ~/javacode/newsreader/coreference-conll-evaluation/corefgraph-raw-wikinews/corpus_apple/ ~/javacode/ixa-pipe-nerc/en-91-14-conll03.bin
````
#### 5. **Convert Coreference prediction from NAF to CoNLL**:

````shell
./05-convert-naf-to-conll.sh
````

#### 6. **Prepare corpora for CoNLL script**:

````shell
./06-prepare-corpus-for-conll-script.sh
````

#### 7. **Run conll script**:

````shell
./07-run-conll-script.sh
````

#### 8. **Print out the results**:

````shell
./08-collect-results.sh
````
