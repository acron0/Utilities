"""
Take a Cockatrice DB (cards.xml) and poke it into an SQL database.
"""

import sys, os
import xml.etree.ElementTree as ET
from card_number import CardNumber
from db_controller import *

caps_dict = dict()

def remove_accents(text):
	replacements = dict()
	replacements['a'] = [ u'\xe2' ]
	
	def __replace(c):	
		for k in replacements:
			if replacements[k].__contains__(c):
				c = k
		return c
	
	text = map(__replace, text)
	print text
	return ''.join(text)
	
def element_to_array(element):

	result = dict()	
	
	# early out if no attributes and no children.
	if len(element.attrib) == 0 and len(element.getchildren()) == 0:
		if element.text != None and len(element.text.strip()) != 0:
			result.update({element.tag:element.text.strip()})
		else:
			result.update({element.tag:""})
		return result

	# create dict for this tag
	result.update({element.tag:dict()})
	
	# if value, create value tag
	if element.text != None and len(element.text.strip()) != 0:
		result[element.tag].update({'value':element.text.strip()})
		
	# add attributes
	for v in element.attrib:
		result[element.tag].update ({v:element.attrib[v]})

	# add children
	for child in element.getchildren():
		to_add = element_to_array(child)
		if result.has_key(element.tag) and result[element.tag].has_key(to_add.keys()[0]):
			# add as list
			dupe_list = []
			if isinstance(result[element.tag][to_add.keys()[0]],list):
				dupe_list = result[element.tag][to_add.keys()[0]]
			else:
				dupe_list.append(result[element.tag][to_add.keys()[0]])
			dupe_list.append(to_add.values()[0])
			result[element.tag][to_add.keys()[0]] = dupe_list
		else:
			result[element.tag].update(to_add)
	
	return result

def create_database(xml_file):

	#
	conn = connect()
	db = open_db(conn, 'oracle')
	clean(db)
	
	#
	tree = ET.parse(xml_file)
	root = tree.getroot()
	if root.tag != "cockatrice_carddatabase":
		print "Not a valid Cockatrice database file: %s" % root.tag
		return
	
	print "Converting Cockatrice Database - Version %s" % root.attrib["version"]

	sets  = root.find("sets")
	cards = root.find("cards")
	
	# --------------------
	for child in sets:
		insert_set(db, child.find("name").text, child.find("longname").text)		
		
	print "Found %d set(s)..." % len(sets)
	
	# --------------------
	cn = CardNumber()
	for child in cards:
		name = child.find("name").text
		crd = element_to_array(child)
		insert_card(db, str(cn), crd.values()[0])
		cn.increment()
		
	print "Found %d cards(s)..." % len(cards)	
	
	close(conn)	

if __name__ == "__main__":
	create_database(sys.argv[1])