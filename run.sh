#!/bin/sh

CURRENTPATH=$(pwd)

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink

  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located 
 
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd $DIR

function usage(){
    printf "Usage:\n"
    printf "\t-h           : print this message\n"
    printf "\t-g           : path to the folder containing gold files\n"
    printf "\t-s           : path to the folder containing system files\n"
    printf "\t--timeline   : path to the folder containing timelines produced automatically\n"
    printf "\t-l           : language (it, en, nl, es)\n"
    printf "\t-r           : path to the file in which the results will be printed\n"
    printf "\t-t           : path to a folder in which temporary files will be saved\n"
    printf "\t-m           : list of modules (separated by a comma) to be evaluated (srl, nerc, ned, time, entcoref, eventcoref, fact, timeline, all)\n"
}

OPTS=$( getopt -o h,g,s,r,l,m,t -l timeline -- "$@" )
if [ $? != 0 ]
then
    exit 1
fi

GOLD=''
SYS=''
SYSTIMELINE=''
RES=''
language=''
TEMP=''
MODULE=''

while true ; do
    #echo $1
    case "$1" in
	-h) usage;
	    exit 0;;
	-g) GOLD=$2;
	    shift 2;;
	-s) SYS=$2;
	    shift 2;;
	--timeline) SYSTIMELINE=$2;
	    shift 2;;
	-r) RES=$2;
	    shift 2;;
	-l) language=$2;
	    shift 2;;
	-t) TEMP=$2;
	    shift 2;;
	-m) MODULE=$2;
	    shift 2;;
	--) shift; break;;
	*) break;;
    esac
done

if [[ "$MODULE" == *"timeline"* && $SYSTIMELINE == '' ]]; then
    printf "Please specify the path to the timelines produced automatically.\n"
    exit 0;
fi

if [[ "$SYSTIMELINE" == '' ]]
then
    SYSTIMELINE=" "
fi

#GOLD=$1
#SYS=$2
#SYSTIMELINE=$3
#RES=$4
#language=$5
#TEMP=$6

if [[ "$GOLD" != /* ]]; then
    GOLD="$CURRENTPATH"/"$GOLD"
fi
if [[ "$SYS" != /* ]]; then
    SYS="$CURRENTPATH"/"$SYS"
fi
if [[ "$RES" != /* ]]; then
    RES="$CURRENTPATH"/"$RES"
fi
if [[ "$TEMP" != /* ]]; then
    TEMP="$CURRENTPATH"/"$TEMP"
fi

if [[ ! -d "$TEMP" ]]; then
    mkdir "$TEMP"
fi

CROMER=gold_CAT/
if [[ -d "$GOLD"/gold_CROMER/ && "$(ls -A $GOLD/gold_CROMER/)" ]]; then
    CROMER=gold_CROMER/
fi

options=${MODULE/,/ }

#IFS=' ' read -ra ADDR <<< "$@"
#counter=1

#for i in "${ADDR[@]}"; do
#    if [[ $counter > 6 ]]; then
#	#echo $i
#	options="$options $i"
#    fi
#    let "counter += 1"
#done

#echo $options

python run_prepare_data.py "$GOLD"/gold_CAT/ "$GOLD"/"$CROMER" scripts_convert/ $GOLD $language $options

#python run_evaluation_all_modules.py "$SYS" "$RES" "$LANG" srl-evaluation/ nerc-evaluation/ nominal-coreference-evaluation/ scorer_CAT_event_timex_rel/ ned-evaluation/ factuality-evaluation/ "$GOLD"/CoNLL_SRL/ "$GOLD"/CoNLL_NER/ "$GOLD"/CoNLL_entCoref/ "$GOLD"/CoNLL_evCoref/ "$GOLD"/gold_CAT/ "$GOLD"/NAF_NED/ "$GOLD"/CoNLL_fact/

python run_evaluation_all_modules.py srl-evaluation/ nerc-evaluation/ nominal-coreference-evaluation/ scorer_CAT_event_timex_rel/ ned-evaluation/ factuality-evaluation/ eso-evaluation/ timeline-evaluation/ scripts_convert/ $GOLD $SYS $SYSTIMELINE $RES $language $TEMP $options


exit 0