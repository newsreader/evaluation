#!/usr/bin/python 

#WRITTEN BY ANNE-LYSE MINARD, RESEARCHER AT FONDAZIONE BRUNO KESSLER, TRENTO, ITALY.

## input files: CAT XML output
## output: evaluation on markables (entity, event, temporal expression, ...) and relations 
## usage:  
##          python scorer_CAT.py gold_folder_path system_folder_path file_list_markables_relations debug score_file

## debug = 0, no print on the standard output
## debug = 1, prints the final IAA with details 
## debug = 2, prints IAA for each file
## debug = 3, prints TLINK annotation to check problem
## debug = 4, prints triples build from TLINK

import os 
import re
import sys 
import math
import commands 
from xml.dom import minidom
from xml.parsers.expat import ExpatError

import relation_to_timegraph


def get_arg(index):
    return sys.argv[index]

debug = 0

directory_path = '' 

## paramaters ##
relaxed_match = True
evaluation_5_sent = False

## global variables for evaluation 
global_number_files = 0

global_system_markable = {} 
global_gold_markable = {}
global_gold_token = {}
global_system_token = {}
global_markable_strict_match = {}
global_markable_relaxed_match = {} 
global_att_markable_match = {}
global_att_markable_relaxed_match = {}

global_markable_recall = {}
global_markable_precision = {}
global_markable_fmeasure = {}

global_system_relation = {}
global_gold_relation = {}
global_gold_relation_common_markables = {}
global_system_relation_common_markables = {}
global_relation_match = {}
global_att_relation_match = {}
global_relation_relaxed_match = {}
global_att_relation_relaxed_match = {}


global_list_markables_att = {}
global_list_relations_one2one_att = {}
global_list_relations_many2one_att = {}
global_list_instances_att = {}
global_list_annotation_specificity = {}

global_prec_matched_tlink = 0
global_rec_matched_tlink = 0
global_system_total_tlink = 0
global_gold_total_tlink = 0 


correspIdAnnotTokens_gold = {}
correspIdAnnotTokens_sys = {}

markable_id = "id"
token_id = "id"
relation_id = "id"


class markable():
    "defining markable class"
    def __init__(self):
        self.eid = ''
        self.tokenAnchor = []
        self.att = {}

class relation():
    "defining relation class"
    def __init__(self):
        self.rid = ''
        self.source = []
        self.target = []
        self.att = {}

class pairwise():
    "defining one-to-one relation"
    def __init__(self):
        self.id1Gold = ''
        self.id1Sys = ''
        self.id2Gold = ''
        self.id2Sys = ''
        self.att = {}
        self.rid = ''

class instance():
    "defining instance annotation class"
    def __init__(self):
        self.iid = ''
        self.att = {}
        #self.tagD = ''


################ INIT functions #################

def init_global_variable(file_class_att):
    "init to 0 counters"
    global global_gold_markable
    global global_system_markable
    global global_markable_strict_match
    global global_markable_relaxed_match 
    global global_att_markable_match
    global global_att_markable_relaxed_match
    
    read_class_att(file_class_att)

    for eltN in global_list_markables_att:
        global_gold_markable[eltN] = 0
        global_system_markable[eltN] = 0
        global_gold_token[eltN] = 0
        global_system_token[eltN] = 0
        global_markable_strict_match[eltN] = 0
        global_markable_relaxed_match[eltN] = 0
        global_att_markable_match[eltN] = {}
        global_att_markable_relaxed_match[eltN] = {}
        global_markable_recall[eltN] = 0
        global_markable_precision[eltN] = 0
        global_markable_fmeasure[eltN] = 0
        for att in global_list_markables_att[eltN]:
            global_att_markable_match[eltN][att.lower()] = 0
            global_att_markable_relaxed_match[eltN][att.lower()] = 0

    for eltN in global_list_relations_one2one_att:
        global_gold_relation[eltN] = 0
        global_system_relation[eltN] = 0
        global_gold_relation_common_markables[eltN] = 0
        global_system_relation_common_markables[eltN] = 0
        global_relation_match[eltN] = 0
        global_att_relation_match[eltN] = {}
        global_relation_relaxed_match[eltN] = 0
        global_att_relation_relaxed_match[eltN] = {}
        for att in global_list_relations_one2one_att[eltN]:
            global_att_relation_match[eltN][att.lower()] = 0
            global_att_relation_relaxed_match[eltN][att.lower()] = 0

    eltN = "TLINK (strict match)"
    global_gold_relation[eltN] = 0
    global_system_relation[eltN] = 0
    global_gold_relation_common_markables[eltN] = 0
    global_system_relation_common_markables[eltN] = 0
    global_relation_match[eltN] = 0
    global_att_relation_match[eltN] = {}
    global_relation_relaxed_match[eltN] = 0
    global_att_relation_relaxed_match[eltN] = {}
    for att in global_list_relations_one2one_att['TLINK']:
        global_att_relation_match[eltN][att.lower()] = 0
        global_att_relation_relaxed_match[eltN][att.lower()] = 0
  

#init markable id, relation id and token id if labelled xml
def init_id_elt (type_xml):
    global markable_id
    global relation_id
    global token_id
    markable_id = "m_id"
    relation_id = "r_id"
    token_id = "t_id"

#read config file
def read_class_att(filename):
    "read the file with the name of the annotation for which the IAA should be computed"
    global global_list_markables_att
    global global_list_relations_one2one_att
    global global_list_relations_many2one_att
    global global_list_instances_att
    global global_list_annotation_specificity
    fileObj = open( filename, "r")
    type_annot = ''
    for line in fileObj:
        line = line.rstrip('\n')
        if not re.match('^$',line) and not re.match('^#',line):
            elts = re.split('\t',line)
            if len(elts) >= 3:
                eltName = elts[0]
                type_annot = elts[1]
                if type_annot == 'markable':
                    temp = []
                    if len(elts) > 3:
                        for i in range(3,len(elts)):
                            temp.append(elts[i])
                    global_list_markables_att[eltName] = temp
                elif type_annot == 'one2one':
                    global_list_annotation_specificity[eltName] = elts[2]
                    temp = []
                    if len(elts) > 3:
                        for i in range(3,len(elts)):
                            temp.append(elts[i])
                    global_list_relations_one2one_att[eltName] = temp
                elif type_annot == 'instance':
                    global_list_annotation_specificity[eltName] = elts[2]
                    temp = []
                    if len(elts) > 3:
                        for i in range(3,len(elts)):
                            temp.append(elts[i])
                    global_list_instances_att[eltName] = temp
                else:
                    print type_annot, 'is not a authorized type'
            else:
                print 'You must give at least for each markable or relation a name, type and specificity'

    fileObj.close() 


################## functions to get information from the XML parser ####################    

def get_element_value(elt):
    "get the list of token ids that composed the extent of the markable"
    tokenAnchorList = elt.getElementsByTagName('token_anchor') 
    tokenId = []
    for tokA in tokenAnchorList:
        tokenId.append(tokA.getAttribute(token_id))
    return tokenId

