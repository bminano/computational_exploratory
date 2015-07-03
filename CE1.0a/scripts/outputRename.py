import sys, getopt
import os
import re

def processDir(directory):
	counter = 0
	for f in sorted(os.listdir(directory)):
		if os.path.isdir(os.path.join(directory,f)):
			if (len(re.findall(r'visit_dump_[0-9]+', f)) > 0):
				os.rename(os.path.join(directory,f), os.path.join(directory,'visit_dump_' + str(counter)))
			    	counter = counter + 1
			else:
				if (len(re.findall(r'visit_dump.[0-9]+', f)) > 0):
					os.rename(os.path.join(directory,f), os.path.join(directory,'visit_dump.' + str(counter)))
				    	counter = counter + 1
				else:
					processDir(os.path.join(directory,f))



def main(argv):
	#Script usage
    	try:
        	opts, args = getopt.getopt(argv,"hd:",["help", "directory="])
    	except getopt.GetoptError:
        	print 'USAGE: python outputRename.py -d <directory>'
        	sys.exit(2)
    	for opt, arg in opts:
        	if opt == '-h':
            		print 'USAGE: python outputRename.py -d <directory>'
            		sys.exit()
        	elif opt in ("-d", "--directory"):
            		directory = arg

	processDir(directory)


if __name__ == "__main__":
	main(sys.argv[1:])
