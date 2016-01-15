#!/usr/bin/python2.6

#usage: python CAT_to_evaluation_formats.py [CAT files or folder] [output_folder] [lang] [SRL, NER] 
#version 5: add option language

import os 
import re
import sys 
import math
import commands
import codecs
from xml.dom import minidom

##### Parameters #####
type_annotation = "all" #BIO-smallest: annotate inner extents; BIO-biggest: annotate outer extents; all: annotate all (multi columns output)

all_ent_types = False #if False only ORG, LOC and PER, else also FIN and PRO
all_synt_types = False #if False only NAM and PRE.NAM, else all (some problem to resolve if True)

lang = "en"
layer = ""
#####


markable_id = "m_id"
relation_id = "r_id"
token_id = "t_id"


nb_per = 0
nb_loc = 0
nb_org = 0

def get_arg(index):
    return sys.argv[index]


# take input from command line and give error messages 
# call appropriate functions to evaluate 
def input_and_evaluate(): 
    global all_ent_types
    global all_synt_types
    global type_annotation
    global lang
    global layer

    invalid = 'false' 
    arg1 = get_arg(1) 
    global directory_path 
    directory_path = get_directory_path(sys.argv[0])

    id_arg_layer = 3

    if len(get_arg(3)) == 2 and get_arg(3) in ("es","en","it","nl"):
        lang = get_arg(3)
        id_arg_layer = 4

    if get_arg(id_arg_layer) == "SRL":
        all_ent_types = True
        all_synt_types = True
        type_annotation = "all"
        
    elif get_arg(id_arg_layer) == "NER" and len(sys.argv) > id_arg_layer:
        if get_arg(id_arg_layer+1) == "inner":
            type_annotation = "BIO-smallest"
        elif get_arg(id_arg_layer+1) == "outer":
            type_annotation = "BIO-biggest"
    
    elif get_arg(id_arg_layer) == "NER":
        type_annotation = "all"

    layer = get_arg(id_arg_layer)

    # both arguments are directories 
    if os.path.isdir(arg1):
        evaluate_folder(arg1)
    elif os.path.isfile(arg1):
        read_CAT_file(arg1)

     
def evaluate_folder(repName):
    if repName[-1] != '/': 
        repName += '/' 
    for file in os.listdir(repName):
        if os.path.isdir(repName+file):
            subdir = file+'/'
            if debug >= 1: 
                print 'Traverse files in Directory', gold+subdir
            evaluate_folder(repName+subdir)
        else:
            fileName = repName +  file
            if not re.search('DS_Store', file): 
                read_CAT_file(fileName)

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

class instance():
    "defining instance annotation class"
    def __init__(self):
        self.iid = ''
        self.att = {}
        self.tagDesc = ''


def get_element_value(elt):
    "get the list of token ids that composed the extent of the markable"
    tokenAnchorList = elt.getElementsByTagName('token_anchor') 
    tokenId = []
    for tokA in tokenAnchorList:
        tokenId.append(tokA.attributes[token_id].value)
    return tokenId


def get_element_feat(elt, nameFeat):
    if elt.hasAttribute(nameFeat):
        return elt.getAttribute(nameFeat)
    else:
        return ""


def get_token_value(listTokAnchor, listToken):
    text = ''
    for t in listTokAnchor:
        elt = listToken[int(t)-1]
        text += elt.childNodes[0].nodeValue + ' '
    return text

#get a dict: key -> token id, value -> token text
def get_list_tokenId_value(listToken):
    list_tokenId_value = {}
    for t in listToken:
        list_tokenId_value[t.getAttribute(token_id)] = t.childNodes[0].nodeValue
    return list_tokenId_value

def get_all_element_value(elements, eltName, objectEval):
    "build a list of markable object"
    entityList = []
    entityTokenList = []
    elementsList = elements.getElementsByTagName(eltName)
    for elt in elementsList:
        e = markable()

        e.tokenAnchor = get_element_value(elt)
        e.eid = get_element_feat(elt, markable_id)
        
        for objE in objectEval:
            e.att[objE] = get_element_feat(elt, objE)
            if e.att[objE] == "" and get_arg(3) == "factuality":
                e.att[objE] = "O"
            
        if len(e.tokenAnchor) > 0 and (not "syntactic_type" in e.att or all_synt_types or (e.att["syntactic_type"] == "NAM" or e.att["syntactic_type"] == "PRE.NAM")):
#        if len(e.tokenAnchor) > 0 and (not "syntactic_type" in e.att or all_synt_types or (e.att["syntactic_type"] == "NAM")):
        #if len(e.tokenAnchor) > 0:
            entityList.append(e)

    return entityList


