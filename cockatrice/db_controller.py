from pymongo import Connection

def connect():
	connection = Connection()
	return connection
	
def open_db(connection, name):
	db = connection[name]
	return db
	
def insert_set(db, name, img):	
	set = {"img":img, "name":name}
	db.sets.insert(set)
	
def insert_card(db, index, card_data):
	card = {"card_index":index}
	card.update(card_data)
	db.cards.insert(card)
	
def clean(db):
	if db == None:
		raise Exception("DB is null.")
		
	db.drop_collection('sets')
	db.drop_collection('cards')
	db.create_collection('sets')
	db.create_collection('cards')

def do_tests():
	print 'Running tests...'
	db = connect()
	clean(db)

def close(connection):
	connection.close()

if __name__ == "__main__":
	do_tests()