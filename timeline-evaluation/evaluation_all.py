#!/usr/bin/python 

b'You need Python 2.6 or later.'

import sys
import os
import tempfile
import errno
import re


gold_dir = ''
system_dir = ''
directory_path = ''


def get_directory_path(path):
    name = extract_name(path)
    dir = re.sub(name, '', path)
    if dir == '':
        dir = './'
    return dir

def extract_name(filename):
    parts = re.split('/', filename)
    length = len(parts)
    return parts[length-1]

def create_tmp_folder():
    tmp_folder = tempfile.mkdtemp() 
    try:
        os.makedirs(tmp_folder)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(tmp_folder):
            pass
        else: raise
    return tmp_folder

tmp_folder = create_tmp_folder()

directory_path = get_directory_path(sys.argv[0])

if len(sys.argv) > 3:
    ord = 1
else:
    ord = 0

if (ord):
    gold_dir = sys.argv[2]
    system_dir = sys.argv[3]
else:
    gold_dir = sys.argv[1]
    system_dir = sys.argv[2]

globalPrec = 0.0
globalSys = 0.0
globalRec = 0.0
globalGold = 0.0
for file in os.listdir(gold_dir):
    f = open(gold_dir+'/'+file,'r')
    out = open(tmp_folder+'/gold-'+file,'w')
    for i, line in enumerate(f):
        if i == 0:
            continue
        out.write(line)
    length = i
    f.close()
    out.close()
    if not os.path.isfile(system_dir+'/'+file):
        print "No answer file found " + system_dir+'/'+file
        print "Skipping the evaluation of it. Fscore set at 0"
        continue
    f = open(system_dir+'/'+file,'r')
    out = open(tmp_folder+'/sys-'+file,'w')
    for i, line in enumerate(f):
        if i == 0:
            continue
        out.write(line)
    f.close()
    out.close()
        
    if (ord):
        command = 'python '+directory_path+'evaluation_timeline_ord.py '+tmp_folder+' gold-'+file +' sys-'+file
        os.system(command)
    else:
        command = 'python '+directory_path+'evaluation_timeline.py '+tmp_folder+' gold-'+file +' sys-'+file
        os.system(command)
    f = open(tmp_folder+'/tmp.out','r')
    for line in f:
        if line.strip()=='':
            continue
        values = line.split("\t")
        valFScore = values[0].strip()
        valPrecision = values[1].strip()
        valRecall = values[2].strip()
        valGlobalPrec = values[3].strip()
        valGlobalSys = values[4].strip()
        valGlobalRec = values[5].strip()
        valGlobalGold = values[6].strip()

        # print str(100*round(fscore, 6))+'\t'+str(100*round(precision, 6))+'\t'+str(100*round(recall, 6))+'\t'+str(global_prec_matched)+'\t'+str(global_system_total)+'\t'+str(global_rec_matched)+'\t'+str(global_gold_total)

        print file+'\tFSCORE\t'+valFScore+'\tPRECISION\t'+valPrecision+'\tRECALL\t'+valRecall
        globalPrec += float(valGlobalPrec)
        globalSys += float(valGlobalSys)
        globalRec += float(valGlobalRec)
        globalGold += float(valGlobalGold)

pmicro = 100*round(globalPrec/globalSys,6)
rmicro = 100*round(globalRec/globalGold,6)
if pmicro+rmicro == 0:
    fmicro = 0
else:
    fmicro = 2.0*pmicro*rmicro/(pmicro+rmicro)
print "\tMICRO-FSCORE\t"+str(fmicro)+"\tMICRO-PRECISION\t"+str(pmicro)+"\tMICRO-RECALL\t"+str(rmicro)
command = 'rm -rf '+tmp_folder    
os.system(command)
