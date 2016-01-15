#!/usr/bin/python 

b'You need Python 2.6 or later.'

import sys
import os
import tempfile
import errno
import re
import subprocess

tmp_folder = sys.argv[1]
gold_file = sys.argv[2]
system_file = sys.argv[3]

gold_event_list = []
gold_event_id = []

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def order_timeline(text):
    lines = text.split('\n')
    non_empty = [line.rstrip() for line in lines if line.strip()]
    non_empty.sort(key=natural_keys)
    return '\n'.join(non_empty)

def init_file(out,docId):
    out.write('<?xml version="1.0" ?><TimeML xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd">\n')
    out.write('<DOCID>'+docId+'</DOCID>\n')
    out.write('<DCT></DCT>\n')
    out.write('<TEXT>\n')

def end_text_file(out):
    out.write('</TEXT>\n')

def finalize_file(out):
    out.write('</TimeML>\n')

def create_gold_tml(timeline):
    out = open(tmp_folder+'/'+gold_file+'_gold.tml', 'w')
    init_file(out,'GOLD')
    gold_event_dict = {}

    eid = 1
    for line in timeline.split('\n'):
        if line.strip() == '': 
            continue 
        info = line.split('\t')

        if len(info) < 3:
            continue

        order = info[0]

        if int(order) == 0:
            continue

        for i in range(2, len(info)):
            event = info[i]
            out.write('<EVENT class="OCCURRENCE" eid="e'+str(eid)+'">'+event+'</EVENT>\n')
            gold_event_dict[str(eid)+'-order'] = order
            gold_event_list.append(event)
            gold_event_id.append(eid)
            eid += 1           
    end_text_file(out)

    lid = 1
    for i in range(0, len(gold_event_list)):
        event = gold_event_list[i]
        eventId = gold_event_id[i]

        out.write('<MAKEINSTANCE aspect="NONE" eiid="ei'+str(eventId)+'" eventID="e'+str(eventId)+'" polarity="" pos="" tense=""/>\n')

    for i in range(0, len(gold_event_id)-1):
        order1 = int(gold_event_dict[str(gold_event_id[i])+'-order'])
        order2 = int(gold_event_dict[str(gold_event_id[i+1])+'-order'])

        if order1 < order2:
            out.write('<TLINK lid="l'+str(lid)+'" eventInstanceID="ei'+str(i+1)+'" relatedToEventInstance="ei'+str(i+2)+'" relType="BEFORE"/>\n')
        else:
            out.write('<TLINK lid="l'+str(lid)+'" eventInstanceID="ei'+str(i+1)+'" relatedToEventInstance="ei'+str(i+2)+'" relType="SIMULTANEOUS"/>\n')
        lid += 1


    finalize_file(out)
    out.close()

def create_system_tml(timeline):
    out = open(tmp_folder+'/'+system_file+'_sys.tml', 'w')
    init_file(out,'SYSTEM')
    maxEID = len(gold_event_list) + 1
    event_list = []
    event_id = []
    event_dict = {}
    
    for line in timeline.split('\n'):
        if line.strip() == '':
            continue
        info = line.split('\t')
        if len(info) < 3:
            continue

        order = info[0]
        if int(order) == 0:
            continue
            
        for i in range(2, len(info)):
            event = info[i]
            eid = -1
            if (gold_event_list.count(event) < 1):
                eid = maxEID
                maxEID += 1
            else:
                # the event is in the gold-standard (at least one)
                if (event_list.count(event) < 1):
                    eid = gold_event_id[gold_event_list.index(event)]
                else:
                    # same event already in the timeline, get the next one
                    # if there is one
                    next = event_list.count(event)
                    idx = gold_event_list.index(event)
                    #if event_list.count(event) > (idx+next):
                    if event_list.count(event) < gold_event_list.count(event):
                        pos = gold_event_list.index(event,idx+next)
                        eid = gold_event_id[pos]          
                    else:
                        eid = maxEID
                        maxEID += 1
            out.write('<EVENT class="OCCURRENCE" eid="e'+str(eid)+'">'+event+'</EVENT>\n')
            event_dict[str(eid)+'-order'] = order
            event_list.append(event)
            event_id.append(eid)

    end_text_file(out)

    lid = 1
    for i in range(0, len(event_list)):
        event = event_list[i]
        eventId = event_id[i]
        out.write('<MAKEINSTANCE aspect="NONE" eiid="ei'+str(eventId)+'" eventID="e'+str(eventId)+'" polarity="" pos="" tense=""/>\n')

    for i in range(0, len(event_id)-1):
        order1 = int(event_dict[str(event_id[i])+'-order'])
        order2 = int(event_dict[str(event_id[i+1])+'-order'])

        if order1 < order2:
            out.write('<TLINK lid="l'+str(lid)+'" eventInstanceID="ei'+str(event_id[i])+'" relatedToEventInstance="ei'+str(event_id[i+1])+'" relType="BEFORE"/>\n')
        else:
            out.write('<TLINK lid="l'+str(lid)+'" eventInstanceID="ei'+str(event_id[i])+'" relatedToEventInstance="ei'+str(event_id[i+1])+'" relType="SIMULTANEOUS"/>\n')
        lid += 1



    finalize_file(out)
    out.close()


#The gold timeline comes ordered. If not, call the script for ordering timelines: order_timeline
# gold_timeline = open(tmp_folder+'/'+gold_file).read()
# create_gold_tml(gold_timeline)
gold_text = open(tmp_folder+'/'+gold_file).read()
gold_timeline = order_timeline(gold_text)
create_gold_tml(gold_timeline)

system_text = open(tmp_folder+'/'+system_file).read()
system_timeline = order_timeline(system_text)
create_system_tml(system_timeline)

command = 'python temporal_evaluation.py '+tmp_folder+'/'+gold_file+'_gold.tml '+tmp_folder+'/'+system_file+'_sys.tml 0 > '+tmp_folder+'/tmp.out'
os.system(command) 

