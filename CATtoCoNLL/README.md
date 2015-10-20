=========== from CAT format to CoNLL format (NER or SRL) ============

Date: November 2014
Author: Anne-Lyse Minard

Convert CAT annotation into CoNLL format for Named Entity Recognition, Semantic Role Labelling and event factuality evaluations.


 
Processing of a folder:
> python CAT_to_evaluation_formats.py folder_CAT folder_output [NER inner,NER outer,SRL,fact] 

Processing of one file: 
> python CAT_to_evaluation_formats.py file_CAT folder_output [NER inner,NER outer,SRL,fact]

Paramaters (defined in the python script):
type_annotation: inner ("BIO-smallest"), outer ("BIO-biggest") or all annotations ("all")
all_ent_types: 
- False: only ORG, LOC and PER entities are kept in the output file
- True: all entities are kept (ORG, LOC, PER, FIN and PRO)
all_synt_types:
- False: only NAM and PRE.NAM are kept in the output file
- True: all entities are kept

