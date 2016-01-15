EVALUATION PACKAGE - NEWSREADER
===============================

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

And copy the cat files into gold_dutch/gold_CAT/

