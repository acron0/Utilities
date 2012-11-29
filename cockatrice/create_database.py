"""
Take a Cockatrice DB (cards.xml) and poke it into an SQL database.
"""

import sys, os
import xml.etree.ElementTree as ET
from card_number import CardNumber
from db_controller import *
from data_scraper import *

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
		
def format_card_dict(card_dict, set_name):

	result = dict()	
	
	valid_colors = [('Black', 'B'), ('Blue', 'U'), ('White', 'W'), ('Red', 'R'), ('Green','G')]
	valid_rarity = ['Mythic Rare', 'Rare', 'Uncommon', 'Common', 'Special', 'Promo']
	
	# edge cases
	if not card_dict.has_key("pt"):
		card_dict["pt"] = ''
	
	result["name"] 		= card_dict["name"]
	result["type"] 		= card_dict["type"]
	result["pt"] 		= card_dict["pt"]
	result["text"] 		= card_dict["text"]
	result["cost"] 		= card_dict["cost"]
	result["set"]   	= set_name
	result["img"]		= card_dict["img_url"]
	
	# rarities may differ by set but we don't *really* care so pick the first one we encounter
	rarest_idx = len(card_dict["set/rarity"])
	new_rarity = card_dict["set/rarity"]
	for rarity in valid_rarity:
		idx = card_dict["set/rarity"].find(rarity)
		if idx != -1 and idx < rarest_idx:
			rarest_idx = idx
			new_rarity = rarity
	result["rarity"] = new_rarity
	
	# deduce colors
	if not card_dict.has_key('color'):
		result["color"] = [x for x in list(set(list(card_dict["cost"]))) if x in [c[1] for c in valid_colors]]
	else:
		result["color"] = []
		card_cols = card_dict["color"].split('/')
		for c in valid_colors:
			if c[0] in card_cols:
				result["color"].append(c[1])
	return result
	
# -------------------------------------------------------------------
def create_database_from_scrape(single_threaded):

	#
	conn = connect()
	db = open_db(conn, 'oracle')
	clean(db)
	
	#
	print "Generating a new database via scraper...(this may take a while)"
	
	sets = get_sets()
	cards = get_cards([s["name"] for s in sets], single_threaded)	
	
	# --------------------
	for child in sets:
		insert_set(db, child["name"], child["img"])	
		
	# --------------------
	cn = CardNumber()
	for card_set in cards:
		for card in card_set[1]:
			name = card["name"]
			crd = format_card_dict(card, card_set[0])
			insert_card(db, str(cn), crd)
			cn.increment()	
	
	close(conn)	
	
# -------------------------------------------------------------------
if __name__ == "__main__":
	single_thread = False
	if "-s" in sys.argv:
		single_thread = True
		print "(Running in single-threaded mode...)"
	create_database_from_scrape(single_thread)