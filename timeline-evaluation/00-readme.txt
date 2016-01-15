


			       STS 2015

			      TimeLine:
	      Cross-Document Event Ordering (pilot task)

		   TRIAL DATA and EVALUATION SCRIPT 


Contents:

  00-README.txt 		  this file

  evaluation_all.py               evaluate a set of timelines 

  evaluation_timeline.py	  evaluate one timeline (ordering and time anchor)
  evaluation_timeline_ord.py	  evaluate one timeline (only ordering)

  temporal_evaluation.py          auxiliary functions
  relation_to_timegraph.py        auxiliary functions 

  fake_system1/                   directory containing fake system answers 

  fake_system2/                   directory containing fake system answers 


Introduction
------------

This evaluation script relies heavily on the TempEval-3 evaluation
script (UzZaman et al., 2013) used to evaluate relations. The
temporal_evaluation.py and relation_to_timegraph.py auxiliary
functions were downloaded from:

http://www.cs.rochester.edu/drupal/u/naushad/temporal


For each timeline, we use the evaluation metric presented at
TempEval-3 to evaluate relations and to obtain the F1 score. The metric
captures the temporal awareness of an annotation (UzZaman and Allen,
2011). Our evaluation script returns the micro average F1 score. 

From (UzZaman et al., 2013):

     Temporal awareness is defined as the performance of an annotation
     as identifying and categorizing temporal relations, which implies
     the correct recognition and classification of the temporal
     entities involved in the relations.

     We calculate the Precision by checking the number of reduced
     system relations that can be verified from the reference
     annotation temporal closure graph, out of number of temporal
     relations in the reduced system relations. Similarly, we
     calculate the Recall by checking the number of reduced reference
     annotation relations that can be verified from the system
     output’s temporal closure graph, out of number of temporal
     relations in the reduced reference annotation.

Before evaluating the temporal awareness, each timeline needs to be
transformed into the corresponding graph representation. For that, we
defined the following transformation steps:

- ordering and time anchors
a) Each time anchor is represented as a TIMEX3
b) Each event is related to one TIMEX3 with the "SIMULTANEOUS" relation type
c) If one event happens before another one, a "BEFORE" relation type is created between both events
d) If one event happens at the same time as another one, a "SIMULTANEOUS" relation type is created between both events

- ordering only
a) If one event happens before another one, a "BEFORE" relation type is created between both events
g) If one event happens at the same time as another one, a "SIMULTANEOUS" relation type is created between both events


Requirements
------------

Python 2.6 or later


Gold Standard
-------------

The gold standard is contained in a directory, with one file per
timeline.

The directory will contain one file per timeline. 

The name of the files must be the mention of the target entity in
lower case, and the extension ".txt". In the case of multi-word
entities, tokens will be separated by an underscore (see trial data).

A TimeLine is represented in a simple tab format:
ordering    time_anchor    event(s)

The first column (ordering) contains a cardinal number which indicates
the position of the event in the TimeLine (two events can be
associated to the same number if they are simultaneous). The second
column (time_anchor) contains a time anchor. The third column (event)
consists of one event or a list of corefered events separated by a
tab. Each event is represented by the id of the file (<DOCID>), the id
of the sentence and the extent of the event mention in the following
format: docid-sentid-event (11778-2-launch)

In the case of multi-word events, tokens are separated by an underscore.

TimeLine example:

iTunes
1    2003    11778-3-launch    11778-4-launch
2    2007    11778-4-pass
3    2008-01    11778-7-hold
4    2008-02    11778-2-pass    11778-5-pass
4    2008-02    11778-3-accounts_for

System Answer 
--------------

Each run of the system answer is contained in a separate
directory. The name of the directory needs to match the official name
of the run, as this name will be used to report system results. Please
include the name of your organization at the beginning of the name of your
runs.

The name of the files must be the mention of the target entity in
lower case, and the extension ".txt". In the case of multi-word
entities, tokens will be separated by an underscore (see trial data).

The format is the same as the gold standard.

IMPORTANT NOTE: if the answers correspond to a "ordering only"
subtrack (no assignment of time anchors), the evaluation script will
completely ignore the second column, but bogus strings need to be included. 

For example:

iTunes
1    ZZZZ    11778-3-launch    11778-4-launch
2    ZZZZ    11778-4-pass
3    ZZZZ    11778-7-hold
4    ZZZZ    11778-2-pass    11778-5-pass
4    ZZZZ    11778-3-accounts_for



Scoring
-------

The official score is based on the micro-average of the individual F1
scores for each timeline. It also provides with the micro-average
RECALL and PRECISION values. By default the evaluation script takes
ordering and time anchors into account. If the --ord option is used,
only the ordering will be evaluated.

$ ./evaluation_all.py [--ord?] [GS dir] [Answer dir]


For example

   $ ./evaluation_all.py TimeLines_trial_data_task4_v1.0 fake_system1

   steve_jobs.txt	FSCORE	61.1223	PRECISION	97.4684	RECALL	44.5205
   ipod.txt	FSCORE	81.4815	PRECISION	68.75	RECALL	100.0
   iphone_3g.txt	FSCORE	72.7273	PRECISION	100.0	RECALL	57.1429
   itunes_store.txt	FSCORE	77.135	PRECISION	87.5	RECALL	68.9655
   beatles_apple_corps.txt	FSCORE	92.3077	PRECISION	94.7368	RECALL	90.0
   iphone_4.txt	FSCORE	84.4444	PRECISION	90.4762	RECALL	79.1667
   MICRO-FSCORE	71.022233145	MICRO-PRECISION	92.0732	MICRO-RECALL	57.8059


It is possible to evaluate a single timeline as follows:

$ ./evaluation_timeline.py directory [GS file] [Answer file]

where directory contains both GS and Answer files.

For example:

  $ ./evaluation_timeline.py tmp_dir ipod_gold.txt ipod_sys.txt
 
  The F-score, recall and precision of the timeline are stored in the tmp_dir/tmp.out file.
  
  The script also creates and stores the corresponding graph representation
  files in the tmp_dir directory

In order to evaluate a single timeline with only ordering:

$ ./evaluation_timeline_ord.py tmp_dir [GS file] [Answer file]

Note: If with the information available it's not possible to order an
event, then the event is placed at the beginning of the TimeLine with
0 as position. These events are not considered by the evaluation tool.

Authors
-------

Itziar Aldabe
Eneko Agirre




References
----------

Naushad UzZaman and James Allen (2011), "Temporal Evaluation." In
Proceedings of The 49th Annual Meeting of the Association for
Computational Linguistics: Human Language Technologies (Short Paper),
Portland, Oregon, USA.

Naushad UzZaman and Hector Llorens and Leon Derczynski and Marc
Verhagen and James Allen and James Pustejovsky (2013) "SemEval-2013
Task 1: TEMPEVAL-3: Evaluating Time Expressions, Events, and Temporal
Relations" Second Joint Conference on Lexical and Computational
Semantics (*SEM), Volume 2: Seventh International Workshop on Semantic
Evaluation (SemEval 2013), pages 1–9, Atlanta, Georgia, June 14-15,
2013. http://anthology.aclweb.org//S/S13/S13-2001.pdf
