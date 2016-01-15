#!/usr/bin/python2.6
#python run_prepare_data.py [CAT folder] [output folder] [path convert scripts] [path nominal-coreference]

import os
import re
import sys
import commands
import codecs
import tempfile
import errno
import subprocess


def input_and_convert():
    
    dirgoldin = sys.argv[1]
    dirgoldincromer = sys.argv[2]
    path_convert_scripts = sys.argv[3]
    path_eval_entity_coref = "nominal-coreference-evaluation/"
    path_eval_eso = "eso-evaluation/"
    dirgoldout = sys.argv[4]
    lang = sys.argv[5]
    
    options = []
    if len(sys.argv) > 5:
        for i in range(5,len(sys.argv)):
            options.append(sys.argv[i].lower())
    else:
        options.append("all")

    if "all" in options or "srl" in options:
        prepare_data_srl(dirgoldin, dirgoldout, path_convert_scripts, lang)
    if "eso" in options:
        prepare_data_eso(dirgoldin, dirgoldout, path_eval_eso)
    if "all" in options or "nerc" in options:
        prepare_data_ner(dirgoldin, dirgoldout, path_convert_scripts)
    if "all" in options or "fact" in options:
        prepare_data_fact(dirgoldin, dirgoldout, path_convert_scripts)
    if "all" in options or "entcoref" in options:
        prepare_data_entity_coref(dirgoldin, dirgoldout, path_eval_entity_coref)
    if "all" in options or "eventcoref" in options:
        prepare_data_event_coref(dirgoldin, dirgoldout, path_eval_entity_coref)
    if "all" in options or "ned" in options:
        prepare_data_ned(dirgoldincromer, dirgoldout, path_convert_scripts)
    
def extract_name(filename):
    parts = re.split('/',filename)
    length = len(parts)
    return parts[length-1]


def prepare_data_srl(subdirname, goldfoldername, path_convert_script, lang):

    if not os.path.exists(goldfoldername+"CoNLL_SRL/"):
        command = 'mkdir '+goldfoldername+"CoNLL_SRL/"
        os.system(command)

    command = 'python '+path_convert_script+'CAT_to_evaluation_formats_v5.py '+subdirname+' '+goldfoldername+"CoNLL_SRL/"+' '+lang+' SRL'
    os.system(command)



def prepare_data_eso(subdirname, goldfoldername, path_convert_script):

    if not os.path.exists(goldfoldername+"CoNLL_ESO/"):
        command = 'mkdir '+goldfoldername+"CoNLL_ESO/"
        os.system(command)

    command = 'python '+path_convert_script+'CAT_to_evaluation_formats_v5.py '+subdirname+' '+goldfoldername+"CoNLL_ESO/"+' ESO'
    os.system(command)


def prepare_data_fact(subdirname, goldfoldername, path_convert_script):
            
    if not os.path.exists(goldfoldername+"CoNLL_fact/"):
        command = 'mkdir '+goldfoldername+"CoNLL_fact/"
        os.system(command)

    command = 'python '+path_convert_script+'CAT_to_evaluation_formats_v5.py '+subdirname+' '+goldfoldername+"CoNLL_fact/"+' factuality'
    os.system(command)

    
def prepare_data_ner(subdirname, goldfoldername, path_convert_script):

    if not os.path.exists(goldfoldername+"CoNLL_NER/"):
        command = 'mkdir '+goldfoldername+"CoNLL_NER/"
        os.system(command)
    if not os.path.exists(goldfoldername+"CoNLL_NER/inner/"):
        command = 'mkdir '+goldfoldername+"CoNLL_NER/inner/"
        os.system(command)
    if not os.path.exists(goldfoldername+"CoNLL_NER/outer/"):
        command = 'mkdir '+goldfoldername+"CoNLL_NER/outer/"
        os.system(command)

    command = 'python '+path_convert_script+'CAT_to_evaluation_formats_v5.py '+subdirname+' '+goldfoldername+"CoNLL_NER/inner/"+' NER inner'
    os.system(command)
    command = 'python '+path_convert_script+'CAT_to_evaluation_formats_v5.py '+subdirname+' '+goldfoldername+"CoNLL_NER/outer/"+' NER outer'
    os.system(command)


def prepare_data_ned(subdirname, goldfoldername, path_convert_script):

    if not os.path.exists(goldfoldername+"NAF_NED/"):
        command = 'mkdir '+goldfoldername+"NAF_NED/"
        os.system(command)
        
    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            print file

            command = 'python '+path_convert_script+'catcromer2naf_v2.py '+subdirname+file+' | cat > '+goldfoldername+"NAF_NED/"+file+".naf"
            os.system(command)


def prepare_data_entity_coref(subdirname, goldfoldername, path_convert_script):
    if not os.path.exists(goldfoldername+"CoNLL_entCoref/"):
        command = 'mkdir '+goldfoldername+"CoNLL_entCoref/"
        os.system(command)

    command = 'cp '+subdirname+'* '+goldfoldername+"CoNLL_entCoref/"
    os.system(command)

    command = 'java -cp '+path_convert_script+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.CatCoref --coref-type ENTITY --file-extension .xml --folder '+goldfoldername+"CoNLL_entCoref/ "+' --format conll '
    os.system(command)

    command = 'java -cp '+path_convert_script+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllKey --key '+goldfoldername+"CoNLL_entCoref/"
    os.system(command)

    command = 'rm '+goldfoldername+"CoNLL_entCoref/*.xml "
    os.system(command)

def prepare_data_event_coref(subdirname, goldfoldername, path_convert_script):
    if not os.path.exists(goldfoldername+"CoNLL_evCoref/"):
        command = 'mkdir '+goldfoldername+"CoNLL_evCoref/"
        os.system(command)

    command = 'cp '+subdirname+'* '+goldfoldername+"CoNLL_evCoref/"
    os.system(command)

    command = 'java -cp '+path_convert_script+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.CatCoref --coref-type EVENT --file-extension .xml --folder '+goldfoldername+"CoNLL_evCoref/ "+' --format conll '
    os.system(command)
    
    command = 'java -cp '+path_convert_script+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllKey --key '+goldfoldername+"CoNLL_evCoref/"
    os.system(command)

    command = 'rm '+goldfoldername+"CoNLL_evCoref/*.xml "
    os.system(command)

input_and_convert()
