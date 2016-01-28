#!/usr/bin/python2.6

import os
import re
import sys
import time
import commands
import codecs
import tempfile
import errno
import mmap

from subprocess import Popen, PIPE, STDOUT

global dirgold
global out_write
global dirsysin
global output_file
global temp_folder
global lang

path_eval_srl = sys.argv[1]
path_eval_ner = sys.argv[2]
path_eval_entity_coref = sys.argv[3]
path_eval_temp_proc = sys.argv[4]
path_eval_ned = sys.argv[5]
path_eval_fact = sys.argv[6]
path_eval_eso = sys.argv[7]
path_eval_timeline = sys.argv[8]
path_script_convert = sys.argv[9]

path_gold = sys.argv[10]
dirsysin = sys.argv[11]
dirsysintimeline = sys.argv[12]

#print dirsysin
output_file = sys.argv[13]
lang = sys.argv[14]
temp_folder = sys.argv[15]

dirgold_srl = path_gold+"/CoNLL_SRL/"
dirgold_eso = path_gold+"/CoNLL_ESO/"
dirgold_nerc = path_gold+"/CoNLL_NER/"
dirgold_entity_coref = path_gold+"/CoNLL_entCoref/"
dirgold_event_coref = path_gold+"/CoNLL_evCoref/"
dirgold_temp_proc = path_gold+"/gold_CAT/"
dirgold_ned = path_gold+"/NAF_NED/"
dirgold_fact = path_gold+"/CoNLL_fact/"
dirgold_timeline = path_gold+"/timeline/"

#path_scorer_entity_coref = "\/home\/anne-lyse\/Documents\/NewsReader\/Code\/evaluation\/evaluation_NWR_github\/evaluation\/nominal-coreference-evaluation\/reference-coreference-scorers\/v8.01\/"

path_scorer_entity_coref = path_eval_entity_coref+"reference-coreference-scorers/v8.01/"
path_scorer_entity_coref = path_scorer_entity_coref.replace("/","\\/")

