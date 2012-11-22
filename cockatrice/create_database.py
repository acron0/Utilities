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
	
	valid_colors = ['B', 'U', 'W', 'R', 'G']
	valid_rarity = ['Mythic Rare', 'Rare', 'Uncommon', 'Common', 'Special', 'Promo']
	
	result["name"] 		= card_dict["name"]
	result["type"] 		= card_dict["type"]
	result["pt"] 		= card_dict["pt"]
	result["text"] 		= card_dict["text"]
	result["cost"] 		= card_dict["cost"]
	result["set"]   	= set_name
	result["img"]		= card_dict["img_url"]
	
	# rarities may differ by set but we don't *really* care so pick the first one we encounter
	rarest_idx = len(card_dict["set/rarity"])
	new_rarity = ""
	for rarity in valid_rarity:
		idx = card_dict["set/rarity"].find(rarity)
		if idx != -1 and idx < rarest_idx:
			rarest_idx = idx
			new_rarity = rarity
	
	# deduce colors
	result["color"] = [x for x in list(set(list(card_dict["cost"]))) if x in valid_colors]
	
	return result
	
# -------------------------------------------------------------------
def create_database_from_scrape():

	#
	conn = connect()
	db = open_db(conn, 'oracle')
	clean(db)
	
	#
	print "Generating a new database via scraper...(this may take a while)"
	
	sets = get_sets()
	cards = get_cards([s["name"] for s in sets])	
	
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
		create_database_from_scrape()