def get_all_relation_value(element, eltName, objectEval):
    "build a list of relation objects"
    relationList = []
    elementList = element.getElementsByTagName(eltName)
    for elt in elementList:
        r = relation()
        for objE in objectEval:
            r.att[objE] = get_element_feat(elt, objE)
        
        r.rid = get_element_feat(elt, relation_id)
        r.source = get_relation_elt(elt, 'source')
        r.target = get_relation_elt(elt, 'target')

        
        if len(r.source) > 0 and len(r.target) > 0:
            relationList.append(r)

    return relationList
        
    
def get_relation_elt(element, eltName):
    "build a list of the id of eltName contained in element"
    elementList = element.getElementsByTagName(eltName)
    listIdElt = []
    for elt in elementList:
        listIdElt.append(get_element_feat(elt, markable_id))
    return listIdElt


def get_instance(markables, eltN, att):
    "build a dict: key --> instance id; val --> instance object"
    instances_list = {}
    instance_elt_list = markables.getElementsByTagName(eltN)
    for elt in instance_elt_list:
        inst = instance ()
        inst.iid = get_element_feat(elt, markable_id)
        inst.att[att] = get_element_feat(elt, att)
        inst.tagDesc = get_element_feat(elt, 'TAG_DESCRIPTOR')
            #inst.att = get_element_feat(ev, 'class')
        instances_list[inst.iid] = inst
    
    return instances_list

#build a dict: key --> markable id (EVENT_MENTION or ENTITY_MENTION), value --> class (PRO, PER, ORG, ...)    
def get_mention_class(instances_list, refers_to_list, att):
    mention_id_class_list = {}
    for rel in refers_to_list:
        if len(rel.target) == 1:
            target = rel.target[0]
            if target in instances_list:
                sources = rel.source
                for src in sources:
                    if instances_list[target].att[att] != "" and ((instances_list[target].att[att] != "PRO" and instances_list[target].att[att] != "FIN") or (all_ent_types == True)):
                    #if instances_list[target].att[att] != "" and (instances_list[target].att[att] != "PRO" or all_ent_types == True):
                        #if not instances_list[target].att[att] == "FIN":
                        mention_id_class_list[src] = instances_list[target].att[att]
                        #else:
                        #mention_id_class_list[src] = "ORG"

    return mention_id_class_list

#get the document creation time of the document
def get_DCT_timex(list_timex):
    for t in list_timex:
        if "functionInDocument" in t.att and t.att["functionInDocument"] == "CREATION_TIME":
            return t.att["value"]
    return "0"


#build a dict: key --> token id, value --> list of markables containing this token
def get_list_markable_tok_id (list_mention, list_ment_class):
    list_id = {}
    for ment in list_mention:
        if ment.eid in list_ment_class and (ment.att["syntactic_type"] == "NAM" or ment.att["syntactic_type"] == "PRE.NAM" or all_synt_types == True):
#         if ment.eid in list_ment_class and (ment.att["syntactic_type"] == "NAM" or all_synt_types == True):
            for tok in ment.tokenAnchor:
                if tok in list_id:
                    list_id[tok].append(ment)
                else:
                    list_id[tok] = [ment]

    for tok_id in list_id:
        if len(list_id[tok_id]) > 1:
            new_list_ment = sorted (list_id[tok_id], key=lambda l: len(l.tokenAnchor), reverse=True)
            list_id[tok_id] = new_list_ment
            #ment1 = list_id[tok_id][0]
            #ment2 = list_id[tok_id][1]
            #if ment1.eid in list_ment_class and ment2.eid in list_ment_class and list_ment_class[ment1.eid] == list_ment_class[ment2.eid] and (ment1.att["syntactic_type"] == "NAM" or ment1.att["syntactic_type"] == "PRE.NAM") and (ment2.att["syntactic_type"] == "NAM" or ment2.att["syntactic_type"] == "PRE.NAM"):
            #    print ment1.eid+" : "+ment2.eid+" --> "+list_ment_class[ment1.eid]
            #    if len(list_id[tok_id]) > 2:
            #        print "> 2"
    #list_id = sort_list_markable_extent(list_id)
    return list_id


#build a dict: key --> token id, value --> list of markables containing this token
def get_list_markable_tok_id_srl (list_mention):
    list_id = {}
    for ment in list_mention:
        prev_id = -1
        conj = False
        for tok in ment.tokenAnchor:
            if prev_id > -1 and int(tok) != prev_id+1:
                conj = True
            prev_id = int(tok)

        if not conj:
            for tok in ment.tokenAnchor:
                if tok in list_id:
                    list_id[tok].append(ment)
                else:
                    list_id[tok] = [ment]
    return list_id