def get_element_feat(elt, nameFeat):
    return elt.getAttribute(nameFeat)

def get_token_value(listTokAnchor, listToken):
    text = ''
    for t in listTokAnchor:
        elt = listToken[int(t)-1]
        text += elt.childNodes[0].nodeValue + ' '
    return text

def get_all_element_value(elements, eltName, objectEval, typeFile, listToken):
    "build a list of markable object"
    entityList = []
    entityTokenList = []
    elementsList = elements.getElementsByTagName(eltName)
    for elt in elementsList:
        e = markable()

        e.tokenAnchor = get_element_value(elt)
        e.eid = get_element_feat(elt, markable_id)

        #if eltName != "TIMEX3" or (eltName == "TIMEX3" and (e.eid != "1" or (e.eid == "1" and len(e.tokenAnchor) > 0))) :
        if (eltName != "TIMEX3" and len(e.tokenAnchor) > 0) or eltName == "TIMEX3":
            for objE in objectEval:
                e.att[objE.lower()] = get_element_feat(elt, objE)
            
            if len(e.tokenAnchor) == 1 or (len(e.tokenAnchor) > 1 and int(e.tokenAnchor[1]) == int(e.tokenAnchor[0])+1) or (len(e.tokenAnchor) == 0 and eltName in global_list_instances_att and global_list_annotation_specificity[eltName] == 'comparable'):
                entityList.append(e)
                entityTokenList.append(get_element_value(elt))

                if typeFile == 'gold':
                    if len(e.tokenAnchor) > 0:
                        correspIdAnnotTokens_gold[e.eid] = get_token_value(e.tokenAnchor,listToken)
                    else:
                        correspIdAnnotTokens_gold[e.eid] = get_element_feat(elt,'')
                else:
                    if len(e.tokenAnchor) > 0:
                        correspIdAnnotTokens_sys[e.eid] = get_token_value(e.tokenAnchor,listToken)
                    else:
                        correspIdAnnotTokens_sys[e.eid] = get_element_feat(elt,'')

    return entityList, entityTokenList


def get_all_relation_value(element, eltName, objectEval, list_instances):
    "build a list of relation objects"
    relationList = []
    relationListWoId = []
    elementList = element.getElementsByTagName(eltName)
    for elt in elementList:
        r = relation()
        for objE in objectEval:
            r.att[objE.lower()] = get_element_feat(elt, objE)

        r.rid = get_element_feat(elt, relation_id)
        r.source = get_relation_elt(elt, 'source')
        r.target = get_relation_elt(elt, 'target')

        if len(r.source) > 0 and len(r.target) > 0:
            duplicate = False
            for rel_tmp in relationList:
                if rel_tmp.source == r.source and rel_tmp.target == r.target:
                    duplicate = True

            if not duplicate:
                relationList.append(r)
        
    #if many-to-one relations are expressed by one-to-one relations, then transform one-to-one to many-to-one
    if eltName in global_list_relations_many2one_att:
        relationList = convert_one2one_relation_in_many2one(relationList)
    return relationList
        
    
def get_relation_elt(element, eltName):
    "build a list of the id of eltName contained in element"
    elementList = element.getElementsByTagName(eltName)
    listIdElt = []
    for elt in elementList:
        listIdElt.append(get_element_feat(elt, markable_id))
    return listIdElt


def get_instance(markables):
    "build a dict: key --> instance id; val --> instance object"
    instances_list = {}
    for eltN in global_list_instances_att:
        instance_elt_list = markables.getElementsByTagName(eltN)
        for elt in instance_elt_list:
            inst = instance ()
            inst.iid = get_element_feat(elt, markable_id)
            for att in global_list_instances_att[eltN]:
                inst.att[att] = get_element_feat(elt, att)
            instances_list[inst.iid] = inst
    
    return instances_list
    

def get_relation_common_source_sys(relation_list, correspId, typeData):
    "build a new relation list where relation involving non common sources (= markable match) between gold and system are deleted"
    relation_common_source_gold_sys = []
    for r in relation_list:
        new_relation = relation()
        listSource = []
        for s in r.source:
            if s in correspId:
                if typeData == 'sys':
                    listSource.append(correspId[s])
                else:
                    listSource.append(s)
        new_relation.target = r.target
        new_relation.source = listSource
        new_relation.rid = r.rid
        new_relation.att = r.att
        if len(listSource) > 0:
            relation_common_source_gold_sys.append(new_relation)

    return relation_common_source_gold_sys


def relaxed_match(tokList,tokListSys):
    for t in tokList:
        if t in tokListSys:
            return 1
    return 0


def inArrayPos0 (correspId_array, elt_id):
    for pairs in correspId_array:
        if pairs[0] == elt_id:
            return 1
    return 0


def get_inverse_array (correspId_array):
    correspId_inst_inv = []
    for pairs in correspId_array:
        temp = []
        temp.append(pairs[1])
        temp.append(pairs[0])
        correspId_inst_inv.append(temp)
    return correspId_inst_inv


def get_nb_token(tokens):
    "get number of tokens in the 5 first sentences"
    sent5Find = False
    i = 0
    nb = 0
    while i < len(tokens) and sent5Find == False:
        if tokens[i].getAttribute('sentence') != '0' and tokens[i].getAttribute('sentence') != '6' :
            nb += 1
        if tokens[i].getAttribute('sentence') == '6':
            sent5Find = True
        i += 1

    return nb

#concatenation of two dict
def cat_dict (listDict):
    "cat dicts contained in a list"
    listCat = {}
    for l in listDict:
        for i in l:
            listCat[i] = l[i]
    return listCat



#get the highest id used for the markables
def get_highest_id (markables_g, markables_s):
    highest_id = 0
    for child in markables_g.childNodes:
        if child.nodeType == child.ELEMENT_NODE and (child.tagName == "EVENT" or child.tagName == "TIMEX3"):
            if int(child.getAttribute(markable_id)) > highest_id:
                highest_id = int(child.getAttribute(markable_id))

    for child in markables_s.childNodes:
        if  child.nodeType == child.ELEMENT_NODE and (child.tagName == "EVENT" or child.tagName == "TIMEX3") and int(child.getAttribute(markable_id)) > highest_id:
            highest_id = int(child.getAttribute(markable_id))
       
    return highest_id+1



############# TempEval3 scorer functions ####################

#TempEval3 scorer function
def get_timegraphs(gold, system): 
    gold_text = gold # open(gold).read() # gold #
    system_text = system # open(system).read() # system # 

    tg_gold = relation_to_timegraph.Timegraph() 
    tg_gold = relation_to_timegraph.create_timegraph_from_weight_sorted_relations(gold_text, tg_gold) 
    tg_gold.final_relations = tg_gold.final_relations + tg_gold.violated_relations
    tg_system = relation_to_timegraph.Timegraph() 
    tg_system = relation_to_timegraph.create_timegraph_from_weight_sorted_relations(system_text, tg_system) 
    tg_system.final_relations = tg_system.final_relations + tg_system.violated_relations

    return tg_gold, tg_system 

