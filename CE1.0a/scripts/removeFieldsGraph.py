import re
import sys, getopt

def main():
	f = open("graph1_1.gv", 'r')
	fout = open("graph1_1_initial.gv", 'w')
	fields = ["username", "numTweets", "firstTweetTime", "lastTweetTime", "text", "count", "firstInteraction"]


	for line in f:
		for field in fields:
			line = re.sub(re.escape(field) + r'[ ]*=[ ]*[^,"]*,?([ \]])', r'\1', line)
			line = re.sub(re.escape(field) + r'[ ]*=[ ]*"[^"]*",?([ \]])', r'\1', line)
		# Remove last comma
		line = re.sub(r',[ ]*\]', ']', line)
		# Delete empty label structure
		line = re.sub(r'\[[ ]*\]', '', line)
		# Delete graph labels
		line = re.sub(r'^[^\[]*=[^\]]*$', '', line)
	    	fout.write(line)

	f.close()
	fout.close()

if __name__ == "__main__":
    main()