#build a dict: key --> token id, value --> list of markables containing this token
def get_list_markable_smallest_biggest_bis (list_mention, list_ment_class, size):
    list_id = {}
    for ment in list_mention:
        if ment.eid in list_ment_class and (ment.att["syntactic_type"] == "NAM" or ment.att["syntactic_type"] == "PRE.NAM" or all_synt_types == True):
#        if ment.eid in list_ment_class and (ment.att["syntactic_type"] == "NAM" or all_synt_types == True):
            for tok in ment.tokenAnchor:
                if tok in list_id:
                    list_id[tok].append(ment)
                else:
                    list_id[tok] = [ment]

    for tok_id in list_id:
        if len(list_id[tok_id]) > 1:
            new_list_ment = sorted (list_id[tok_id], key=lambda l: len(l.tokenAnchor), reverse=True)
            if size == "smallest" :
                list_id[tok_id] = [new_list_ment[len(new_list_ment)-1]]
            else:
                list_id[tok_id] = [new_list_ment[0]]
            #list_id[tok_id] = new_list_ment
            
    return list_id

#For each token part of more than on markable, sort the markables according to their size
def sort_list_markable_extent (list_tok_id_mark):
    for tok_id in list_tok_id_mark:
        if len(list_tok_id_mark[tok_id]) > 1:
            ment1 = list_tok_id_mark[tok_id][0]
            ment2 = list_tok_id_mark[tok_id][1]
            
            if len(ment1.tokenAnchor) < len(ment2.tokenAnchor):
                list_tok_id_mark[tok_id][0] = ment2
                list_tok_id_mark[tok_id][1] = ment1

            if len(list_tok_id_mark[tok_id]) > 2:
                ment3 = list_tok_id_mark[tok_id][2]
                if len(ment3.tokenAnchor) > len(list_tok_id_mark[tok_id][0].tokenAnchor) and len(ment3.tokenAnchor) < len(list_tok_id_mark[tok_id][1].tokenAnchor):
                    list_tok_id_mark[tok_id][2] = list_tok_id_mark[tok_id][1]
                    list_tok_id_mark[tok_id][1] = ment3
                elif len(ment3.tokenAnchor) < len(list_tok_id_mark[tok_id][0].tokenAnchor):
                    list_tok_id_mark[tok_id][2] = list_tok_id_mark[tok_id][1]
                    list_tok_id_mark[tok_id][1] = list_tok_id_mark[tok_id][0]
                    list_tok_id_mark[tok_id][0] = ment3

    return list_tok_id_mark
                    

#build a dict: key --> token id, value --> list of markables containing this token (either the biggest extent (APP, CONJ, etc.) or smallest)
def get_list_smallest_biggest_markable_tok_id (list_mention, size):
    list_id = {}
    list_mention_selected = []
    for m in range(0,len(list_mention)):
        token_anchor = list_mention[m].tokenAnchor
        
        smallest = True
        biggest = True

        for mm in range(0,len(list_mention)):
            token_anchor_2 = list_mention[mm].tokenAnchor
            if m != mm and int(token_anchor[0]) <= int(token_anchor_2[0]) and int(token_anchor[len(token_anchor)-1]) >= int(token_anchor_2[len(token_anchor_2)-1]):
                smallest = False
            if m != mm and int(token_anchor_2[0]) <= int(token_anchor[0]) and int(token_anchor_2[len(token_anchor_2)-1]) >= int(token_anchor[len(token_anchor)-1]): 
                biggest = False

        if smallest and size == "smallest":
            list_mention_selected.append(list_mention[m])
        elif biggest and size == "biggest":
            list_mention_selected.append(list_mention[m])

    for ment in list_mention_selected:
        for tok in ment.tokenAnchor:
            if tok in list_id:
                list_id[tok].append(ment)
            else:
                list_id[tok] = [ment]
    return list_id


#build a dict: key --> token id, value --> timex containing this token
def get_list_timex_by_tokId(list_timex):
    list_by_tokId = {}
    for timex in list_timex:
        list_tok = timex.tokenAnchor
        for tok in list_tok:
            list_by_tokId[tok] = timex

    return list_by_tokId

#get the type of a timex from the token id
def get_type_timex(tokId, timex, attType):
    list_tok = timex.tokenAnchor
    if len(list_tok) == 1:
        return "B-"+timex.att[attType]
    else:
        i = 0
        for tok in list_tok:
            if tok == tokId:
                if i==0:
                    return "B-"+timex.att[attType]
                else:
                    return "I-"+timex.att[attType]
            i+=1
    return "O"


#Return True if the event containing the given token id is involved in HAS_PARTICIPANT relations
def isEventHasPart(list_has_part, tok_id, list_event_tok_id):
    if tok_id in list_event_tok_id:
        list_ev_id = list_event_tok_id[tok_id]
        for ev_id in list_ev_id:
        #ev_id = list_event_tok_id[tok_id][0]
            for rel in list_has_part:
                if rel.source[0] == ev_id.eid:
                    return True
    return False
    

