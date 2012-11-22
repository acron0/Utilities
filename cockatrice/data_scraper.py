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
		
def get_cards(sets_name_list):
	cards_url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?output=spoiler&method=text&set=["%s"]&special=true'
	img_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=%d&type=card'
	
	def add_field(card_dict, key, tds_list, index):
		index += 1
		card_dict[key] = tds_list[index].text.encode("UTF-8")
		index += 1
		return index
	
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
			count = 0
			tds = cards[0].find('table').findAll('td')
			runs = len(tds)/noof_tds_per_entry
			for index in range(runs):
				
				card = dict()
				count = add_field(card, "name",  		tds, count)
				
				# get img
				url = tds[count-1].findChild('a')["href"]
				id = url[url.index('=') + 1:]
				card["img_url"] = img_url % int(id)
				
				count = add_field(card, "cost",  		tds, count)
				count = add_field(card, "type",  		tds, count)
				count = add_field(card, "pt",  			tds, count)
				count = add_field(card, "text",  		tds, count)
				count = add_field(card, "set/rarity",  	tds, count)	
				count += 1 # colspan
				self.cards.append( card )
	
	threads = list()
	for set in sets_name_list:
		threads.append(CardSetEntry(set))
	
	for t in threads:
		t.start()
		
	while len([t for t in threads if t.is_alive()]) != 0:
		pass
		
	for t in threads:
		print "'%s' returned %d cards..." % (t,len(t.cards))
		
	return [(t.name, t.cards) for t in threads]

if __name__ == "__main__":
	sets = get_sets()
	cards = get_cards([s["name"] for s in sets])