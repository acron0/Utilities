"""deadendthrills_rand_image.py

Generates a database of screenshots from the website www.deadendthrills.com
and randomly returns one.

Usage:
	--generate 	- Generates the database.
	--random	- Returns a random image URL from the current database.
	--help		- Shows this message
"""
import sys
import getopt
import urllib
import re
import BeautifulSoup
import sqlite3
import os
import htmlentitydefs

db_name = 'deadendthrills.db'

def print_usage(code):
	print __doc__
	sys.exit(code)	
	
def get_random_image_url():
	conn = sqlite3.connect(db_name)
	result = conn.execute("SELECT * FROM images ORDER BY RANDOM() LIMIT 1").fetchall()
	return result

def generate_database():

	url = 'http://deadendthrills.com/404/'	# url to generate the 404
	exclude = ['Print Art', 'Blog', 'Community', 'ModList']
	extensions = ['.jpg', '.png', '.gif']	
		
	# set up addToDatabase function
	def add_to_images(conn, game_name, game_cat, img_url):
		print '\tAdding %s' % img_url
		conn.execute( "INSERT INTO images VALUES ('{0}', '{1}', '{2}')".format(game_name, game_cat, img_url))
		
	# set up addToDatabase function
	def valid_image(img_url):
		return img_url[-4:] in extensions
				
	# -------------------------------------------------------------------------------------------	
	
	print 'Generating database from %s - please wait, this may take a while...' % url

	# class for game entries
	class GameEntry:
		def __init__(self, name, cat_id, page):
			self.name = name
			self.page = page
			self.cat_id = cat_id
			
		def __str__(self):
			return self.name
			
	# burn existing temp db
	temp_db_name = 'temp_' + db_name
	try:
	   open(temp_db_name, 'r')
	   os.remove(temp_db_name)
	except IOError:
	   pass

	# create table
	conn = sqlite3.connect(temp_db_name)	
	conn.execute("CREATE TABLE images (game_name text, game_cat text, img_url text)")
	
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
			cat_id = current[0].attrs[0][1].replace('cat-item', '').replace('-', '').strip()
			if current and current[0].contents[0].string not in exclude:
				games.append(GameEntry(current[0].contents[0].string, cat_id, current[0].contents[0].attrs[0][1]))
		except IndexError, AttributeError:
			pass

	# iterate the games, one by one.
	for game in games:

		print 'Collecting data for %s (%s) ...' % (game.name, game.cat_id)

		page_url = game.page
		page_count = 1
		img_entries = []

		while True:
			try:
				result = urllib.urlopen(page_url)
			except IOError, e:
				print 'FAILED: ' + e
				continue
			response = result.read()
			soup = BeautifulSoup.BeautifulSoup(response)

			# filter the html		
			img_count = 0
			
			# start with large images
			divs = soup.findAll("div", { "class" : "tagmeta" })
			for div in divs:
				links = div.findAll('a', { 'title': None })
				if links:
					try:
					
						for i in range(len(links)):
							img_url = links[len(links)-(1+i)]['href']
							if(valid_image(img_url)):
								break
							else:
								img_url = None
					except IndexError, KeyError:
						continue
					
					if img_url != None:
						img_count+=1
						add_to_images(conn, game.name, game.cat_id, img_url)
						img_entries.append(img_url)
					
			# now, try gallery images
			"""divs = soup.findAll("div", { "class" : "ngg-gallery-thumbnail"})
			for div in divs:
				try:
					img_url = div.findAll('a')[0]['href']
					
					if valid_image(img_url):
						img_count+=1
						add_to_images(conn, game.name, img_url)
						img_entries.append(img_url)
				except IndexError, KeyError:
					continue"""

			print "\tFound %s images on page %s" % (img_count, page_count)
		
			# do we have another page?
			try:
				back_div = soup.find("div", { "class" : "alignright" }).contents[0]
			except IndexError, AttributeError:
				break

			try:
				if back_div:
					page_url = back_div['href']
					page_count += 1
				else:		
					break
			except IndexError, KeyError:
				break

		print "\tTotal: %s images" % len(img_entries)

	conn.commit()
	conn.close()
	
	# switch dbs
	try:
	   open(db_name, 'r')
	   os.remove(db_name)
	except IOError:
	   pass
	   
	os.rename(temp_db_name, db_name)
	
def main():

	if len(sys.argv) <= 1:
		print_usage(2)
	
	# process options
	for o in sys.argv:
		if o in ("--help"):
			print_usage(0)
		if o in ("--generate"):
			generate_database()
			sys.exit(0)
		if o in ("--random"):
			print get_random_image_url()
			sys.exit(0)
	
	print 'Undefined usage: %s\n' % sys.argv[1:]
	print_usage(0)

if __name__ == "__main__":
	main()