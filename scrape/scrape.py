import urllib
import re

core_ext=".cfm"
save_dir = "C:\\Users\\acron\\Desktop\\fvgh\\"
base_url = 'http://www.forestviewguesthouse.co.uk/'

tests = [
     (re.compile('.*href\s*=\s*\"([^\"]*\.cfm)'), 0),
     (re.compile('.*href\s*=\s*\"([^\"]*\.css)'), 0),

     (re.compile('.*src\s*=\s*\"([^\"]*\.png)'), 0),
     (re.compile('.*src\s*=\s*\"([^\"]*\.jpg)'), 0),
     (re.compile('.*src\s*=\s*\"([^\"]*\.gif)'), 0),

     (re.compile('.*url\(([^\"]*\.png)'), 0),    
     (re.compile('.*url\(([^\"]*\.jpg)'), 0),
     (re.compile('.*url\(([^\"]*\.gif)'), 0),
]

# -----------------------------------------------
urls = [base_url + 'index' + core_ext]
excluded = []

for url in urls:

     try:
          excluded.index(url)
          continue
     except Exception:
          pass

     print 'Opening %s...' % url
     excluded.append(url)

     if url.find(core_ext) >= 0 or url.find('.css') >= 0:
		
          result = urllib.urlopen(url)
          response = result.read()

          inf = open(save_dir + url.replace(base_url, ''), 'w')
          inf.write(response)
          inf.close()

          response = response.replace('\t', '')
          response_lines = response.split('\n')

          for line in response_lines:
               for reg in tests:
                    results = reg[0].match(line)
                    if results:
						print 'Matched: ' + str(results.group(1))
						urls.append(base_url + results.group(1))
     else:
		try:
			urllib.urlretrieve(url, save_dir + url.replace(base_url, ''))
		except IOError:
			pass
		