#build a dict: key --> markable id (entity involved in a HAS_PART relation), value -> semRole
def getHasPartRoles(list_has_part, tok_id, list_entity_tok_id, list_entityId_head):
    list_pred_roles = {}
    for rel in list_has_part:
        for entity in list_entity_tok_id[tok_id]:
            if rel.target[0] == entity.eid and (not entity.eid in list_entityId_head or tok_id in list_entityId_head[entity.eid]):
                list_pred_roles[rel.source[0]] = rel.att['sem_role']
    return list_pred_roles


#build a dict: key --> markable id (entity involved in a HAS_PART relation), value -> semRole
def getHasPartRoles_conll05(list_has_part, tok_id, list_entity_tok_id, list_entityId_head):
    list_pred_roles = {}
    for rel in list_has_part:
        if tok_id in list_entity_tok_id:
            for entity in list_entity_tok_id[tok_id]:
                if rel.target[0] == entity.eid and (not entity.eid in list_entityId_head or tok_id in list_entityId_head[entity.eid]):
                    if tok_id == entity.tokenAnchor[0] and len(entity.tokenAnchor) == 1:
                        list_pred_roles[rel.source[0]] = "("+rel.att['sem_role']+"*)"
                    elif tok_id == entity.tokenAnchor[0]:
                        list_pred_roles[rel.source[0]] = "("+rel.att['sem_role']+"*"
                    elif len(entity.tokenAnchor) > 1 and tok_id == entity.tokenAnchor[len(entity.tokenAnchor)-1]:
                        list_pred_roles[rel.source[0]] = "*)"
                    else:
                        list_pred_roles[rel.source[0]] = "*"
                #list_pred_roles[rel.source[0]] = rel.att['sem_role']
    return list_pred_roles


#Using the syntactic_type and head attributes build a dict: key --> entity id, value --> the head of the entity or the nested entities of a APP or CONJ entity
def getEntityIdHead_old(list_entity, list_tok_value):
    entityIdHead = {}

    for ent in list_entity:
        synt_type = ent.att["syntactic_type"]
        if synt_type != "":

            if synt_type == "APP" or synt_type == "CONJ" or synt_type == "ARC":
                for nested_ent in list_entity:
                    if nested_ent.tokenAnchor[0] in ent.tokenAnchor and (nested_ent.att["syntactic_type"] == "NAM" or nested_ent.att["syntactic_type"] == "NOM"):
                    #if nested_ent.tokenAnchor[0] in ent.tokenAnchor:
                        noHeadEnt = False
                        if nested_ent.att["head"] != "":
                            j = 0
                            tok_head = nested_ent.att["head"].lower().split(" ")
                            
                            tok_toadd = []
                            for tok in nested_ent.tokenAnchor:
                                if j < len(tok_head) and tok in list_tok_value and (list_tok_value[tok].lower() in tok_head[j] or tok_head[j] in list_tok_value[tok].lower()):
                                    tok_toadd.append(tok)
                                    j+=1
                            if j < len(tok_head):
                                noHeadEnt = True
                            else:
                                if ent.eid in entityIdHead:
                                    entityIdHead[ent.eid] += tok_toadd
                                else:
                                    entityIdHead[ent.eid] = tok_toadd
                                    
                        if nested_ent.att["head"] == "" or noHeadEnt:
                            if ent.eid in entityIdHead:
                                entityIdHead[ent.eid] += nested_ent.tokenAnchor
                            else:
                                entityIdHead[ent.eid] = nested_ent.tokenAnchor
                        
        if not ent.eid in entityIdHead:
            j = 0
            if ent.att["head"] != "":
                tok_head = ent.att["head"].lower().split(" ")
                #print ent.att["head"], str(len(tok_head))
                for tok in ent.tokenAnchor:
                    if j < len(tok_head) and tok in list_tok_value and (list_tok_value[tok].lower() in tok_head[j] or tok_head[j] in list_tok_value[tok].lower()) :
                        if ent.eid in entityIdHead:
                            entityIdHead[ent.eid].append(tok)
                        else:
                            entityIdHead[ent.eid] = [tok]
                        j+=1
                if j < len(tok_head):
                    entityIdHead.pop(ent.eid, None)
            else:
                entityIdHead[ent.eid] = ent.tokenAnchor

    return entityIdHead


