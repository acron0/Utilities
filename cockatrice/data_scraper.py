import requests
import threading
import re
from BeautifulSoup import BeautifulSoup

def get_sets():
	sets_url = 'http://magic.tcgplayer.com/all_magic_sets.asp'
	r = requests.get(sets_url)
	b = BeautifulSoup(r.text.encode("UTF-8"))
	s = list()
	tables = b.findAll('table')
	magic_index_number = 15 #table index on site	
	p = re.compile('.*(\(.+\)).*') # regex for removing brackets e.g. (M13)
	
	replacements = { # specific names to replace
	
		"Alpha Edition" : "Limited Edition Alpha",
		"Beta Edition" : "Limited Edition Beta"
	}
		
	end = False
	complete_pair = dict()
	for td in tables[magic_index_number].tr.findAll('td'):
		for child in td.fetch():
			if child.name == "img":
			
				complete_pair["img"] = child["src"]
				
			elif child.name == "a":
			
				name = child.text.encode("UTF-8")
				
				# brackets				
				m = p.match(name)
				if m != None:
					g = m.groups()
					for n in g:
						name = name.replace(n,'')
					
				# replacements
				elif replacements.has_key(name):
					name = replacements[name]
				
				complete_pair["name"] = name.strip()
				
			elif child.name == "strong" and child.text == "Special sets":
			
				end = True
				break
				
			if len(complete_pair) == 2:
				s.append(complete_pair)
				complete_pair = dict()	
		if end:
			break
			
	s.reverse() # reverse so oldest first (number system should be preserved)
	return s
		
def get_cards(sets_name_list, single_threaded):
	cards_url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?output=spoiler&method=text&set=["%s"]&special=true'
	img_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=%d&type=card'
	
	def add_field(card_dict, key, tds_list, index):
		index += 1
		card_dict[key] = tds_list[index].text.encode("UTF-8")
		index += 1
		return index
		
	# --------------------------------------------------
	class CardSetEntry  ( threading.Thread ):
		def __init__(self, name):
			super(CardSetEntry, self).__init__()
			self.name = name
			self.url = cards_url % name 
			self.cards = list()
			
		def __str__(self):
			return self.name
			
		def run ( self ):		
			r = requests.get(self.url)
			b = BeautifulSoup(r.text.encode("UTF-8"))
			cards = b.findAll('div', { 'class': 'textspoiler' })
			
			noof_tds_per_entry = 13
			tds = cards[0].find('table').findAll('td')
			runs = len(tds)/noof_tds_per_entry
			
			cards_collection = []
			current_card = {}
			
			for td_idx in range(len(tds)):
				td = tds[td_idx]
				
				if td.has_key('colspan'):
					continue
				
				if not td.text.encode("UTF-8").endswith(':'):
					continue
					
				if len(current_card) != 0 and td.text.encode("UTF-8") == "Name:":
					self.cards.append( current_card )
					current_card = {}
				
				if   td.text.encode("UTF-8") == "Name:":
					current_card["name"] = tds[td_idx + 1].text.encode("UTF-8")
					url = tds[td_idx + 1].findChild('a')["href"]
					id = url[url.index('=') + 1:]
					current_card["img_url"] = img_url % int(id)					
					
				elif td.text.encode("UTF-8") == "Cost:":
					current_card["cost"] = tds[td_idx + 1].text.encode("UTF-8")
				elif td.text.encode("UTF-8") == "Type:":
					current_card["type"] = tds[td_idx + 1].text.encode("UTF-8")
				elif td.text.encode("UTF-8") == "Pow/Tgh:":
					current_card["pt"] = tds[td_idx + 1].text.encode("UTF-8")
				elif td.text.encode("UTF-8") == "Rules Text:":
					current_card["text"] = tds[td_idx + 1].text.encode("UTF-8")
				elif td.text.encode("UTF-8") == "Set/Rarity:":
					current_card["set/rarity"] = tds[td_idx + 1].text.encode("UTF-8")
				elif td.text.encode("UTF-8") == "Color:":
					current_card["color"] = tds[td_idx + 1].text.encode("UTF-8")
					
			# don't forget the last one :)		
			self.cards.append( current_card )	
# --------------------------------------------------			
			
	threads = list()
	for set in sets_name_list:
		threads.append(CardSetEntry(set))
	
	for t in threads:
		t.start()
		if single_threaded:
			print "Started thread for '%s'..." % str(t)
			while t.is_alive():
				pass
			
	if not single_threaded:	
		while len([t for t in threads if t.is_alive()]) != 0:
			pass
		
	for t in threads:
		print "'%s' returned %d cards..." % (t,len(t.cards))
		
	return [(t.name, t.cards) for t in threads]

if __name__ == "__main__":
	sets = get_sets()
	cards = get_cards([s["name"] for s in sets])