def input_and_evaluate():
    global out_write
    global dirsysin
    global dirsysintimeline
    global output_file
    global temp_folder
    global lang
    #dirsysin = sys.argv[1]

    num_arg = 15

    if (not os.path.isdir(dirsysintimeline) or not len(os.listdir(dirsysintimeline)) > 0) and not os.path.isfile(output_file):
        dirsysintimeline = ""
        output_file = sys.argv[12]
        lang = sys.argv[13]
        temp_folder = sys.argv[14]
        num_arg = 14
        
    
    options = []
    if len(sys.argv) > num_arg:
        for i in range(num_arg,len(sys.argv)):
            options.append(sys.argv[i].lower())
    else:
        options.append("all")

    out_write = open(output_file, "w")

    if os.path.isdir(dirsysin):
        for file in os.listdir(dirsysin):
            if dirsysin[-1] != '/':
                dirsysin += '/'
            command = 'perl '+path_script_convert+'rename_NAF_files.pl '+dirsysin+file+'/'
            os.system(command)
            
        if "all" in options or "srl" in options:
            print "\n\n>>> evaluation SRL\n\n"
            out_write.write("************ SRL *************\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                   
                out_write.write("\n>>>> head from NAF\n")
                evaluate_folder_srl(dirsysin+file, "", path_eval_srl)
                out_write.write("\n>>>> full span from NAF\n")
                evaluate_folder_srl(dirsysin+file, "fullspan", path_eval_srl)


        if "eso" in options:
            print "\n\n>>> evaluation ESO\n\n"
            out_write.write("************ ESO *************\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                   
                #out_write.write("\n>>>> head from NAF\n")
                #evaluate_folder_srl(dirsysin+file, "", path_eval_eso)
                out_write.write("\n>>>> full span from NAF\n")
                evaluate_folder_srl(dirsysin+file, "fullspan", path_eval_eso)


        if "all" in options or "nerc" in options:

            print "\n\n>>> evaluation NERC\n\n"
            out_write.write("\n********** NERC **********\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                
                evaluate_folder_ner(dirsysin+file,"inner")
            
                evaluate_folder_ner(dirsysin+file,"outer")


        if "all" in options or "ned" in options:
                
            print "\n\n>>> evaluation NED\n\n"
            out_write.write("\n********** NED **********\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                
                evaluate_folder_ned(dirsysin+file)


        if "all" in options or "entcoref" in options:
            
            print "\n\n>>> evaluation nominal coreference\n\n"
            out_write.write("\n********** Nominal coreference **********\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                
                evaluate_folder_entity_coref(dirsysin+file)

            
        if "all" in options or "eventcoref" in options:

            print "\n\n>>> evaluation event coreference\n\n"
            out_write.write("\n********** Event coreference **********\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                
                evaluate_folder_event_coref(dirsysin+file)


        if "all" in options or "time" in options:

            print "\n\n>>> evaluation time processing\n\n"
            out_write.write("\n********** Temporal Processing **********\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                
                evaluate_temporal_processing(dirsysin+file)

        
        if "all" in options or "fact" in options:

            print "\n\n>>> evaluation factuality\n\n"
            out_write.write("\n********** Factuality **********\n\n")
            for file in os.listdir(dirsysin):
                out_write.write("\n"+file+"\n")
                if dirsysin[-1] != '/':
                    dirsysin += '/'
                
                evaluate_factuality(dirsysin+file)



    if "all" in options or "timeline" in options:

        if os.path.isdir(dirsysintimeline):
            
            print "\n\n>>> evaluation timeline creation\n\n"
            out_write.write("\n********** TimeLine creation **********\n\n")
            for file in os.listdir(dirsysintimeline):
                out_write.write("\n"+file+"\n")
                if dirsysintimeline[-1] != '/':
                    dirsysintimeline += '/'
                
                evaluate_timeline_creation(dirsysintimeline+file)




    out_write.close()

def extract_name(filename):
    parts = re.split('/',filename)
    length = len(parts)
    return parts[length-1]


def create_tmp_folder():
    tmp_folder = tempfile.mkdtemp()
    #tmp_folder += "_"+ext+"/"
    try:
        os.makedirs(tmp_folder)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(tmp_folder):
            pass
        else: raise
    return tmp_folder


def create_folder(folder_name):
    
    try:
        os.makedirs(folder_name)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(folder_name):
            command = 'rm '+folder_name+'/*'
            os.system(command)
            pass
        else: raise
    return folder_name


def evaluate_folder_srl(subdirname, span, path_scripts):
    list_id_files = []
    list_id_name_files = {}

    subdirsysoutsrl = create_folder(temp_folder+extract_name(subdirname)+'_sys_srl'+span+'/')
    subdirgoldoutsrl = create_folder(temp_folder+extract_name(subdirname)+'_gold_srl'+span+'/')
    subdirgoldoutsrlconll = create_folder(temp_folder+extract_name(subdirname)+'_gold_srl'+span+'_conll/')

    filesysoutsrl = temp_folder+extract_name(subdirname)+'_sys_srl'+span+'.conll'

    filegoldoutsrl = temp_folder+extract_name(subdirname)+'_gold_srl'+span+'.conll'

    if subdirname[-1] != '/':
        subdirname += '/'

    #print subdirname

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files.append(id_file)
            list_id_name_files[id_file] = file
            #print file

            if lang == "it" or lang == "nl":
                command = 'perl '+path_scripts+'naf2conll_notEn.pl '+subdirname+file+' '+subdirsysoutsrl+"/"+file+".conll "+span
            else:
                command = 'perl '+path_scripts+'naf2conll.pl '+subdirname+file+' '+subdirsysoutsrl+"/"+file+".conll "+span
       
            #print command
            os.system(command)
    

    dirgold_srleso = dirgold_srl
    if not "srl" in path_scripts:
        dirgold_srleso = dirgold_eso

    for file in os.listdir(dirgold_srleso):
        if os.path.isfile(dirgold_srleso+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            if id_file in list_id_files:
                new_name = list_id_name_files[id_file]
                new_name = new_name[:-4]+".naf.conll"
                #new_name = new_name[:-4]+".txt.xml" 
                
                #if "srl" in path_scripts:
                command = 'cp '+dirgold_srleso+file+' '+subdirgoldoutsrl+"/"+new_name
                os.system(command)

                #else:
                #    command = 'cp '+dirgold_eso+file+' '+subdirgoldoutsrl+"/"+new_name
                #    os.system(command)

                    

    #command = 'sh '+path_eval_srl+'prepare_SRL_ref_files.sh '+subdirgoldoutsrl+"/ "+subdirsysoutsrl+'/ '+subdirgoldoutsrlconll+"/"
    command = 'sh '+path_eval_srl+'prepare_SRL_ref_files.sh '+subdirgoldoutsrl+"/ "+subdirsysoutsrl+'/ '+subdirgoldoutsrlconll+"/"
    #print command
    os.system(command)

    command = 'perl '+path_scripts+'cat_sent_eval_v2.pl '+subdirgoldoutsrlconll+'/ '+filegoldoutsrl
    #print command
    os.system(command)

    command = 'perl '+path_scripts+'cat_sent_eval_v2.pl '+subdirsysoutsrl+'/ '+filesysoutsrl
    #print command
    os.system(command)


    command = 'perl '+path_eval_srl+'eval09_conll_srl.pl -q -g '+filegoldoutsrl+' -s '+filesysoutsrl
    os.system(command)

    #output = subprocess.check_output(command, shell=True)
    #output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
    #print output

    command = 'rm -rf '+subdirsysoutsrl
    #print command
    #os.system(command)
    command = 'rm -rf '+subdirgoldoutsrl
    #os.system(command)
    #print command
    command = 'rm -rf '+subdirgoldoutsrlconll
    #print command
    #os.system(command)

def evaluate_folder_ner(subdirname,ner_extent):
    list_id_files = []

    subdirsysoutner = create_folder(temp_folder+extract_name(subdirname)+'_sys_ner_'+ner_extent+'/')
    subdirgoldoutner = create_folder(temp_folder+extract_name(subdirname)+'_gold_ner_'+ner_extent+'/')

    filesysoutner = temp_folder+extract_name(subdirname)+'_sys_ner_'+ner_extent+'.conll'

    filegoldoutner = temp_folder+extract_name(subdirname)+'_gold_ner_'+ner_extent+'.conll'

    filegoldsysevalner = temp_folder+extract_name(subdirname)+'_eval_ner_'+ner_extent

    if subdirname[-1] != '/':
        subdirname += '/'

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files.append(id_file)
            command = 'cp '+subdirname+file+' '+subdirsysoutner+'/'+file
            os.system(command)

    #command = 'java -jar '+path_eval_ner+'lib/ixa-pipe-convert-0.2.0.jar --nafToCoNLL03 '+subdirname+' --out '+subdirsysoutner
    command = 'java -jar '+path_eval_ner+'lib/ixa-pipe-convert-0.2.0.jar --nafToCoNLL03 '+subdirsysoutner
    os.system(command)

    command = 'rm '+subdirsysoutner+'/*.naf '
    os.system(command)
    

    for file in os.listdir(dirgold_nerc+ner_extent+"/"):
        if os.path.isfile(dirgold_nerc+ner_extent+"/"+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            if id_file in list_id_files:
                command = 'cp '+dirgold_nerc+ner_extent+"/"+file+' '+subdirgoldoutner+"/"+file
                os.system(command)
                #command = "sed -i 's/B-/I-/g' "+subdirgoldoutner+"/"+file
                #os.system(command)
    
    command = 'sh '+path_eval_ner+'01-get-first-5-sentences-from-gold.sh '+subdirgoldoutner
    os.system(command)
    #print command
    command = 'cat '+subdirgoldoutner+'/*.five >'+filegoldoutner
    os.system(command)

    command = 'sh '+path_eval_ner+'01-get-first-5-sentences-from-gold.sh '+subdirsysoutner
    os.system(command)
    command = 'cat '+subdirsysoutner+'/*.five >'+filesysoutner
    os.system(command)
    #command = "sed -i 's/[BI]-MISC/O/g' "+filesysoutner
    #os.system(command)
    #print command

    #command = 'sh '+path_eval_ner+'04-setup-test-for-conll03-script.sh '+filegoldoutner+' '+filesysoutner+' >'+filegoldsysevalner
    command = 'sh '+path_eval_ner+'04-setup-test-for-conll03-script.sh '+filesysoutner+' '+filegoldoutner+' >'+filegoldsysevalner
    os.system(command)
    #print command

    out_write.write("\n>>>> "+ner_extent+" phrase-based\n")
    command = 'perl '+path_eval_ner+'conlleval.pl <'+filegoldsysevalner
    #os.system(command)
    
    #output = subprocess.check_output(command, shell=True)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
    #print output

    out_write.write("\n>>>> "+ner_extent+" token-based\n")
    command = 'perl '+path_eval_ner+'conlleval.pl -r <'+filegoldsysevalner
    #os.system(command)
    
    #output = subprocess.check_output(command, shell=True)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
    #print output


    command = 'rm -rf '+subdirsysoutner
    #print command
    #os.system(command)
    command = 'rm -rf '+subdirgoldoutner
    #print command
    #os.system(command)

def evaluate_folder_ned(subdirname):
    list_id_files = {}

    subdirsysoutned = create_folder(temp_folder+extract_name(subdirname)+'_sys_ned')
    subdirgoldoutned = create_folder(temp_folder+extract_name(subdirname)+'_gold_ned')

    filegoldoutned = temp_folder+extract_name(subdirname)+'_gold_file_ned'
    fileevalned = temp_folder+extract_name(subdirname)+'_eval_ned'

    if subdirname[-1] != '/':
        subdirname += '/'

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files[id_file] = file
    
    if lang == "en":
        command = 'perl '+path_eval_ned+'systemFiveSentences.pl '+subdirname+' spotlight_v1 '+subdirsysoutned+'/outAnnotation '+subdirsysoutned+'/outInfo '
    else:
        command = 'perl '+path_eval_ned+'systemFiveSentencesNotEnglish.pl '+subdirname+' wikipedia-db-'+lang+'En '+subdirsysoutned+'/outAnnotation '+subdirsysoutned+'/outInfo '+path_eval_ned
    
    #print command
    os.system(command)
    

    for file in os.listdir(dirgold_ned):
        if os.path.isfile(dirgold_ned+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            if id_file in list_id_files:
                command = 'cp '+dirgold_ned+file+' '+subdirgoldoutned+"/"+list_id_files[id_file]
                os.system(command)
    
    command = 'perl '+path_eval_ned+'goldFiveSentencesWithRedirects.pl '+subdirgoldoutned+'/ '+filegoldoutned+' '+path_eval_ned
    os.system(command)
    
    command = 'perl '+path_eval_ned+'evaluate_v2.pl '+filegoldoutned+' '+subdirsysoutned+'/outAnnotation '+fileevalned
    os.system(command)
    #print command

    #command = 'cat '+fileevalned
    
    #output = subprocess.check_output(command, shell=True)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
    #print output

    #command = 'rm -rf '+subdirsysoutned
    #os.system(command)
    #command = 'rm -rf '+subdirgoldoutned
    #os.system(command)


def evaluate_folder_entity_coref(subdirname):
    list_id_files = {}

    subdirsysoutner = create_folder(temp_folder+extract_name(subdirname)+'_sys_entCoref/')
    subdirgoldoutner = create_folder(temp_folder+extract_name(subdirname)+'_gold_entCoref/')

    filesysoutner = temp_folder+extract_name(subdirname)+'_sys_entCoref.conll'

    filegoldoutner = temp_folder+extract_name(subdirname)+'_gold_entCoref.conll'

    filegoldsysevalner = temp_folder+extract_name(subdirname)+'_eval_entCoref'

    if subdirname[-1] != '/':
        subdirname += '/'

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files[id_file] = file

            command = 'cp '+subdirname+file+' '+subdirsysoutner+"/"+file
            os.system(command)
    
            #command = 'sed -i "s/\\(<coref id=\\"[^\\"]*\\"\\)>/\\1 type=\\"entity\\">/g" '+subdirsysoutner+"/"+file
            #os.system(command)
            #command = 'sed -i "s/\\(<target id=\\"\\)t\\([^\\"]*\\"\\/>\\)/\\1w\\2/g" '+subdirsysoutner+"/"+file
            #os.system(command)
            

    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type ENTITY --file-extension .naf --folder '+subdirsysoutner+' --format conll'
    os.system(command)

    for file in os.listdir(subdirsysoutner):
        if os.path.isfile(subdirsysoutner+"/"+file):
            file_name_wo_ext = file
            file_name_wo_ext = file_name_wo_ext[0:file.index(".")]

            #file_name_wo_ext = file_name_wo_ext.replace(".naf.ENTITY.response","")
            #command = 'sed -i "s/\\(begin document (\\)[^)]*)/\\1'+file_name_wo_ext+')/" '+subdirsysoutner+"/"+file
            command = "perl -p -i -e 's/(begin document \()[^\)]*\)/${1}"+file_name_wo_ext+"\)/' "+subdirsysoutner+"/"+file
            os.system(command)
    

    for file in os.listdir(dirgold_entity_coref):
        if os.path.isfile(dirgold_entity_coref+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            if id_file in list_id_files:
                #command = 'cp '+dirgold_entity_coref+file+' '+subdirgoldoutner+"/"+list_id_files[id_file]+".ENTITY.key"
                #os.system(command)
                #file_name_wo_ext = list_id_files[id_file]
                #file_name_wo_ext = file_name_wo_ext.replace(".naf","")
                #command = 'sed -i "s/\\(begin document (\\)[^)]*)/\\1'+file_name_wo_ext+')/" '+subdirgoldoutner+"/"+list_id_files[id_file]+".ENTITY.key"
                #os.system(command)
    
                file_name_wo_ext = list_id_files[id_file]
                file_name_wo_ext = file_name_wo_ext[0:list_id_files[id_file].index(".")]

                #file_name_wo_ext = file_name_wo_ext.replace(".naf","")
                
                command = "perl -pe 's/(begin document \()[^\)]*\)/${1}"+file_name_wo_ext+"\)/' "+dirgold_entity_coref+file+" >"+subdirgoldoutner+"/"+list_id_files[id_file]+".ENTITY.key"
                os.system(command)
                

    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllResponse --response '+subdirsysoutner+'/ --key '+subdirgoldoutner+'/'
    os.system(command)


    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.script.MakeScoreScript --key '+subdirgoldoutner+' --response '+subdirsysoutner+' --corpus muc_entities --method muc'
    os.system(command)
    
    command = "perl -p -i -e 's/\.\/v8.01\//"+path_scorer_entity_coref+"/g' "+temp_folder+'muc_entities.score.sh'
    #command = 'sed -i "s/\.\/v8.01\//'+path_scorer_entity_coref+'/g" '+temp_folder+'muc_entities.score.sh'
    os.system(command)

    command = 'sh '+temp_folder+'muc_entities.score.sh '
    os.system(command)


    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.script.MakeScoreScript --key '+subdirgoldoutner+' --response '+subdirsysoutner+' --corpus ceafe_entities --method ceafe'
    os.system(command)    

    command = "perl -p -i -e 's/\.\/v8.01\//"+path_scorer_entity_coref+"/g' "+temp_folder+'ceafe_entities.score.sh'
    #command = 'sed -i "s/\.\/v8.01\//'+path_scorer_entity_coref+'/g" '+temp_folder+'ceafe_entities.score.sh'
    os.system(command)

    command = 'sh '+temp_folder+'ceafe_entities.score.sh '
    os.system(command)


    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.script.MakeScoreScript --key '+subdirgoldoutner+' --response '+subdirsysoutner+' --corpus bcub_entities --method bcub'
    os.system(command)

    command = "perl -p -i -e 's/\.\/v8.01\//"+path_scorer_entity_coref+"/g' "+temp_folder+'bcub_entities.score.sh'
    #command = 'sed -i  "s/\.\/v8.01\//'+path_scorer_entity_coref+'/g" '+temp_folder+'bcub_entities.score.sh'
    os.system(command)


    command = 'sh '+temp_folder+'bcub_entities.score.sh '
    os.system(command)


    command = 'sh '+path_eval_entity_coref+'08-collect-results-NWR.sh '+subdirsysoutner+' '+temp_folder
    
    #output = subprocess.check_output(command, shell=True)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
    #print output

    #command = 'rm -rf '+subdirsysoutner
    #print command
    #os.system(command)
    #command = 'rm -rf '+subdirgoldoutner
    #print command
    #os.system(command)


def evaluate_folder_event_coref(subdirname):
    list_id_files = {}

    subdirsysoutner = create_folder(temp_folder+extract_name(subdirname)+'_sys_eventCoref/')
    subdirgoldoutner = create_folder(temp_folder+extract_name(subdirname)+'_gold_eventCoref/')

    filesysoutner = temp_folder+extract_name(subdirname)+'_sys_eventCoref.conll'

    filegoldoutner = temp_folder+extract_name(subdirname)+'_gold_eventCoref.conll'

    filegoldsysevalner = temp_folder+extract_name(subdirname)+'_eval_eventCoref'

    if subdirname[-1] != '/':
        subdirname += '/'

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files[id_file] = file

            command = 'cp '+subdirname+file+' '+subdirsysoutner+"/"+file
            os.system(command)
    
            #command = 'sed -i "s/\\(<target id=\\"\\)t\\([^\\"]*\\"\\/>\\)/\\1w\\2/g" '+subdirsysoutner+"/"+file
            #os.system(command)
            

    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.NafCoref --coref-type EVENT --file-extension .naf --folder '+subdirsysoutner+' --format conll'
    os.system(command)

    for file in os.listdir(subdirsysoutner):
        if os.path.isfile(subdirsysoutner+"/"+file):
            file_name_wo_ext = file
            file_name_wo_ext = file_name_wo_ext[0:file.index(".")]
            #file_name_wo_ext = file_name_wo_ext.replace(".naf.EVENT.response","")
            command = "perl -p -i -e 's/(begin document \()[^\)]*\)/${1}"+file_name_wo_ext+"\)/' "+subdirsysoutner+"/"+file
            #command = 'sed -i "s/\\(begin document (\\)[^)]*)/\\1'+file_name_wo_ext+')/" '+subdirsysoutner+"/"+file
            os.system(command)
    

    for file in os.listdir(dirgold_event_coref):
        if os.path.isfile(dirgold_event_coref+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            if id_file in list_id_files:
                command = 'cp '+dirgold_event_coref+file+' '+subdirgoldoutner+"/"+list_id_files[id_file]+".EVENT.key"
                os.system(command)
                file_name_wo_ext = list_id_files[id_file]
                file_name_wo_ext = file_name_wo_ext[0:list_id_files[id_file].index(".")]
                #file_name_wo_ext = file_name_wo_ext.replace(".naf","")
                command = "perl -pe 's/(begin document \()[^\)]*\)/${1}"+file_name_wo_ext+"\)/' "+dirgold_event_coref+file+" >"+subdirgoldoutner+"/"+list_id_files[id_file]+".EVENT.key"
                #command = 'sed -i "s/\\(begin document (\\)[^)]*)/\\1'+file_name_wo_ext+')/" '+subdirgoldoutner+"/"+list_id_files[id_file]+".EVENT.key"
                os.system(command)
    
    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.conversion.ReduceConllResponse --response '+subdirsysoutner+'/ --key '+subdirgoldoutner+'/'
    os.system(command)    

    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.script.MakeScoreScript --key '+subdirgoldoutner+' --response '+subdirsysoutner+' --corpus blanc_events --method blanc'
    os.system(command)

    command = "perl -p -i -e 's/\.\/v8.01\//"+path_scorer_entity_coref+"/g' "+temp_folder+'blanc_events.score.sh'
    #command = 'sed -i "s/\.\/v8.01\//'+path_scorer_entity_coref+'/g" /tmp/blanc_events.score.sh'
    os.system(command)

    command = 'sh '+temp_folder+'blanc_events.score.sh '
    os.system(command)

    #command = 'sh '+path_eval_entity_coref+'08-collect-results-events-NWR.sh '+subdirsysoutner+' /tmp/'
    command = 'java -cp '+path_eval_entity_coref+'lib/coreference-evaluation-1.0-SNAPSHOT-jar-with-dependencies.jar eu.newsreader.result.CollectResults --result-folder '+subdirsysoutner+' --extension .result'
    os.system(command)

    command = 'tail -n+3 '+temp_folder+'results.csv'

    #output = subprocess.check_output(command, shell=True)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
    #print output

    #command = 'rm -rf '+subdirsysoutner
    #os.system(command)
    #print command
    #command = 'rm -rf '+subdirgoldoutner
    #os.system(command)
    #print command


def evaluate_temporal_processing (subdirname):
    list_id_files = {}

    subdirsysouttime = create_folder(temp_folder+extract_name(subdirname)+'_sys_time/')
    subdirgoldouttime = create_folder(temp_folder+extract_name(subdirname)+'_gold_time/')

    #print subdirsysouttime
    #print subdirgoldouttime

    #filesysoutner = '/tmp/'+extract_name(subdirname)+'_sys.cat'

    #filegoldoutner = '/tmp/'+extract_name(subdirname)+'_gold.cat'

    #filegoldsysevalner = '/tmp/'+extract_name(subdirname)+'_eval'

    if subdirname[-1] != '/':
        subdirname += '/'

    print subdirname

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files[id_file] = file
            
            #command = 'cp '+subdirname+file+' '+subdirsysoutner+"/"+file
            #os.system(command)
    #        print file
    #command = 'java -cp '+path_eval_temp_proc+'lib/jdom-2.0.5.jar:'+path_eval_temp_proc+'lib/kaflib-naf-1.1.8.jar:'+path_eval_temp_proc+'lib/NAFtoCAT.jar eu.fbk.newsreader.naf.NAFtoCAT '+subdirname+file+' '+subdirsysouttime+'/'+file+'.xml'
    command = 'java -cp '+path_eval_temp_proc+'lib/jdom-2.0.5.jar:'+path_eval_temp_proc+'lib/kaflib-naf-1.1.8.jar:'+path_eval_temp_proc+'lib/NAFtoCAT.jar eu.fbk.newsreader.naf.NAFtoCAT '+subdirname+' '+subdirsysouttime+'/'
    os.system(command)
            
    for file in os.listdir(dirgold_temp_proc):
        if os.path.isfile(dirgold_temp_proc+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            if id_file in list_id_files:
                command = 'cp '+dirgold_temp_proc+file+' '+subdirgoldouttime+"/"+list_id_files[id_file]+'.xml'
                os.system(command)

    command = 'python '+path_eval_temp_proc+'scorer_CAT_NWR_v2.py '+subdirgoldouttime+'/ '+subdirsysouttime+'/ '+path_eval_temp_proc+'list_class_att_NWR'
    
    #output = subprocess.check_output(command, shell=True)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read()
    out_write.write(output)
                

    #command = 'rm -rf '+subdirsysouttime
    #os.system(command)

    #command = 'rm -rf '+subdirgoldouttime
    #os.system(command)



def evaluate_timeline_creation (subdirname):
    list_id_files = {}

    #subdirsysouttime = create_folder(temp_folder+extract_name(subdirname)+'_sys_timeline/')
    #subdirgoldouttime = create_folder(temp_folder+extract_name(subdirname)+'_gold_timeline/')


    subdirgoldtimeline = dirgold_timeline+extract_name(subdirname)

    if subdirname[-1] != '/':
        subdirname += '/'

    print subdirname


    if os.path.isdir(subdirname) and os.path.exists(subdirgoldtimeline):


        command = 'python '+path_eval_timeline+'evaluation_all.py '+subdirgoldtimeline+' '+subdirname+' '
        print command

        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        out_write.write(output)

    else:
        
        if not os.path.isdir(subdirname):
            print subdirname+" doesn't exist or is not a folder"
        else:
            print subdirgoldtimeline+" doesn't exist or is not a folder"


def evaluate_factuality (subdirname):
    list_id_files = {}

    subdirsysoutfact = create_folder(temp_folder+extract_name(subdirname)+'_sys_fact/')
    subdirgoldoutfact = create_folder(temp_folder+extract_name(subdirname)+'_gold_fact/')

    #print subdirsysoutfact
    #print subdirgoldoutfact

    if subdirname[-1] != '/':
        subdirname += '/'

    no_fact = False

    for file in os.listdir(subdirname):
        if os.path.isfile(subdirname+file):
            p = re.compile('^([0-9]+)[_-]')
            m = p.match(file)
            id_file = m.group(1)
            
            list_id_files[id_file] = file

            f = open(subdirname+file)
            s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            if s.find('layer=\"factualities\"') == -1:
                no_fact = True
                break

            command = 'cat '+subdirname+file+' | python '+path_eval_fact+'factuality_to_conll_v2.py >'+subdirsysoutfact+'/'+file+'.conll'
            os.system(command)

    if not no_fact:
        for file in os.listdir(dirgold_fact):
            if os.path.isfile(dirgold_fact+file):
                p = re.compile('^([0-9]+)[_-]')
                m = p.match(file)
                id_file = m.group(1)
                if id_file in list_id_files:
                    command = 'cp '+dirgold_fact+file+' '+subdirgoldoutfact+"/"+list_id_files[id_file]+'.conll'
                    os.system(command)

        command = 'perl '+path_eval_fact+'evaluation_factuality_v3.0.pl '+subdirgoldoutfact+'/ '+subdirsysoutfact+'/ '
    
    #output = subprocess.check_output(command, shell=True)
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        out_write.write(output)

    #command = 'rm -rf '+subdirsysoutfact
    #os.system(command)

    #command = 'rm -rf '+subdirgoldoutfact
    #os.system(command)


def printUsage():
    print "usage: python run_evaluation_all_modules.py gold sys res lang temp [options]"
    print " "                                          
    print "       gold : path to the folder containing the goldstandard"
    print "       sys : path to the folder containing the system files"
    print "       res : output file that will contain the results of the evaluation"
    print "       lang : en | es | it | nl "
    print "       temp : path to the folder in which will be saved the temporary files"
    print "       options   : list of layers to evaluate "
    print "                   all : all layers"
    print "                   srl ; nerc ; ned ; entcoref ; eventcoref ; time ; fact"


if __name__ == '__main__':
    
    if len(sys.argv) < 15:
        printUsage()
    else:
        input_and_evaluate()