#Using the syntactic_type and head attributes build a dict: key --> entity id, value --> the head of the entity or the nested entities of a APP or CONJ entity
def getEntityIdHead(list_entity, list_tok_value):
    entityIdHead = {}

    for ent in list_entity:
        synt_type = ent.att["syntactic_type"]

        j = 0
        if ent.att["head"] != "":
            tok_head = ent.att["head"].lower().split(" ")
            #print ent.att["head"], str(len(tok_head))
            for tok in ent.tokenAnchor:
                if j < len(tok_head) and tok in list_tok_value and (list_tok_value[tok].lower() in tok_head[j] or tok_head[j] in list_tok_value[tok].lower()) :
                    if ent.eid in entityIdHead:
                        entityIdHead[ent.eid].append(tok)
                    else:
                        entityIdHead[ent.eid] = [tok]
                    j+=1
            if j < len(tok_head):
                entityIdHead.pop(ent.eid, None)
        else:
            entityIdHead[ent.eid] = ent.tokenAnchor

    return entityIdHead


def convertSRL(list_token, list_has_part, list_event_tok_id, list_entity_tok_id, list_entityId_head):
    global lang
    numSent = "0"
    content = []
    j = 0
    list_pred = {}
    list_pred_rev = {}
    cpt_pred = 0
    first_tok_sent = 0

    for tok in list_token:
        if tok.firstChild:
            if int(tok.getAttribute('sentence')) != int(numSent):
                content.insert(j,[""])
                j+=1
                for h in range(first_tok_sent,j-1):
                    for e in range(14,len(list_pred_rev)+14):
                        content[h].insert(e,'_')

                    if len(content[h])>1 and content[h][0] in list_entity_tok_id:
                        list_roles_tok = getHasPartRoles(list_has_part,content[h][0],list_entity_tok_id,list_entityId_head)
                        for pred in list_roles_tok:
                            if pred in list_pred_rev:
                                if list_roles_tok[pred] != "":
                                    if lang == "es":
                                        content[h][list_pred_rev[pred]+14] = list_roles_tok[pred].replace("Arg","arg")
                                    else:
                                        content[h][list_pred_rev[pred]+14] = list_roles_tok[pred].replace("Arg","A")
                
                list_pred = {}
                list_pred_rev = {}
                cpt_pred = 0
                first_tok_sent = j

            
            content.insert(j,[tok.getAttribute(token_id)])#ID
            content[j].append(tok.firstChild.nodeValue)#form
            
            #lemma, plemma, pos, ppos, feat, pfeat, head, phead, deprel, pdeprel
            for c in range(0,10):
                content[j].append("_")

            if isEventHasPart(list_has_part,tok.getAttribute(token_id),list_event_tok_id) and not list_event_tok_id[tok.getAttribute(token_id)][0].eid in list_pred_rev:
                
                event = list_event_tok_id[tok.getAttribute(token_id)]
                tok_anchor = event[0].tokenAnchor
                if len(tok_anchor)>1:
                    ev_text = get_token_value(tok_anchor, list_token)
                    ev_text = ev_text.replace(" ","_")
                    ev_text = ev_text[:-1]
                    content[j].append("Y")
                    content[j].append(ev_text.lower()+".01")
                else:
                    content[j].append("Y")
                    content[j].append(tok.firstChild.nodeValue.lower()+".01")
                list_pred[j] = list_event_tok_id[tok.getAttribute(token_id)][0].eid
                list_pred_rev[list_event_tok_id[tok.getAttribute(token_id)][0].eid] = cpt_pred
                cpt_pred+=1
              
            elif tok.getAttribute(token_id) in list_event_tok_id and not list_event_tok_id[tok.getAttribute(token_id)][0].eid in list_pred_rev:                
                event = list_event_tok_id[tok.getAttribute(token_id)]
                tok_anchor = event[0].tokenAnchor
                if len(tok_anchor)>1:
                    ev_text = get_token_value(tok_anchor, list_token)
                    ev_text = ev_text.replace(" ","_")
                    ev_text = ev_text[:-1]
                    content[j].append("Y")
                    content[j].append(ev_text.lower()+".01")
                else:
                    content[j].append("Y")
                    content[j].append(tok.firstChild.nodeValue.lower()+".01")
                list_pred[j] = list_event_tok_id[tok.getAttribute(token_id)][0].eid
                list_pred_rev[list_event_tok_id[tok.getAttribute(token_id)][0].eid] = cpt_pred
                cpt_pred+=1

            else: 
                content[j].append("_")
                content[j].append("_")
            j+=1
            
            numSent = tok.getAttribute("sentence")

    content.insert(j,[""])
    j+=1
    for h in range(first_tok_sent,j-1):
        for e in range(14,len(list_pred_rev)+14):
            content[h].insert(e,'_')

        if len(content[h])>1 and content[h][0] in list_entity_tok_id:
            list_roles_tok = getHasPartRoles(list_has_part,content[h][0],list_entity_tok_id,list_entityId_head)
            for pred in list_roles_tok:
                if pred in list_pred_rev:
                    if list_roles_tok[pred] != "":
                        if lang == "es":
                            content[h][list_pred_rev[pred]+14] = list_roles_tok[pred].replace("Arg","arg")
                        else:
                            content[h][list_pred_rev[pred]+14] = list_roles_tok[pred].replace("Arg","A")

    return content