#TempEval3 scorer function
def get_triples(tlink_file): 
    tlinks = tlink_file # open(tlink_file).read() # tlink_file # 
    relations = '' 
    for line in tlinks.split('\n'): 
        if line.strip() == '': 
            continue 
        if debug >= 4: 
            print 'sending_triples', line 
            
        words = line.split('\t') 
        relations += words[0]+'\t'+words[1]+'\t'+words[2]+'\t'+words[3]+'\n'
        if debug >= 4: 
            print 'received_triples', words[0]+'\t'+words[1]+'\t'+words[2]+'\t'+words[3]+'\n'
        if words[1] != words[2]: 
            relations += words[0]+'\t'+words[2]+'\t'+words[1]+'\t'+reverse_relation(words[3]) +'\n'        
            if debug >= 4: 
                print 'received_triples', words[0]+'\t'+words[2]+'\t'+words[1]+'\t'+reverse_relation(words[3]) +'\n'
    
    return relations 

#TempEval3 scorer function
def get_x_y_rel(tlinks): 
    words = tlinks.split('\t')
    x = words[1]
    y = words[2]
    rel = words[3]
    return x, y, rel 

def get_entity_rel(tlink): 
    words = tlink.split('\t') 
    if len(words) == 3: 
        return words[0]+'\t'+words[1]+'\t'+words[2] 
    return words[1]+'\t'+words[2]+'\t'+words[3] 


#Compute fscore from precision and recall
def get_fscore(p, r):
    "compute fscore from precision and recall"
    if p+r == 0: 
        return 0 
    return 2.0*p*r/(p+r) 


def get_tlink_relations_tempeval_format(relationList, correspId, correspId_inst, typeFile, highest_id):
    fake_id = highest_id
    newtext = ''

    cmpt_new_rel = 0
    cmpt_rel = 0
    for rel_elt in relationList:

        core = [rel_elt.source[0]]
        ref = [rel_elt.target[0]]
        relType = ''

        if typeFile == 'sys':
            if core[0] in correspId:
                core = [correspId[core[0]]]
            elif  inArrayPos0(correspId_inst, core[0]):
                elt_core = core[0]
                core = []
                for pairs in correspId_inst:
                    if pairs[0] == elt_core:
                        core.append(pairs[1])
            else:
                core = [str(fake_id)]

            #if ref in correspId:
            #    ref = correspId[ref]
            if ref[0] in correspId:
                ref = [correspId[ref[0]]]
            elif  inArrayPos0(correspId_inst, ref[0]):
                elt_ref = ref[0]
                ref = []
                for pairs in correspId_inst:
                    if pairs[0] == elt_ref:
                        ref.append(pairs[1])
            else:
                ref = [str(fake_id)]
                
        else:
            if not core[0] in correspId and not inArrayPos0(correspId_inst, core[0]):
                core = [str(fake_id)]
            if not ref[0] in correspId and not inArrayPos0(correspId_inst, ref[0]):
                ref = [str(fake_id)]

        if 'reltype' in rel_elt.att:
            relType = rel_elt.att['reltype']

        if len(core) > 0 and len(ref) > 0 and relType != '':
            cmpt_rel+=1
            for c in core:
                for r in ref:
                    cmpt_new_rel += 1
                    newtext += typeFile+'\t'+c+'\t'+r+'\t'+relType+'\n'
            #newtext += typeFile+'\t'+core+'\t'+ref+'\t'+relType+'\n'
    fake_id += 1

    #diff = number of relations created 
    #in case of empty TIMEX3 that matches more than one empty TIMEX3 
    diff = cmpt_new_rel - cmpt_rel
    return [newtext,diff]

#TempEval3 scorer function
def total_relation_matched(A_tlinks, B_tlinks, B_relations, B_tg): 
    count = 0
    for tlink in A_tlinks.split('\n'):
        if tlink.strip() == '':
            continue 
        x, y, rel = get_x_y_rel(tlink)
        foo = relation_to_timegraph.interval_rel_X_Y(x, y, B_tg, rel, 'evaluation')
        if re.search(get_entity_rel(tlink.strip()), B_relations): 
            count += 1 
            continue 
        if re.search('true', foo[1]):
            count += 1
    return count 

#TempEval3 scorer function
def reverse_relation(rel): 
    rel = re.sub('"', '', rel) 
    if rel.upper() == 'BEFORE': 
        return 'AFTER'
    if rel.upper() == 'AFTER': 
        return 'BEFORE' 
    if rel.upper() == 'IBEFORE': 
        return 'IAFTER' 
    if rel.upper() == 'IAFTER': 
        return 'IBEFORE' 
    if rel.upper() == 'DURING': 
        return 'DURING_INV' 
    if rel.upper() == 'BEGINS': 
        return 'BEGUN_BY' 
    if rel.upper() == 'BEGUN_BY': 
        return 'BEGINS'
    if rel.upper() == 'ENDS': 
        return 'ENDED_BY' 
    if rel.upper() == 'ENDED_BY': 
        return 'ENDS' 
    if rel.upper() == 'INCLUDES': 
        return 'IS_INCLUDED' 
    if rel.upper() == 'IS_INCLUDED': 
        return 'INCLUDES' 
    return rel.upper() 
    #return 'NONE'


#################### functions for computing RECALL and PRECISION ##########################

