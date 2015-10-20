#!/usr/bin/env python

# This script reads a CAT XML file and converts it to NAF XML
# This script also takes into account the named entities from the CROMER layer that 
# were already included in the CAT files by FBK.

# Date: 24 January 2015
# Author: Marieke van Erp  
# Contact: marieke.van.erp@vu.nl 

import sys
import re
import codecs

path = "/home/newsreader/components-eval/NWR-eval.v11/factuality-evaluation/"
sys.path.append(path)
from KafNafParserPy import *

#infile = open('555_Boeing_unveils_long-range_777.txt.xml',"r")
infile = codecs.open(sys.argv[1], 'r', encoding='utf-8')
raw = infile.read()
root = etree.XML(raw)

# maak een lijst van tokens:
token_list = root.findall(".//token")
num_sents = int(token_list[-1].get("sentence"))

# Init KafNafParserobject
my_parser = KafNafParser(None, type='NAF')
my_parser.root.set('{http://www.w3.org/XML/1998/namespace}lang','en')
my_parser.root.set('version','v3')
textlayer = Ctext()
termlayer = Cterms()
offset = 0
num = 0 

sents = [root.findall(".//token[@sentence='%s']" % str(n)) for n in range(0,num_sents + 1)]
for sent in sents:
	num = num + 1 
	for node in sent:
		wf = Cwf() 
		wf.set_id(node.get("t_id"))
		sentence_no = int(node.get("sentence")) + 1
		wf.set_sent(str(sentence_no))
		wf.set_para("1")
		wf.set_offset(str(offset))
		offset = offset + len(node.text)
		wf.set_length(str(len(node.text)))
		wf.set_text(node.text)
		my_parser.add_wf(wf)
		term = Cterm()
		term.set_id(node.get("t_id"))
		term.set_lemma(node.text)
		term_span = Cspan()
		term_target = Ctarget()
		term_target.set_id(node.get("t_id"))
		term_span.add_target(term_target)
		term.set_span(term_span)
		my_parser.add_term(term)
		
		#print "bla", node.text.encode('utf8')


# get a list of all entities
entities_list = root.findall(".//ENTITY") 
entities_ids = {}
entities_refs = {}

for entity in entities_list:
	entities_ids[entity.get("m_id")] = entity.get("ent_type")
	external_ref = str(entity.get("external_ref"))
	entities_refs[entity.get("m_id")] = external_ref
 #	print entity.get("m_id"), entity.get("ent_type"), external_ref
	
# Get the refers to relations to match the instances to the mentions 
refers_to_relations = root.findall(".//COREFERENCE")
relation_sources = {}
for relation in refers_to_relations:
	target = relation.findall(".//target")
	sources = relation.findall(".//source")
	for source in sources:
		relation_sources[source.get("m_id")] = target[0].get("m_id")
	#	print relation_sources[source.get("m_id")], target[0].get("m_id")

refers_to_relations = root.findall(".//REFERS_TO")
#relation_sources = {}
for relation in refers_to_relations:
	target = relation.findall(".//target")
	sources = relation.findall(".//source")
	for source in sources:
		relation_sources[source.get("m_id")] = target[0].get("m_id")
	#	print relation_sources[source.get("m_id")], target[0].get("m_id")


# get a list of all entity mentions :
entity_mentions_list = root.findall(".//ENTITY_MENTION")
entity_mention_ids = {} 
entity_mention_type = {}
for entity in entity_mentions_list:
	entity_mention_ids[entity.get("m_id")] = []
	entity_mention_type[entity.get("m_id")] = entity.get("syntactic_type")
	entity_mention_anchors = entity.findall(".//token_anchor")
	for tokens in entity_mention_anchors:
		entity_mention_ids[entity.get("m_id")].append(tokens.get("t_id"))
		
#print len(entity_mention_ids), len(entities_ids)

# get a list of all entity mentions and create NAF entities for each of them
for mention in entity_mention_ids:
	entity = Centity()
	entity.set_id(mention)
	if mention not in relation_sources:
		continue
	if entity_mention_type[mention] != "NAM" and entity_mention_type[mention] != "PRE.NAM":
                continue
	entity.set_type(entities_ids[relation_sources[mention]])
	externalreferenceslayer = CexternalReferences()
	new_ext_reference = CexternalReference()
	new_ext_reference.set_resource('byCROMER')
	#new_ext_reference.set_reference(entities_refs[relation_sources[mention]])
	new_ext_reference.set_reference(str(entities_refs[relation_sources[mention]]))
	new_ext_reference.set_confidence('1.0')
	entity.add_external_reference(new_ext_reference)
	my_parser.add_entity(entity)
	reference = Creferences()
	reference_span = Cspan()
	span_target = Ctarget()
#	span_target.set_id("bla")
	reference_span.add_target(span_target)
	span_targets = entity_mention_ids[mention]
	reference.add_span(span_targets)
	entity.add_reference(reference)
#	print mention, entity_mention_ids[mention], relation_sources[mention], entities_ids[relation_sources[mention]], entities_refs[relation_sources[mention]]

	


my_parser.dump()
