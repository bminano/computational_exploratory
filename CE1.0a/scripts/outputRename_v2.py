import getopt
import re
from stat import S_ISDIR, ST_CTIME, ST_MODE
import os, sys, time

def processDir(directory):
    counter = 0
    entries = (os.path.join(directory, fn) for fn in os.listdir(directory))
    entries = ((os.stat(path), path) for path in entries)

    # leave only regular files, insert creation date
    entries = ((stat[ST_CTIME], path) for stat, path in entries if S_ISDIR(stat[ST_MODE]))

    for cdate, path in sorted(entries):
        if len(re.findall(r'visit_dump_[0-9]+', os.path.basename(path))) > 0 or len(re.findall(r'visit_dump.[0-9]+', os.path.basename(path))) > 0:
            os.rename(os.path.join(directory,os.path.basename(path)), os.path.join(directory,'output.' + str(counter)))
            counter = counter + 1
        else:
            processDir(os.path.join(directory,os.path.basename(path)))



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
