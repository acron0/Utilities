import urllib
import re
import BeautifulSoup
import random

url = 'http://deadendthrills.com/404/'	# url to generate the 404
r = random.Random()
exclude = ['Print Art']

# class for game entries
class gameEntry:
	def __init__(self, name, page):
		self.name = name
		self.page = page
		
	def __str__(self):
		return self.name

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
	if(len(current) > 0):
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
				imgEntries =  imgEntries + [ metaDiv.findAll('a', {'title':None})[0]['href'] ]
		
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
	
"""
# randomly select an image
imageUrl = imgEntries[r.randrange(len(imgEntries))]['href']
print imageUrl"""
