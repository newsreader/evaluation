EVALUATION PACKAGE - NEWSREADER
===============================

Copyright 2016 FBK, EHU, VUA

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

==============================

Each folder contains the materials for evaluating one module of the pipeline as well as a README with contact information.

Author: FBK, EHU, VUA
Contact: minard@fbk.eu

Evaluation of the modules of the pipeline:
- SRL
- NERC
- NED
- nominal coreference
- event coreference
- TIMEX3 and TLINK
- factuality

Usage:
        -h           : print this message
        -g           : path to the folder containing gold files
        -s           : path to the folder containing system files
        --timeline   : path to the folder containing timelines produced automatically
        -l           : language (it, en, nl, es)
        -r           : path to the file in which the results will be printed
        -t           : path to a folder in which temporary files will be saved
        -m           : list (separated by a comma) of modules to be evaluated (srl, nerc, ned, time, entcoref, eventcoref, fact, timeline, all)


> sh run.sh -g gold_english/ -s system_naf_output_folder/ --timeline system_timeline_output_folder/ -r result_file -l lang -t temporal_folder/ -m [option]

lang:
- en
- nl
- it
- es

option:
- all: evaluation of all modules
- nerc: evaluation of NERC module
- srl: evaluation of SRL module
- ned: evaluation of NED module
- time: evaluation of TIMEX3 and TLINK
- fact: evaluation of factuality
- entcoref: evaluation of nominal coreference
- eventcoref: evaluation of event coreference 

Benchmarking files:
- gold_english/gold_CAT/ contains all the annotated files in CAT format

If cross-document annotated files are different than intra-document annotated files, then they should be in the folder: gold_english/gold_CROMER/.

In order to run the evaluation for Dutch, Spanish and Italian:
> mkdir gold_dutch/
> mkdir gold_dutch/gold_CAT/
> mkdir gold_dutch/gold_CROMER/

And copy the intra-doc files (annotated with CAT) into gold_dutch/gold_CAT/ and the cross-doc files (annotated with CROMER) into gold_dutch/gold_CROMER/.

The gold standard files can be downloaded from the newsreader website: http://www.newsreader-project.eu/results/data/wikinews


Installation:
> git clone https://github.com/newsreader/evaluation

> cd evaluation/

NERC scorer: 
> wget http://www.cnts.ua.ac.be/conll2000/chunking/conlleval.txt nerc-evaluation/
> mv nerc-evaluation/conlleval.txt nerc-evaluation/conlleval.pl

Temporal Relation evaluation:
> git clone git@github.com:naushadzaman/tempeval3_toolkit.git
> cp tempeval3_toolkit/evaluation-relations/relation_to_timegraph.py* scorer_CAT_event_timex_rel/
> cp tempeval3_toolkit/evaluation-relations/* tempeval3_toolkit/timeline-evaluation/

SRL scorer:
> wget http://ufal.mff.cuni.cz/conll2009-st/eval09.pl srl-evaluation/