def compute_recall_precision_tlink_tempeval_format (gold_relationList, sys_relationList, correspId, correspId_inst, highest_id):
    
    global global_prec_matched_tlink
    global global_rec_matched_tlink
    global global_system_total_tlink 
    global global_gold_total_tlink 

    eltName = "TLINK"

    correspId_inst_inv = get_inverse_array(correspId_inst)

    [gold_annotation_tlink, diff_rel_gold] = get_tlink_relations_tempeval_format(gold_relationList, correspId, correspId_inst, 'gold', highest_id)
    [system_annotation_tlink, diff_rel_sys] = get_tlink_relations_tempeval_format(sys_relationList, {v:k for k, v in correspId.items()}, correspId_inst_inv, 'sys', highest_id+200) 

    tg_gold, tg_system = get_timegraphs(gold_annotation_tlink, system_annotation_tlink) 
    gold_relations = get_triples(gold_annotation_tlink) 
    system_relations = get_triples(system_annotation_tlink) 
    
    #for precision
    if debug >= 2: 
        print '\n TLINK'
        print '\nchecking precision' 
    prec_matched = total_relation_matched(tg_system.final_relations, tg_gold.final_relations, gold_relations, tg_gold) 
    # for recall 
    if debug >= 2: 
        print '\nchecking recall' 
    rec_matched = total_relation_matched(tg_gold.final_relations, tg_system.final_relations, system_relations, tg_system) 

    if debug >= 2: 
        print 'precision', rec_matched, len(tg_system.final_relations.split('\n'))-1
    if len(tg_system.final_relations.split('\n')) <= 1: 
        precision = 0 
    else: 
        precision = rec_matched*1.0/(len(tg_system.final_relations.split('\n'))-1-diff_rel_sys)

    if debug >= 2: 
        print 'recall', rec_matched, len(tg_gold.final_relations.split('\n'))-1
    if len(tg_gold.final_relations.split('\n')) <= 1: 
        recall = 0 
    else:
        recall = rec_matched*1.0/(len(tg_gold.final_relations.split('\n'))-1-diff_rel_gold)

    fmeasure = 0
    if recall > 0 and precision > 0:
        fmeasure = 1.0*2*recall*precision/(recall+precision)

    total_relation_match = rec_matched
    total_gold_relation = len(tg_gold.final_relations.split('\n'))-1-diff_rel_gold
    total_system_relation = len(tg_system.final_relations.split('\n'))-1-diff_rel_sys

    if debug >= 2: 
        print '\n',eltName,' PERFORMANCE'
        print 'Strict Recall:', recall
        print 'Strict Precision:', precision
        print 'Strict Fmeasure:', fmeasure

        print 'total gold relations in gold:', total_gold_relation
        print 'total system relations in system:', total_system_relation
        print 'total matching relations:', total_relation_match

        print 'total matching attribute reltype: ',prec_matched

    global_system_relation[eltName] += total_system_relation
    global_gold_relation[eltName] += total_gold_relation
    global_relation_match[eltName] += total_relation_match

    global_att_relation_match[eltName]['reltype'] += prec_matched
    #for objE in objectEval:
    #    global_att_relation_match[eltName][objE.lower()] += total_att_relation_match[objE.lower()]



def compute_precision_recall_relation_one2one (gold_relation, sys_relation, correspId, correspId_inst, objectEval, eltName, type_match):
    "Compute precision, recall and dice's coefficient for the one2one relation"

    global global_system_relation
    global global_gold_relation
    global global_relation_match
    global global_att_relation_match
    global global_relation_relaxed_match
    global global_att_relation_relaxed_match

    total_relation_match = 0
    total_att_relation_match = {}
    
    for objE in objectEval:
        total_att_relation_match[objE.lower()] = 0

    strict_relation_recall = 0
    
    total_gold_relation = 0
    total_system_relation = 0
    
    #correspIdInverse = {v:k for k, v in correspId.items()}

    for r in sys_relation:
        if len(r.source) == 1 and len(r.target) == 1:
            total_system_relation += 1
    
    for r in gold_relation:
        if len(r.source) == 1 and len(r.target) == 1:
            idSource = r.source[0]
            idTarget = r.target[0]
            total_gold_relation += 1

            if (idSource in correspId or inArrayPos0(correspId_inst,idSource)) and (idTarget in correspId or inArrayPos0(correspId_inst,idTarget)) :
                idSourceMatchSys = []
                idTargetMatchSys = []

                if idSource in correspId:
                    idSourceMatchSys.append(correspId[idSource])
                
                if idTarget in correspId:    
                    idTargetMatchSys.append(correspId[idTarget])

                if inArrayPos0(correspId_inst,idSource):
                    for pairs in correspId_inst:
                        if pairs[0] == idSource:
                            idSourceMatchSys.append(pairs[1])

                if inArrayPos0(correspId_inst,idTarget):
                    for pairs in correspId_inst:
                        if pairs[0] == idTarget:
                            idTargetMatchSys.append(pairs[1])

                for r_sys in sys_relation:
                    #undirectional relation
                    if global_list_annotation_specificity[eltName] == 'undirectional':
                        #test if the source and target are the same in both files
                        if len(r_sys.source) == 1 and len(r_sys.target) == 1 and r_sys.source[0] in idSourceMatchSys and r_sys.target[0] in idTargetMatchSys:
                            
                            total_relation_match +=1 #TP

                            for objE in objectEval:
                                if r.att[objE.lower()].upper() == r_sys.att[objE.lower()].upper():
                                    total_att_relation_match[objE.lower()] += 1 #TP att

                        #else test if the source in gold == the target in system and the target in system == the source in gold
                        #in this case the type of the relation has to be reverse (before --> after, ...)
                        elif len(r_sys.source) == 1 and len(r_sys.target) == 1 and r_sys.source[0] in idTargetMatchSys and r_sys.target[0] in idSourceMatchSys:
                            total_relation_match +=1 # TP

                            for objE in objectEval:
                                if r.att[objE.lower()].upper() == reverse_relation(r_sys.att[objE.lower()].upper()) or (reverse_relation(r_sys.att[objE.lower()].upper()) == 'NONE' and r.att[objE.lower()].upper() == r_sys.att[objE.lower()].upper()):
                                    total_att_relation_match[objE.lower()] += 1 #TP att

                    else:
                        if len(r_sys.source) == 1 and len(r_sys.target) == 1 and r_sys.source[0] in idSourceMatchSys and r_sys.target[0] in idTargetMatchSys:
                            total_relation_match +=1 #TP
                            
                            for objE in objectEval:
                                if r.att[objE.lower()].upper() == r_sys.att[objE.lower()].upper():
                                    total_att_relation_match[objE.lower()] += 1 #TP att

    strict_relation_recall = 0 
    if total_gold_relation != 0: 
        strict_relation_recall = 1.0*total_relation_match/total_gold_relation
    
    strict_relation_precision = 0
    if total_system_relation != 0:
        strict_relation_precision = 1.0*total_relation_match/total_system_relation

    strict_relation_fmeasure = 0
    if strict_relation_recall != 0 and strict_relation_precision != 0:
        strict_relation_fmeasure = 1.0*2*strict_relation_recall*strict_relation_precision/(strict_relation_recall+strict_relation_precision)
    
    if eltName == "TLINK":
        eltName = "TLINK (strict match)"

    if debug >= 2: 
        print '\n',eltName,' PERFORMANCE', '(',type_match,')'
        print 'Strict Recall:', strict_relation_recall
        print 'Strict Precision:', strict_relation_precision
        print 'Strict Fmeasure:', strict_relation_fmeasure

        print 'total gold relations in gold:', total_gold_relation
        print 'total system relations in system:', total_system_relation
        print 'total matching relations:', total_relation_match

        for objE in objectEval:
            print 'total matching attribute ', objE, ':', total_att_relation_match[objE.lower()]


    #relaxed match
    if type_match == "relaxed":
        if re.match('TLINK.*',eltName) and "reltype" in total_att_relation_match:
            global_relation_relaxed_match[eltName] += total_att_relation_match['reltype']
            #global_relation_relaxed_match[eltName] += total_relation_match
        else:
            global_relation_relaxed_match[eltName] += total_relation_match

        for objE in objectEval:
            global_att_relation_relaxed_match[eltName][objE.lower()] += total_att_relation_match[objE.lower()]

    #strict match
    else:
        global_system_relation[eltName] += total_system_relation
        global_gold_relation[eltName] += total_gold_relation
        
        if re.match('TLINK.*',eltName) and "reltype" in total_att_relation_match:
            global_relation_match[eltName] += total_att_relation_match['reltype']
            #global_relation_match[eltName] += total_relation_match
        else:
            global_relation_match[eltName] += total_relation_match
        
        for objE in objectEval:
            global_att_relation_match[eltName][objE.lower()] += total_att_relation_match[objE.lower()]
    


