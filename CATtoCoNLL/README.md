=========== from CAT format to CoNLL format (NER or SRL) ============

Date: November 2014
Author: Anne-Lyse Minard

Convert CAT annotation into CoNLL format for Named Entity Recognition and Semantic Role Labelling evaluations.


 
Processing of a folder:
> python CAT_to_CoNLL_format_NER_SRL.py folder_CAT [NER,SRL] folder_output

Processing of one file: 
> python CAT_to_CoNLL_format_NER_SRL.py file_CAT [NER,SRL] folder_output

Paramaters (defined in the python script):
type_annotation: inner ("BIO-smallest"), outer ("BIO-biggest") or all annotations ("all")
all_ent_types: 
- False: only ORG, LOC and PER entities are kept in the output file
- True: all entities are kept (ORG, LOC, PER, FIN and PRO)
all_synt_types:
- False: only NAM and PRE.NAM are kept in the output file
- True: all entities are kept

