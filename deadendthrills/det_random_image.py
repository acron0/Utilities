"""deadendthrills_rand_image.py

Generates a database of screenshots from the website www.deadendthrills.com
and randomly returns one.

Usage:
	--generate (-g) 		- Generates the database.
	--random (-r)			- Returns a random image URL from the current database.
	--help (-h)				- Shows this message
	--verbose (-v)			- Enables verbose output
"""
import sys
import getopt
import urllib
import re
import BeautifulSoup
import sqlite3
import os
import threading
import time
import math

db_name = 'deadendthrills.db'

def print_usage(code):
	print __doc__
	sys.exit(code)	
	
def get_random_image_url():
	conn = sqlite3.connect(db_name)
	result = conn.execute("SELECT * FROM images ORDER BY RANDOM() LIMIT 1").fetchall()
	return result

def generate_database(verbose):

	url = 'http://deadendthrills.com/404/'	# url to generate the 404
	exclude = ['Print Art', 'Blog', 'Community', 'ModList']
	extensions = ['.jpg', '.png', '.gif']	
	img_entries = []
		
	# set up addToDatabase function
	def add_to_images(conn, game_name, game_cat, img_url):
		#print '\tAdding %s' % img_url
		conn.execute( "INSERT INTO images VALUES ('{0}', '{1}', '{2}')".format(game_name, game_cat, img_url))
		
	# set up addToDatabase function
	def valid_image(img_url):
		return img_url[-4:] in extensions
		
	# verbose filtered printing
	def _print(message):
		if verbose:
			print(message)
	
	# progress bar - http://snipplr.com/view/25735/
	def progress(width, percent):
		marks = math.floor(width * (percent / 100.0))
		spaces = math.floor(width - marks)
	 
		loader = '[' + ('=' * int(marks)) + (' ' * int(spaces)) + ']'
	 
		sys.stdout.write("%s %d%%\r" % (loader, percent))
		if percent >= 100:
			sys.stdout.write("\n")
		sys.stdout.flush()
				
	# -------------------------------------------------------------------------------------------

	# class for game entries
	class GameEntry  ( threading.Thread ):
		def __init__(self, name, cat_id, page):
			super(GameEntry, self).__init__()
			self.name = name
			self.page = page
			self.cat_id = cat_id
			_print("Found %s  (%s)" % (self.name, self.cat_id))
			
		def __str__(self):
			return self.name
			
		def run ( self ):
		
			page_count = 1
			page_url = self.page		

			while True:
				try:
					result = urllib.urlopen(page_url)
				except IOError as e:
					print "I/O error({0}): {1}".format(e.errno, e.strerror)
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
						except (IndexError, KeyError):
							continue
						
						if img_url != None:
							img_count+=1
							#add_to_images(conn, game.name, game.cat_id, img_url)
							img_entries.append((self.name, self.cat_id, img_url))

				#print "\tFound %s images on page %s" % (img_count, page_count)
			
				# do we have another page?
				try:
					back_div = soup.find("div", { "class" : "alignright" }).contents[0]
				except (IndexError, AttributeError):
					break

				try:
					if back_div:
						page_url = back_div['href']
						page_count += 1
					else:		
						break
				except (IndexError, KeyError):
					break

			#print "\tTotal: %s images" % len(img_entries)
		
	#-------------------------------------------------------------------	
	
	print 'Generating database from %s - please wait, this may take a while...' % url	
			
	# burn existing temp db
	_print("Cleaning up any old temporary files...")
	temp_db_name = 'temp_' + db_name
	try:
	   _print("Creating temporary database...")
	   open(temp_db_name, 'r')
	   os.remove(temp_db_name)
	except IOError:
	   pass

	# create table
	conn = sqlite3.connect(temp_db_name)	
	conn.execute("CREATE TABLE images (game_name text, game_cat text, img_url text)")
	
	# get html
	_print("Fetching games list...")
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
		except (IndexError, AttributeError):
			pass

	# start the threads for each game entry
	for game in games:
		_print( 'Collecting data for %s (%s) ...' % (game.name, game.cat_id) )
		game.start()

	# wait for none to be alive.
	lastAlive = len(games)
	progress(50, 0)
	while True:
		noof_alive_threads = len([game for game in games if game.is_alive()])
		if noof_alive_threads == 0:
			break
		if lastAlive != noof_alive_threads:
			lastAlive = noof_alive_threads
			progress(50, 100.0 - (100.0 * float(noof_alive_threads)/float(len(games))))
		
	progress(50, 100)
	print 'Writing %d images to the database...' % len(img_entries)
	
	for i in range(0, len(img_entries)):
		entry = img_entries[i]
		_print("Adding image (%s, %s): %s " % entry)
		add_to_images(conn, entry[0], entry[1], entry[2])
		progress(50, 100.0 * float(i)/float(len(img_entries)))
		
	progress(50, 100)
	
	# close current db
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
		
	verbose = False
	if sys.argv.__contains__("-v") or sys.argv.__contains__("--verbose"):
		verbose = True
	
	
	# process options
	for o in sys.argv:
		if o in ("--help") or o in ("-h"):
			print_usage(0)
		if o in ("--generate") or o in ("-g"):
			generate_database(verbose)
			sys.exit(0)
		if o in ("--random") or o in ("-r"):
			print get_random_image_url()
			sys.exit(0)
	
	print 'Undefined usage: %s\n' % sys.argv[1:]
	print_usage(0)

if __name__ == "__main__":
	main()