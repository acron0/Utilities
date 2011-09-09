import urllib
import re
import BeautifulSoup
import sqlite3
import os

url = 'http://deadendthrills.com/404/'	# url to generate the 404
db_name = 'deadendthrills.db'
exclude = ['Print Art']

# class for game entries
class gameEntry:
	def __init__(self, name, page):
		self.name = name
		self.page = page
		
	def __str__(self):
		return self.name
		
# burn existing db
try:
   open(db_name, 'r')
   os.remove(db_name)
except IOError as e:
   pass

# create table
conn = sqlite3.connect(db_name)
cur = conn.cursor()
cur.execute( "CREATE TABLE images (game_name text, img_url text)" )

# set up addToDatabase function
def addToDatabase(game_name, img_url):
	cur.execute( "INSERT INTO images VALUES ('%s', '%s' )" % (game_name, img_url) )

# get html
result = urllib.urlopen(url)
response = result.read()
soup = BeautifulSoup.BeautifulSoup(response)

# filter the html
gameEntries = soup.findAll('li')

# populate games list
gamesList = []
for k in range(len(gameEntries)):
	current = [gameEntries[k] for a, b in gameEntries[k].attrs if b.find('cat-item') >= 0]
	if(len(current) > 0 and current[0].contents[0].string not in exclude):
		gamesList = gamesList + [ gameEntry(current[0].contents[0].string, current[0].contents[0].attrs[0][1]) ]

# iterate the games, one by one.
for game in gamesList:

	print ''.join(('Collecting data for ', game.name, '...'))

	pageUrl = game.page
	count = 1
	imgEntries = []
	while 1:
		result = urllib.urlopen(pageUrl)
		response = result.read()
		soup = BeautifulSoup.BeautifulSoup(response)

		# filter the html		
		metaDivEntries = soup.findAll("div", { "class" : "meta" })
		for metaDiv in metaDivEntries:
			links = metaDiv.findAll('a', {'title':None})
			if(links):
				img_url = metaDiv.findAll('a', {'title':None})[0]['href']
				addToDatabase(game.name, img_url)
				imgEntries += [ img_url ]
		
		print ''.join(('\tFound ', str(len(imgEntries)), ' images on page ', str(count)))
	
		# retry if we can't find an image
		if len(imgEntries) > 0:
			pass
	
		# do we have another page?
		navBackDiv = soup.find("div", { "class" : "navback" }).contents[0]
		if(len(navBackDiv.contents) > 0 and navBackDiv.contents[0].name == 'a'):
			pageUrl = navBackDiv.contents[0]['href']
			count += 1
		else:		
			break
	
	print ''.join(('\tTotal: ', str(len(imgEntries)), ' images.'))

conn.commit()
conn.close()