def compute_precision_recall(gold_entity, gold_token_entity, system_entity, system_token_entity, objectEval, eltName): 
    "compute the precision, recall and dice's coefficient for markables"
    global global_system_markable
    global global_gold_markable
    global global_markable_strict_match
    global global_markable_relaxed_match
    global global_markable_recall
    global global_markable_precision
    global global_markable_fmeasure

    global global_att_markable_match

    correspEntityId = {}
    correspInstId = []

    correspEntityIdRM = {} #Relaxed match

    pairInstTP = {}

    fake_id = 200

    system_event_handled = {} 

    total_markable_strict_match = 0
    total_markable_relaxed_match = 0
    total_token_strict_match = 0
    total_token_relaxed_match = 0
    token_match = []

    total_att_match = {}
    total_att_match_relaxed = {}

    for objE in objectEval:
        total_att_match[objE.lower()] = 0
        total_att_match_relaxed[objE.lower()] = 0

    total_gold_token = 0
    total_system_token = 0

    gold_entity_empty = []

    #token overlaps = number of tokens annotated in both files as 'eltName'
    list_token_in_markable_extent_gold = []
    list_token_in_markable_extent_system = []
    for tokList in system_token_entity:
        for tok in tokList:
            list_token_in_markable_extent_system.append(tok)
    total_system_token = len(list_token_in_markable_extent_system)

    for tokList in gold_token_entity:
        for tok in tokList:
            list_token_in_markable_extent_gold.append(tok)
    total_gold_token = len(list_token_in_markable_extent_gold)

    total_token_overlaps = 0
    for tok_sys in list_token_in_markable_extent_system:
        if tok_sys in list_token_in_markable_extent_gold:
            list_token_in_markable_extent_gold[list_token_in_markable_extent_gold.index(tok_sys)] = "#" #count only once
            total_token_overlaps += 1
            

    #Exact match = match markable extent
    for i in range(0,len(gold_entity)):
        tokList = gold_entity[i].tokenAnchor
        
        if len(tokList) > 0:
            if tokList in system_token_entity:
                total_markable_strict_match += 1 #TP
                #total_token_strict_match += len(tokList)

                #for tok in tokList:
                    #if not tok in token_match:
                        #token_match.append(tok)

                correspEntityId[gold_entity[i].eid] = system_entity[system_token_entity.index(tokList)].eid

                #relaxed match
                total_markable_relaxed_match += 1 #TP
                correspEntityIdRM[gold_entity[i].eid] = system_entity[system_token_entity.index(tokList)].eid

                for objE in objectEval:
                    if gold_entity[i].att[objE.lower()].upper() == system_entity[system_token_entity.index(tokList)].att[objE.lower()].upper() :
                        total_att_match[objE.lower()] += 1 #TP att
                        total_att_match_relaxed[objE.lower()] += 1 #TP att

            #relaxed match
            else:
                for tokListSys in system_token_entity:
                    if relaxed_match(tokList,tokListSys) and not gold_entity[i].eid in correspEntityIdRM:
                        total_markable_relaxed_match += 1 #TP
                        correspEntityIdRM[gold_entity[i].eid] = system_entity[system_token_entity.index(tokListSys)].eid

                        for objE in objectEval:
                            if gold_entity[i].att[objE.lower()].upper() == system_entity[system_token_entity.index(tokListSys)].att[objE.lower()].upper() :
                                total_att_match_relaxed[objE.lower()] += 1 #TP att


        #Empty tag
        elif eltName in global_list_instances_att and eltName in global_list_annotation_specificity and global_list_annotation_specificity[eltName] == 'comparable':

            for j in range(0,len(system_entity)):
                if len(system_entity[j].tokenAnchor) == 0:
                    
                    allAttMatch = True
                    #match if non-optional attributes match
                    for attName in global_list_instances_att[eltName]:
                        if attName in gold_entity[i].att and gold_entity[i].att[attName].upper() != system_entity[j].att[attName].upper():
                            allAttMatch = False
                        
                    if allAttMatch:

                        alreadyMatch = False
                        if gold_entity[i].eid in pairInstTP or system_entity[j].eid in pairInstTP.values():
                            alreadyMatch = True
                        
                        pairs = []
                        pairs.append(gold_entity[i].eid)
                        pairs.append(system_entity[j].eid)
                        correspInstId.append(pairs)

                        if not alreadyMatch:
                            pairInstTP[gold_entity[i].eid] = system_entity[j].eid
                            total_markable_strict_match += 1 #TP
                            total_markable_relaxed_match += 1 #TP

                            for objE in objectEval:
                                if gold_entity[i].att[objE.lower()].upper() == system_entity[j].att[objE.lower()].upper() :
                                    total_att_match[objE.lower()] += 1 #TP att
                                    total_att_match_relaxed[objE.lower()] += 1 #TP att
                                 
                
    total_gold_markable = len(gold_token_entity) 
    total_system_markable = len(system_token_entity)

    strict_markable_recall = 0 
    if total_gold_markable != 0: 
        strict_markable_recall = 1.0*total_markable_strict_match/total_gold_markable 

    strict_markable_precision = 0
    if total_system_markable != 0:
        strict_markable_precision = 1.0*total_markable_strict_match/total_system_markable
    
    strict_markable_fmeasure = 0
    if strict_markable_precision != 0 and strict_markable_recall != 0:
        strict_markable_fmeasure = 1.0*2*strict_markable_recall*strict_markable_precision/(strict_markable_recall+strict_markable_precision)

    #relaxed match
    relaxed_markable_recall = 0 
    if total_gold_markable != 0: 
        relaxed_markable_recall = 1.0*total_markable_relaxed_match/total_gold_markable 

    relaxed_markable_precision = 0
    if total_system_markable != 0:
        relaxed_markable_precision = 1.0*total_markable_relaxed_match/total_system_markable
    
    relaxed_markable_fmeasure = 0
    if relaxed_markable_precision != 0 and relaxed_markable_recall != 0:
        relaxed_markable_fmeasure = 1.0*2*relaxed_markable_recall*relaxed_markable_precision/(relaxed_markable_recall+relaxed_markable_precision)


    if debug >= 2: 
        print '\n',eltName,' PERFORMANCE'
        print 'Strict Recall:', strict_markable_recall
        print 'Strict Precision:', strict_markable_precision
        print 'Strict F-measure:', strict_markable_fmeasure

        print 'strict count (mention):', total_markable_strict_match
        #print 'strict count (token):', total_token_overlaps
        for objE in objectEval:
            print 'match attribute', objE, ':', total_att_match[objE.lower()]
 
        print 'total annotations in gold:', total_gold_markable
        print 'total annotations in system:', total_system_markable
        print 'total matching ',eltName,':', total_markable_strict_match

        #relaxed match
        print 'Relaxed Recall:', relaxed_markable_recall
        print 'Relaxed Precision:', relaxed_markable_precision
        print 'Relaxed F-measure:', relaxed_markable_fmeasure

        print 'relaxed count (mention):', total_markable_relaxed_match
        for objE in objectEval:
            print 'match attribute', objE, ':', total_att_match_relaxed[objE.lower()]
 
        print 'total matching (relaxed match) ',eltName,':', total_markable_relaxed_match

    global_system_markable[eltName] += total_system_markable 
    global_gold_markable[eltName] += total_gold_markable
    global_markable_strict_match[eltName] += total_markable_strict_match
    global_markable_relaxed_match[eltName] += total_markable_relaxed_match #relaxed match
    global_system_token[eltName] += total_system_token
    global_gold_token[eltName] += total_gold_token
    
    global_markable_recall[eltName] += strict_markable_recall
    global_markable_precision[eltName] += strict_markable_precision
    global_markable_fmeasure[eltName] += strict_markable_fmeasure

    for objE in objectEval:
        global_att_markable_match[eltName][objE.lower()] += total_att_match[objE.lower()]
        global_att_markable_relaxed_match[eltName][objE.lower()] += total_att_match_relaxed[objE.lower()]

    return [correspEntityId,correspEntityIdRM,correspInstId]




