import os
import sys
import shutil

if __name__ == '__main__':
	dir = sys.argv[1]
	try:
		shutil.rmtree('source')
	except: pass
	try:
		shutil.rmtree('include')
	except: pass
	os.mkdir('source')
	os.mkdir('include')		
	
	for entry in os.walk(os.path.abspath(dir)):
		print '\nMoving files in %s' % entry[0]
		prefix = entry[0].replace(os.getcwd(), '').strip('\\Animation')

		for file in entry[2]:
			to = str()
			if file.find('.cpp') >= 0:
				to = os.path.join(os.getcwd(), 'source', prefix )
				print "%s [cpp] -> %s" % ((file, to))
			elif file.find('.h') >= 0:
				to = os.path.join(os.getcwd(), 'include', prefix )
				print "%s [h] -> %s" % ((file, to))
			try:
				os.mkdir(to)
			except: pass
			shutil.copy(os.path.join(entry[0], file), os.path.join(to, file))