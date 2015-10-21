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

* folder_input/ --> contains NAF files
* folder_output/ --> will contain CAT files

External libraries (to be put in lib/):
- jdom-2.0.5.jar
- kaflib-naf-1.1.8.jar

