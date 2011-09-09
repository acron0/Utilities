import urllib
import re
import BeautifulSoup
import random

download_to = "Scrape"					# folder
url = 'http://deadendthrills.com/404/'	# url to generate the 404

r = random.Random()

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
		gamesList = gamesList + [(current[0].contents[0].string, current[0].contents[0].attrs[0][1])]

while 1:
	# pick one at random
	selectedGame = gamesList[r.randrange(len(gamesList))]
	print 'Selected Game:', selectedGame[0], '(', selectedGame[1], ')'

	result = urllib.urlopen(selectedGame[1])
	response = result.read()
	soup = BeautifulSoup.BeautifulSoup(response)

	# filter the html
	imgEntries = soup.findAll(lambda tag: tag.name == 'a' and tag.string and (tag.string.upper() == 'DOWNLOAD WALLPAPER (1080P)' or tag.string.upper() == 'DOWNLOAD FOR PRINT MEDIA'))
	
	# retry if we can't find an image
	if len(imgEntries) > 0:
		break
	else:
		print 'Error: No images found! Selecting a new game...'
	

# randomly select an image
imageUrl = imgEntries[r.randrange(len(imgEntries))]['href']
print imageUrl
