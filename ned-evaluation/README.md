## Named Entity Disambiguation: Evaluation

In this folder you will find the scripts necessary to evaluate a NED
system, provided you have the gold standard.

### Steps to follow

#### 1) To obtain the manual annotation of the first 5 sentences from
     the CROMER files. 

     > goldFiveSentences.pl goldDir outFile

     Given a directory, the scripts obtains the gold
     annotations and it stores it in a file. Each line has the
     following information (separated by tab):

     docid     span	entity (disambiguated)

     (note: all the IDs of the input files are integers)

#### 2) To obtain the automatic disambiguations of the first 5
     sentences from the NAF files.

     > systemFiveSentences.pl inputDir resource outAnnotation outInfo

     Given a directory, the script looks at the entities layer and it
     extracts the ones with external references that has been
     extracted using the "resource". It keeps just the reference with
     the highest probability. The results are stored in the
     outAnnotation file and each line has the following information
     (separated by tab):

     docid	 span	    entity (disambiguated)	entity-mention

     In a separate file (outInfo), the script stores the number of
     entities detected by the NERC module, the number of entities
     disambiguated by the NED module and the number of entities not
     disambiguated.

#### 3) Run evaluation script:

   > evaluate.pl gold system output

   The script compares the gold and the system files obtained in the
   previous steps and it measure the precision and recall values:

    my $precision = $TP / $sys_all;
    my $recall = $TP / $gold_all;
    my $fscore = 2 * ($precision*$recall/($precision+$recall));

    where tp refers to the true positives, sys_all refers to the total
    amount of entities disambiguated by the system and gold_all refers
    to the total amount of entities manually disambiguated/annotated.

    The script considers true positives the entities automatically
    disambiguated and those sharing part of the span. For example:

    Manual annotation:
    129865_Airbus_offers_funding_to_search_for_black_boxes_from_Air_France_disaster.naf    1    Airbus
    71426_Aer_Lingus_buys_twelve_new_long-haul_Airbus_jets.naf    13-14-15-16-17    Aer_Lingus

    System's output:
    129865_Airbus_offers_funding_to_search_for_black_boxes_from_Air_France_disaster.naf    1    Airbus	Airbus
    71426_Aer_Lingus_buys_twelve_new_long-haul_Airbus_jets.naf    16-17    Aer_Lingus	   Aer Lingus

    Both examples are considered as true positives.

    The script stores this information in a file, each line having the following info:

    TP    Gold    System    DocID    Gold-span    System-span
    1    Airbus    Airbus    129865_Airbus_offers_funding_to_search_for_black_boxes_from_Air_France_disaster.naf    1    1
    1    Aer_Lingus    Aer_Lingus    71426_Aer_Lingus_buys_twelve_new_long-haul_Airbus_jets.naf    13-14-15-16-17    16-17
   