def convertSRL_conll05(list_token, list_has_part, list_event_tok_id, list_entity_tok_id, list_entityId_head):
    numSent = "0"
    content = []
    j = 0
    list_pred = {}
    list_pred_rev = {}
    cpt_pred = 0
    first_tok_sent = 0

    for tok in list_token:
        if tok.firstChild:
            if int(tok.getAttribute('sentence')) != int(numSent):
                content.insert(j,[""])
                j+=1
                for h in range(first_tok_sent,j-1):
                    for e in range(1,len(list_pred_rev)+1):
                        content[h].insert(e,'*')

                    if len(content[h])>1 and list_token[h-int(numSent)].getAttribute(token_id) in list_entity_tok_id:
                    #if len(content[h]) > 1:
                        list_roles_tok = getHasPartRoles_conll05(list_has_part,list_token[h-int(numSent)].getAttribute(token_id),list_entity_tok_id,list_entityId_head)
                        for pred in list_roles_tok:
                            if pred in list_pred_rev:
                                if list_roles_tok[pred] != "":
                                    content[h][list_pred_rev[pred]+1] = list_roles_tok[pred].replace("Arg","A")
                    if content[h][0] != "-" and len(content[h])>1 and list_token[h-int(numSent)].getAttribute(token_id) in list_event_tok_id:
                        content[h][list_pred_rev[list_event_tok_id[list_token[h-int(numSent)].getAttribute(token_id)][0].eid]+1] = "(V*)"

                list_pred = {}
                list_pred_rev = {}
                cpt_pred = 0
                first_tok_sent = j

            
            #content.insert(j,[tok.getAttribute('t_id')])#ID
            #content[j].append(tok.firstChild.nodeValue)#form
            content.insert(j,[])

            #lemma, plemma, pos, ppos, feat, pfeat, head, phead, deprel, pdeprel
            #for c in range(0,10):
            #    content[j].append("_")

            if isEventHasPart(list_has_part,tok.getAttribute(token_id),list_event_tok_id) and not list_event_tok_id[tok.getAttribute(token_id)][0].eid in list_pred_rev:
                
                event = list_event_tok_id[tok.getAttribute(token_id)]
                tok_anchor = event[0].tokenAnchor
                if len(tok_anchor)>1:
                    ev_text = get_token_value(tok_anchor, list_token)
                    ev_text = ev_text.replace(" ","_")
                    ev_text = ev_text[:-1]
                    #content[j].append("Y")
                    content[j].append(ev_text.lower())
                else:
                    #content[j].append("Y")
                    content[j].append(tok.firstChild.nodeValue.lower())
                list_pred[j] = list_event_tok_id[tok.getAttribute(token_id)][0].eid
                list_pred_rev[list_event_tok_id[tok.getAttribute(token_id)][0].eid] = cpt_pred
                cpt_pred+=1
                
            else: 
                #content[j].append("_")
                content[j].append("-")
            j+=1
            
            numSent = tok.getAttribute("sentence")

    content.insert(j,[""])
    j+=1
    for h in range(first_tok_sent,j-1):
        for e in range(1,len(list_pred_rev)+1):
            content[h].insert(e,'*')

        if len(content[h])>1 and list_token[h-int(numSent)].getAttribute(token_id) in list_entity_tok_id:
            #print "end: ",list_token[h].firstChild.childNode
            list_roles_tok = getHasPartRoles_conll05(list_has_part,list_token[h-int(numSent)].getAttribute(token_id),list_entity_tok_id,list_entityId_head)
            for pred in list_roles_tok:
                if pred in list_pred_rev:
                    if list_roles_tok[pred] != "":
                        content[h][list_pred_rev[pred]+1] = list_roles_tok[pred].replace("Arg","A")

    return content


def convertNER_multicol(list_token, list_entity_ment, list_entity_class, list_entity_tok_id):
    global nb_per
    global nb_loc
    global nb_org
    numSent = "0"
    content = []
    j = 0
    first_tok_sent = 0
    
    prev_ent = ""

    for tok in list_token:
        if tok.firstChild:
            if tok.getAttribute('sentence') != numSent:
                content.insert(j,[""])
                j+=1
            
            #content.insert(j,[tok.firstChild.nodeValue,tok.getAttribute(token_id)])
            content.insert(j,[tok.firstChild.nodeValue])

            if tok.getAttribute(token_id) in list_entity_tok_id:
                list_ent_id = list_entity_tok_id[tok.getAttribute(token_id)]
                for ent in list_ent_id:
                    if (ent.att["syntactic_type"] == "NAM" or ent.att["syntactic_type"] == "PRE.NAM" or all_synt_types==True) and ent.eid in list_entity_class:
