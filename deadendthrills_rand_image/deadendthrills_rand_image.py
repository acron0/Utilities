import urllib
import re
import BeautifulSoup
import sqlite3
import os

url = 'http://deadendthrills.com/404/'	# url to generate the 404
db_name = 'deadendthrills.db'
exclude = ['Print Art']

# class for game entries
class GameEntry:
	def __init__(self, name, page):
		self.name = name
		self.page = page
		
	def __str__(self):
		return self.name
		
# burn existing db
try:
   open(db_name, 'r')
   os.remove(db_name)
except IOError:
   pass

# create table
conn = sqlite3.connect(db_name)
cur = conn.cursor()
cur.execute("CREATE TABLE images (game_name text, img_url text)")

# set up addToDatabase function
def add_to_images(cur, game_name, img_url):
	cur.execute( "INSERT INTO images VALUES (?, ?)" % (game_name, img_url))

# get html
result = urllib.urlopen(url)
response = result.read()
soup = BeautifulSoup.BeautifulSoup(response)

# filter the html
game_entries = soup.findAll('li')

# populate games list
games = []
for k in range(len(game_entries)):
	current = [game_entries[k] for a, b in game_entries[k].attrs if b.find('cat-item') >= 0]
	try:
		if current and current[0].contents[0].string not in exclude:
			games.append([game_entry(current[0].contents[0].string, current[0].contents[0].attrs[0][1])])
	except IndexError, AttributeError:
		pass

# iterate the games, one by one.
for game in games:
	print 'Collecting data for %s ...' % game.name

	page_url = game.page
	count = 1
	img_entries = []

	while True:
		result = urllib.urlopen(page_url)
		response = result.read()
		soup = BeautifulSoup.BeautifulSoup(response)

		# filter the html		
		divs = soup.findAll("div", { "class" : "meta" })
		for div in divs:
			links = div.findAll('a', { 'title': None })
			if links:
				try:
					img_url = div.findAll('a', { 'title': None })[0]['href']
				except IndexError, KeyError:
					continue
				
				add_to_images(cur, game.name, img_url)
				img_entries.append(img_url)

		# retry if we can't find an image
		if len(img_entries) > 0:
			continue

		print "\tFound %s images on page %s" % (len(img_entries), count)
	
		# do we have another page?
		try:
			back_div = soup.find("div", { "class" : "navback" }).contents[0]
		except IndexError, AttributeError:
			continue

		try:
			if back_div and back_div.contents[0].name == 'a':
				page_url = back_div.contents[0]['href']
				count += 1
			else:		
				break
		except IndexError, KeyError:
			continue

	print "\tTotal: %s images" % len(img_entries)

conn.commit()
conn.close()