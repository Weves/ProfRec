import sys
import subprocess
#from capes.spiders.cape import CapeSpider

# create a file containing all requested class names
f = open('cnames.txt', 'w')
if (len(sys.argv) > 1 and sys.argv[1] != 'cape'):
	i = 1
	while (i < len(sys.argv)):
		f.write(sys.argv[i])
		f.write('\n')
		i+=1
else:
	print ("ERROR: no classes specified")
f.close()

# use scrapy to find get the data we want about the professors
subprocess.call(["scrapy", "crawl", "cape"])