#                     if (ent.att["syntactic_type"] == "NAM" or all_synt_types==True) and ent.eid in list_entity_class:
                        #if prev_ent != "" and prev_ent == ent.eid:
                        
                        if j > 0 and len(content[j]) < len(content[j-1]) and re.search("-"+list_entity_class[ent.eid],content[j-1][len(content[j])]):
                            pref = "I-"
                        else:
                            if j > 0 and len(content[j]) < len(content[j-1]) and content[j-1][len(content[j])] == "I-"+list_entity_class[ent.eid]:
                                pref = "B-"
                            else:
                                pref = "I-"
                        
                        prev_ent = ent.eid
                        content[j].append(pref+list_entity_class[ent.eid])

                        #count nb of entities of each type
                        if list_entity_class[ent.eid] == "PER" and pref == "B-":
                            nb_per+=1
                        elif list_entity_class[ent.eid] == "LOC" and pref == "B-":
                            nb_loc+=1
                        elif list_entity_class[ent.eid] == "ORG" and pref == "B-":
                            nb_org+=1
            else:
                prev_ent = ""
            
            numSent = tok.getAttribute("sentence")

            if not re.search("B-",content[j][len(content[j])-1]) and not re.search("I-",content[j][len(content[j])-1]):
                content[j].append("O")
            j += 1

    return content


def convertFact_multicol(list_token, list_event_ment):
    global nb_per
    global nb_loc
    global nb_org
    numSent = "0"
    content = []
    j = 0
    first_tok_sent = 0
    
    prev_ent = ""

    list_event_token_id = {}
    for ev in list_event_ment:
        for tokan in ev.tokenAnchor:
            if tokan in list_event_token_id:
                #don't keep CONJ
                if len(ev.tokenAnchor) < len(list_event_token_id[tokan].tokenAnchor):
                    list_event_token_id[tokan] = ev

            else:
                list_event_token_id[tokan] = ev

    for tok in list_token:
        if tok.firstChild:
            if tok.getAttribute('sentence') != numSent:
                content.insert(j,[""])
                j+=1
            
            content.insert(j,[tok.firstChild.nodeValue,"t"+tok.getAttribute(token_id)])
            #content.insert(j,[tok.firstChild.nodeValue])

            if tok.getAttribute(token_id) in list_event_token_id:
                ev = list_event_token_id[tok.getAttribute(token_id)]
                if j > 0 and len(content[j]) < len(content[j-1]) and re.search("-EVENT",content[j-1][len(content[j])]) and len(ev.tokenAnchor) > 1:
                    pref = "I-"
                else:
                    pref = "B-"
                        
                        
                prev_ent = ev.eid
                content[j].append(pref+"EVENT")

                content[j].append(ev.att["polarity"])
                content[j].append(ev.att["certainty"])
                content[j].append(ev.att["time"])
                
            else:
                prev_ent = ""
                content[j].append("O")
                content[j].append("O")
                content[j].append("O")
                content[j].append("O")
                
            numSent = tok.getAttribute("sentence")

            #if not re.search("B-",content[j][len(content[j])-1]) and not re.search("I-",content[j][len(content[j])-1]):
            #    content[j].append("O")
            j += 1

    return content


def transferHasPartLightVerb (list_has_participant, list_glink):
    glinkTargetSource = {}
    list_has_participant_new = []

    for glink in list_glink:
        source = glink.source
        target = glink.target
        glinkTargetSource[target[0]] = source[0] 

    for hasPart in list_has_participant:
        if hasPart.source[0] in glinkTargetSource:
            hasPart.source[0] = glinkTargetSource[hasPart.source[0]]
        list_has_participant_new.append(hasPart)

    return list_has_participant_new


def build_col_format_text(fileName, content):
    content_toprint = ""
    for k in range(0,len(content)):
        for c in range(0,len(content[k])):
            if c == len(content[k])-1:
                content_toprint += content[k][c]
            else:
                content_toprint += content[k][c]+"\t"
        content_toprint += "\n"
    
    content_toprint += "\n"
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    
    if len(sys.argv) > 3:
        extent = ".naf.conll"
        if get_arg(3) == "NER":
            extent = ".naf.conll"
        fileOut = extract_name(fileName)
        fileOut = fileOut.replace(".txt.xml",extent)
        fileOut = fileOut.replace(".xml",extent)
        f = codecs.open(get_arg(2)+fileOut,"w",encoding="utf-8")
        f.write(content_toprint)
        #sys.stdout = f
        
    #sys.stdout.write(content_toprint)


