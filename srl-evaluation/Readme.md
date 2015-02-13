
## Semantic Role Labelling: Evaluation

### STEPS

#### 1.Convert CAT files into CoNLL format

````shell
sh prepare_SRL_ref_files.sh corpus_CAT_ref/corpus_apple/ corpus_CoNLL_sys/corpus_apple/ corpus_CoNLL_gold/corpus_apple/
````

#### 2. Convert SRL annotations from NAF to CoNLL format.

The following script gets the srl layer froms input-naf-file and prints it in CoNLL format into output-conll-file:

````shell
perl naf2conll.pl input-naf-file output-conll-file [fullspan]
````

Without the "fullspan" option the script only returns the head of the fillers.


#### 3. Get the 6 first sentences of each file and concatenate into a single file (apple_SRL_CoNLL_gold)

````shell
perl cat_sent_eval.pl corpus_CoNLL_gold/corpus_apple/ apple_SRL_CoNLL_gold
perl cat_sent_eval.pl corpus_CoNLL_sys/corpus_apple/ apple_SRL_CoNLL_sys
````

#### 4. Run the evaluation script

````shell
perl eval09_conll_srl.pl -q -g apple_SRL_CoNLL_gold -s apple_SRL_CoNLL_sys
````