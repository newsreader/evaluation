========= NAFtoCAT =========
Date: December 2014
Author: Anne-Lyse Minard

Build CAT files following NewsReader task from NAF files.
CAT files contain the following elements: 
<EVENT_MENTION>
<TIMEX3>
<TLINK>
<CLINK>


> sh run_NAFtoCAT.sh folder_input/ folder_output/

or 

> java -cp lib/jdom-2.0.5.jar:lib/kaflib-naf-1.1.8.jar:lib/NAFtoCAT.jar eu.fbk.newsreader.naf.NAFtoCAT folder_input/ folder_output/

or 

> java -cp lib/jdom-2.0.5.jar:lib/kaflib-naf-1.1.8.jar:lib/NAFtoCAT.jar eu.fbk.newsreader.naf.NAFtoCAT file_input file_output


* folder_input/ --> contains NAF files
* folder_output/ --> will contain CAT files


External libraries (to be put in lib/):
- jdom-2.0.5.jar
- kaflib-naf-1.1.8.jar