#Compute and print the results
def get_performance(): 
    output_text = ''
    output_text += 'number of files: '+str(global_number_files)+'\n'
    
    output_text += '\nMarkables'+'\t'+'TP'+'\t'+'FP'+'\t'+'FN'+'\t'+'recall'+'\t'+'precision'+'\t'+'F1-score'+'\t'+'F1-score attribute'+'\t'


    for eltN in global_list_markables_att:
            
        output_text += '\n'+eltN+'\t'
        output_text += '\t\t\t\t\t\t'
        for att in global_list_markables_att[eltN]:
            output_text += att+'\t'
        output_text += '\n'
        output_text += '\t'
            
        output_text += str(global_markable_strict_match[eltN])+'\t'
        fn = 1.0*(global_gold_markable[eltN]-global_markable_strict_match[eltN])
        fp = 1.0*(global_system_markable[eltN]-global_markable_strict_match[eltN])
        output_text += str(fp)+'\t'+str(fn)+'\t'
        
        micro_a_recall = 0
        if global_gold_markable[eltN] != 0:
            micro_a_recall = 1.0*global_markable_strict_match[eltN]/global_gold_markable[eltN]
        micro_a_precision = 0
        if global_system_markable[eltN] != 0:
            micro_a_precision = 1.0*global_markable_strict_match[eltN]/global_system_markable[eltN]
        micro_a_fmeasure = 0
        if micro_a_recall != 0 and micro_a_precision != 0:
            micro_a_fmeasure = 1.0*2*micro_a_recall*micro_a_precision/(micro_a_recall+micro_a_precision)

        output_text += str(round(micro_a_recall,3))+'\t'+str(round(micro_a_precision,3))+'\t'+str(round(micro_a_fmeasure,3))+'\t'


        if debug >= 2: 
            print 'total gold ',eltN,':', global_gold_markable[eltN]
            print 'total system ',eltN,':', global_system_markable[eltN]
            print 'total matching:', global_markable_strict_match[eltN]

        
        if global_markable_strict_match[eltN] != 0: 
            for att in global_list_markables_att[eltN]:
                accuracy_att = global_att_markable_match[eltN][att]*1.0/global_markable_strict_match[eltN]
                
                if debug >= 2:
                    print 'matching', att, ':', global_att_markable_match[eltN][att]
                f1score_att = accuracy_att*1.0*micro_a_fmeasure
                output_text += str(round(f1score_att,3))+'\t'
        
        #relaxed match
        if relaxed_match:
            output_text += '\n'+eltN+'(relaxed match)\t'
            output_text += '\t\t\t\t\t\t'
            for att in global_list_markables_att[eltN]:
                output_text += att+'\t'
            output_text += '\n'
            output_text += '\t'
            
            output_text += str(global_markable_relaxed_match[eltN])+'\t'
            fn = 1.0*(global_gold_markable[eltN]-global_markable_relaxed_match[eltN])
            fp = 1.0*(global_system_markable[eltN]-global_markable_relaxed_match[eltN])
            output_text += str(fp)+'\t'+str(fn)+'\t'
        
            micro_a_recall = 0
            if global_gold_markable[eltN] != 0:
                micro_a_recall = 1.0*global_markable_relaxed_match[eltN]/global_gold_markable[eltN]
            micro_a_precision = 0
            if global_system_markable[eltN] != 0:
                micro_a_precision = 1.0*global_markable_relaxed_match[eltN]/global_system_markable[eltN]
            micro_a_fmeasure = 0
            if micro_a_recall != 0 and micro_a_precision != 0:
                micro_a_fmeasure = 1.0*2*micro_a_recall*micro_a_precision/(micro_a_recall+micro_a_precision)

            output_text += str(round(micro_a_recall,3))+'\t'+str(round(micro_a_precision,3))+'\t'+str(round(micro_a_fmeasure,3))+'\t'


            if debug >= 2: 
                print 'total gold ',eltN,':', global_gold_markable[eltN]
                print 'total system ',eltN,':', global_system_markable[eltN]
                print 'total matching:', global_markable_relaxed_match[eltN]

        
            if global_markable_relaxed_match[eltN] != 0: 
                for att in global_list_markables_att[eltN]:
                    accuracy_att = global_att_markable_relaxed_match[eltN][att]*1.0/global_markable_relaxed_match[eltN]
                
                    if debug >= 2:
                        print 'matching', att, ':', global_att_markable_match[eltN][att]
                    f1score_att = accuracy_att*1.0*micro_a_fmeasure
                    output_text += str(round(f1score_att,3))+'\t'
        
    #output_text += '\n\n\nRelations'+'\t'+'TP'+'\t'+'FP'+'\t'+'FN'+'\t'+'recall'+'\t'+'precision'+'\t'+'F1-score'+'\t'+'F1-score attribute'+'\t'
    output_text += '\n\n\nRelations'+'\t'+'TP'+'\t'+'FP'+'\t'+'FN'+'\t'+'recall'+'\t'+'precision'+'\t'+'F1-score'+'\t'

    global_list_relations_one2one_att['TLINK (strict match)'] = global_list_relations_one2one_att.get('TLINK')
    for eltN in global_list_relations_one2one_att:
        if eltN == "TLINK":
            output_text += '\n'+eltN+' (tempeval evaluation)\t'
        elif re.match("TLINK .+",eltN):
            output_text += '\n'+'TLINK'+'\t'
        else:
            output_text += '\n'+eltN+'\t'
        output_text += '\t\t\t\t\t\t'
        #for att in global_list_relations_one2one_att[eltN]:
            #output_text += att+'\t'
        output_text += '\n'
        output_text += '\t'

            
        micro_a_recall = 0 
        if global_gold_relation[eltN] != 0: 
            micro_a_recall = 1.0*global_relation_match[eltN]/global_gold_relation[eltN]

        
        micro_a_precision = 0
        if global_system_relation[eltN] != 0: 
            micro_a_precision = 1.0*global_relation_match[eltN]/global_system_relation[eltN]
         
            
        micro_a_fmeasure = 0
        if micro_a_recall != 0 and micro_a_precision != 0:
            micro_a_fmeasure = 1.0*2*micro_a_recall*micro_a_precision/(micro_a_recall+micro_a_precision)

        fp = 1.0*(global_system_relation[eltN]-global_relation_match[eltN])
        fn = 1.0*(global_gold_relation[eltN]-global_relation_match[eltN])
        output_text += str(global_relation_match[eltN])+'\t'+str(fp)+'\t'+str(fn)+'\t'
        output_text += str(round(micro_a_recall,3))+'\t'+str(round(micro_a_precision,3))+'\t'+str(round(micro_a_fmeasure,3))+'\t'
    
        if debug >= 2: 
            print '\n', eltN, 'FEATURE EXTRACTION PERFORMANCE'
            print 'total gold ',eltN,' or total features in gold data:', global_gold_relation[eltN]
            print 'total gold ',eltN,' or total features in system data:', global_system_relation[eltN]
            print 'total matching:', global_relation_match[eltN]

            
        #if global_relation_match[eltN] != 0: 
            #for att in global_list_relations_one2one_att[eltN]:
                #accuracy_att = global_att_relation_match[eltN][att]*1.0/global_relation_match[eltN]
                #if debug >= 2:
                #    print 'matching', att, ':', global_att_relation_match[eltN][att]
                #output_text += str(accuracy_att)+'\t'

        if relaxed_match and global_relation_relaxed_match[eltN] > 0 :
            if re.match("TLINK .+",eltN):
                output_text += '\n'+'TLINK (relaxed match)'+'\t'
            else:
                output_text += '\n'+eltN+'(relaxed match)\t'
            output_text += '\t\t\t\t\t\t'
            #for att in global_list_relations_one2one_att[eltN]:
                #output_text += att+'\t'
            output_text += '\n'
            output_text += '\t'

            micro_a_recall = 0 
            if global_gold_relation[eltN] != 0: 
                micro_a_recall = 1.0*global_relation_relaxed_match[eltN]/global_gold_relation[eltN]

        
            micro_a_precision = 0
            if global_system_relation[eltN] != 0: 
                micro_a_precision = 1.0*global_relation_relaxed_match[eltN]/global_system_relation[eltN]
         
            
            micro_a_fmeasure = 0
            if micro_a_recall != 0 and micro_a_precision != 0:
                micro_a_fmeasure = 1.0*2*micro_a_recall*micro_a_precision/(micro_a_recall+micro_a_precision)

            fp = 1.0*(global_system_relation[eltN]-global_relation_relaxed_match[eltN])
            fn = 1.0*(global_gold_relation[eltN]-global_relation_relaxed_match[eltN])
            output_text += str(global_relation_relaxed_match[eltN])+'\t'+str(fp)+'\t'+str(fn)+'\t'
            output_text += str(round(micro_a_recall,3))+'\t'+str(round(micro_a_precision,3))+'\t'+str(round(micro_a_fmeasure,3))+'\t'
    
            if debug >= 2: 
                print '\n', eltN, 'FEATURE EXTRACTION PERFORMANCE (relaxed match)'
                print 'total gold ',eltN,' or total features in gold data:', global_gold_relation[eltN]
                print 'total gold ',eltN,' or total features in system data:', global_system_relation[eltN]
                print 'total matching:', global_relation_relaxed_match[eltN]

            
            #if global_relation_relaxed_match[eltN] != 0: 
            #    for att in global_list_relations_one2one_att[eltN]:
            #        accuracy_att = global_att_relation_relaxed_match[eltN][att]*1.0/global_relation_relaxed_match[eltN]
            #        if debug >= 2:
            #            print 'matching', att, ':', global_att_relation_relaxed_match[eltN][att]
            #        output_text += str(accuracy_att)+'\t'


    return output_text