def get_list_elt_ment_by_id(list_elt_ment):
    list_elt_ment_by_id = {}
    for elt in list_elt_ment:
        list_elt_ment_by_id[elt.eid] = elt
    return list_elt_ment_by_id



def read_CAT_file(fileName): 
    global markable_id
    global relation_id
    global token_id
    global layer
    #print fileName
    
    #parse the file
    xmldoc = minidom.parse(fileName)

    #get elements 'Markables'
    markables = xmldoc.getElementsByTagName('Markables')[0] 
        
    #get elements 'Relations'
    relations = xmldoc.getElementsByTagName('Relations')[0]

    #get tokens
    list_token = xmldoc.getElementsByTagName('token')

    if list_token[0].hasAttribute("id") :
        markable_id = "id"
        token_id = "id"
        relation_id = "id"

    rel_refers_to = get_all_relation_value(relations,'REFERS_TO',{})
    list_has_participant = get_all_relation_value(relations, 'HAS_PARTICIPANT', ['sem_role'])
    list_glink = get_all_relation_value(relations, "GLINK",{})

    list_entity_mention = get_all_element_value(markables,'ENTITY_MENTION',['head','syntactic_type'])
    list_event_mention = get_all_element_value(markables,'EVENT_MENTION',['certainty','time','polarity','special_cases'])

    list_value_mention = get_all_element_value(markables, 'VALUE', ['head','syntactic_type'])
    for val in list_value_mention:
        list_entity_mention.append(val)


    list_entity_instance = get_instance(markables, 'ENTITY', 'ent_type')
    list_event_instance = get_instance(markables, 'EVENT', 'class')

    list_timex = get_all_element_value(markables, 'TIMEX3', ['type','functionInDocument','value'])
    #list_event_eventi = get_all_element_value(markables,'EVENT',['class'])

    list_tokId_value = get_list_tokenId_value(list_token)
    list_entityId_head = getEntityIdHead(list_entity_mention,list_tokId_value)

    content_to_write = []
    
    #Convert CAT files for SRL evaluation
    if layer == "SRL":
        #list_has_participant_new = transferHasPartLightVerb(list_has_participant, list_glink)
        content_to_write = convertSRL(list_token, list_has_participant, get_list_markable_tok_id_srl(list_event_mention), get_list_markable_tok_id_srl(list_entity_mention), list_entityId_head)

    #Convert CAT files for NERC evaluation
    elif layer == "NER":
        list_ent_mention_class = get_mention_class(list_entity_instance, rel_refers_to, "ent_type")
        
        list_entity_mention_class = []
        for val in list_entity_mention:
            if val.eid in list_ent_mention_class and (list_ent_mention_class[val.eid] == "ORG" or list_ent_mention_class[val.eid] == "LOC" or list_ent_mention_class[val.eid] == "PER"):
#            if val.eid in list_ent_mention_class and (list_ent_mention_class[val.eid] == "ORG" or list_ent_mention_class[val.eid] == "LOC" or list_ent_mention_class[val.eid] == "PER" or list_ent_mention_class[val.eid] == "FIN"):
                list_entity_mention_class.append(val)

        list_entity_tok_id = {}
        if type_annotation == "BIO-smallest":
            #list_entity_tok_id = get_list_markable_smallest_biggest_bis (list_entity_mention, list_ent_mention_class, "smallest")
            list_entity_tok_id = get_list_smallest_biggest_markable_tok_id(list_entity_mention_class, "smallest")
        elif type_annotation == "BIO-biggest":
            #list_entity_tok_id = get_list_markable_smallest_biggest_bis (list_entity_mention, list_ent_mention_class, "biggest")
            list_entity_tok_id = get_list_smallest_biggest_markable_tok_id(list_entity_mention_class, "biggest")
        elif type_annotation == "all":
            list_entity_tok_id = get_list_markable_tok_id(list_entity_mention, list_ent_mention_class)

        #if type_annotation == "all":
        #    content_to_write = convertNER_multicol(list_token, list_entity_mention, list_ent_mention_class, list_entity_tok_id)
        #else:
        content_to_write = convertNER_multicol(list_token, list_entity_mention, list_ent_mention_class, list_entity_tok_id)

    elif layer == "factuality":
        content_to_write = convertFact_multicol(list_token, list_event_mention)

    build_col_format_text(fileName, content_to_write)
    

input_and_evaluate()
#print "nb per: "+str(nb_per)
#print "nb org: "+str(nb_org)
#print "nb loc: "+str(nb_loc)
