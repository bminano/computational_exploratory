import re
import sys, getopt

def main(argv):
	try:
        	opts, args = getopt.getopt(argv,"hi:o:")
    	except getopt.GetoptError:
        	print 'multi2mono.py -i <inputFile> -o <outputFile>'
        	sys.exit(2)
    	for opt, arg in opts:
        	if opt == '-h':
            		print 'multi2mono.py -i <inputFile> -o <outputFile>'
            		sys.exit()
		elif opt == '-i':
            		iFile = arg
        	elif opt == '-o':
            		oFile = arg

	f = open(iFile, 'r')
	fout = open(oFile, 'w')

	nodes = ""
	edges = ""

	initial = True
	for line in f:
		if initial:
			fout.write(line)
			initial = False
		if (len(re.findall(r'n[0-9]+\s*\[', line)) > 0):
			line = re.sub(r'n([0-9]+\s*\[)', r'\1', line)
		    	nodes = nodes + line
		if (len(re.findall(r'n[0-9]+\s*-[->]\s*n[0-9]+', line)) > 0):
			line = re.sub(r'n([0-9]+\s*-[->]\s*)n([0-9]+)', r'\1\2', line)
	    		edges = edges + line
	#Write the nodes first
	fout.write(nodes)
	#Write the edges first
	fout.write(edges)
	fout.write("}\n")
	f.close()
	fout.close()

if __name__ == "__main__":
    main(sys.argv[1:])