def getMarkables5Sent (markable, token_list):
    new_markables_list = []

    list_token_5sent = []
    for tok in token_list:
        if int(tok.getAttribute("sentence")) <= 6:
            list_token_5sent.append(tok.getAttribute("t_id"))

    event_mentions = markable.getElementsByTagName("EVENT_MENTION")
    for ev in event_mentions:
        token_id_m = get_element_value(ev)
        if not token_id_m[0] in list_token_5sent:
            #new_markables_list.append(m)
            markable.removeChild(ev)

    timex = markable.getElementsByTagName("TIMEX3")
    for t in timex:
        token_id_m = get_element_value(t)
        if len(token_id_m) > 0 and not token_id_m[0] in list_token_5sent:
            #new_markables_list.append(m)
            markable.removeChild(t)
        

    return markable

def getRelations5Sent (relations, markable, token_list):
    new_relations_list = []
    
    markables_id = []
    list_event = markable.getElementsByTagName("EVENT_MENTION")
    for m in list_event:
        markables_id.append(m.getAttribute("m_id"))

    list_timex = markable.getElementsByTagName("TIMEX3")
    for m in list_timex:
        markables_id.append(m.getAttribute("m_id"))
        

    tlink = relations.getElementsByTagName("TLINK")
    for rel in tlink:
        out = False
        sources = rel.getElementsByTagName("source")
        if len(sources) == 1:
            if not sources[0].getAttribute("m_id") in markables_id:
                out = True
            if not out:
                targets = rel.getElementsByTagName("target")
                if len(targets) == 1:
                    if not targets[0].getAttribute("m_id") in markables_id:
                        out = True
            if out:
                relations.removeChild(rel)
                
    return relations


#replace some characters if the parsing failed
def convert_data(fileName):
    "Writes datachars to writer."
    f = open(fileName,'r')
    w = open(fileName+'.net', 'w')
    for line in f:
        line = re.sub(r'&([A-Z\s])', r'&amp;\1',line)
        w.write(line)
    f.close()
    w.close()
    os.rename(fileName+'.net', fileName)
    return fileName


def evaluate_two_files2(gold_file, system_file): 
    "eveluate two files" 

    correspId = {}
    correspIdRM = {}
    correspId_inst = []
    print gold_file
    if debug >= 2: 
        print '\nEVALUATION:', system_file, ' VS ', gold_file

    #parse the two files
    try:
        xmldoc_gold = minidom.parse(gold_file)
    except ExpatError:
        gold_file = convert_data(gold_file)
        try:
            xmldoc_gold = minidom.parse(gold_file)
        except ExpatError:
            print gold_file,' not well-formed'
            return False
    try:
        xmldoc_sys = minidom.parse(system_file)
    except ExpatError:
        system_file = convert_data(system_file)
        try:
            xmldoc_sys = minidom.parse(system_file)
        except ExpatError:
            print system_file,' not well-formed'
            return False

    #get elements 'Markables'
    markables_gold = xmldoc_gold.getElementsByTagName('Markables')[0]
    markables_sys_all = xmldoc_sys.getElementsByTagName('Markables')[0]
    
    #get elements 'Relations'
    relations_gold = xmldoc_gold.getElementsByTagName('Relations')[0]
    relations_sys_all = xmldoc_sys.getElementsByTagName('Relations')[0]

    #get tokens
    list_token_gold = xmldoc_gold.getElementsByTagName('token')
    list_token_sys = xmldoc_sys.getElementsByTagName('token')

    #XML labbeled?
    if list_token_gold[0].hasAttribute("t_id"):
        init_id_elt ("labelled")


    #get elements 5 sentences
    if evaluation_5_sent:
        markables_sys = getMarkables5Sent(markables_sys_all, list_token_sys)
        relations_sys = getRelations5Sent(relations_sys_all, markables_sys, list_token_sys)
    else:
        markables_sys = markables_sys_all
        relations_sys = relations_sys_all

    #get instances
    instance_gold = get_instance(markables_gold)
    instance_sys = get_instance(markables_sys)
  
        
    highest_id = get_highest_id(markables_gold, markables_sys)
     
    # markables
    for eltName in global_list_markables_att:
        gold_entity, gold_token_entity = get_all_element_value(markables_gold,eltName,global_list_markables_att[eltName],'gold',list_token_gold)
        sys_entity, sys_token_entity = get_all_element_value(markables_sys,eltName,global_list_markables_att[eltName],'sys',list_token_sys)

        correspId_entity_inst = compute_precision_recall(gold_entity, gold_token_entity, sys_entity, sys_token_entity, global_list_markables_att[eltName], eltName) 
            
        correspId = cat_dict([correspId_entity_inst[0], correspId])
        correspIdRM = cat_dict([correspId_entity_inst[1], correspIdRM]) #relaxed match
        correspId_inst = correspId_inst + correspId_entity_inst[2]
        
    # one2one relation
    for eltName in global_list_relations_one2one_att:
        gold_rel = get_all_relation_value(relations_gold,eltName,global_list_relations_one2one_att[eltName], instance_gold)
        sys_rel = get_all_relation_value(relations_sys,eltName,global_list_relations_one2one_att[eltName], instance_sys)

        if eltName == "TLINK":
            compute_recall_precision_tlink_tempeval_format(gold_rel, sys_rel, correspId, correspId_inst, highest_id)
            #else: 
        compute_precision_recall_relation_one2one(gold_rel, sys_rel, correspId, correspId_inst, global_list_relations_one2one_att[eltName], eltName, 'strict')

        compute_precision_recall_relation_one2one(gold_rel, sys_rel, correspIdRM, correspId_inst, global_list_relations_one2one_att[eltName], eltName, 'relaxed')

    return '' 



def evaluate_two_folders(gold, system):
    global global_number_files
    if gold[-1] != '/': 
        gold += '/' 
    if system[-1] != '/': 
        system += '/' 
    for file in os.listdir(gold):
        if os.path.isdir(gold+file):
            subdir = file+'/'
            if debug >= 1: 
                print 'Traverse files in Directory', gold+subdir
            evaluate_two_folders(gold+subdir, system+subdir)
        else:
            goldfile = gold +  file
            #systemfile = system + file 
            if not re.search('DS_Store', file) and goldfile.endswith('.xml'): 
                global_number_files += 1
                #systemfile = systemfile.replace(".txt","")
                #systemfile = systemfile.replace(".xml","")
                systemfile = ""
                num_file = extract_name(goldfile)
                num_file = re.sub(r"^(\d+)(\_|\-).+$",r"\1",num_file)
                #print num_file
                for f in os.listdir(system):
                    if re.search(num_file,f):
                        systemfile = system + f
                        
                #print goldfile
                evaluate_two_files2(goldfile, systemfile)



def extract_name(filename):
    parts = re.split('/', filename)
    length = len(parts)
    return parts[length-1]

def get_directory_path(path): 
    name = extract_name(path)
    dir = re.sub(name, '', path) 
    if dir == '': 
        dir = './'
    return dir 


# take input from command line and give error messages 
# call appropriate functions to evaluate 
def input_and_evaluate():
    global global_number_files
    global debug

    invalid = 'false' 
    if len(sys.argv) < 4: 
        invalid = 'true' 
    else: 
        arg1 = get_arg(1) 
        arg2 = get_arg(2) 
        global directory_path 
        directory_path = get_directory_path(sys.argv[0])

        if len(sys.argv) > 4 and re.match("[0-9]", get_arg(4)): 
            debug = float(get_arg(4))

        init_global_variable(get_arg(3))
        
    # both arguments are directories 
    if invalid == 'false' and os.path.isdir(arg1) and os.path.isdir(arg2): 
        # for each files in gold folder, check the performance of that file in system folder 
        if debug >= 2: 
            print 'compare files in two folders' 
        evaluate_two_folders(arg1, arg2)
    elif invalid == 'false' and os.path.isfile(arg1) and os.path.isfile(arg2) and arg1.endswith('.xml') and arg2.endswith('.xml'): 
        # compare the performance between two files 
        if debug >= 2: 
            print 'compare two files'
        global_number_files = 1
        evaluate_two_files2(arg1, arg2)
    else: 
        invalid = 'true' 
        print 'INVALID INPUT FORMAT'
        print '\nto check the performance of a single file:\n\t python scorer_CAT.py gold_file_path system_file_path list_annotation_file debug result_file\n' 
        print 'to check the performace of all files in a gold folder:\n\t python scorer_CAT.py gold_folder_path system_folder_path list_annotation_file debug  result_file\n\n'
    
    if invalid == 'false': 
        output_text = get_performance()

        fileOut = ""
        
        if len(sys.argv) > 4:
            if re.match("[0-9]",get_arg(4)) and len(sys.argv) > 5:
                fileOut = get_arg(5)
            elif not re.match("[0-9]",get_arg(4)):
                fileOut = get_arg(4)
          
        #print fileOut
        if not fileOut == "":
            f = open(fileOut,'w')
            f.write(output_text)
            f.close()
        else:
            print output_text


input_and_evaluate()
