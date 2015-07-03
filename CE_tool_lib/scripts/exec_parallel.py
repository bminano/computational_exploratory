import sys, getopt
import os, os.path
from subprocess import call
import ConfigParser
import StringIO
import re
import itertools
import multiprocessing as mp

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

def getTyped(s):
	if s.count('.') > 0:
	        return float(s)
	else:
	        return int(s)

def isNum(s):
    	try:
        	int(s)
		return True
    	except ValueError:
	    	try:
	        	float(s)
			return True
		except ValueError:
			return False

def isString(s):
    	if re.match(r'"[^"]+"', s) != None:
		return True
	return False

def isList (s):
	lista = re.split(r' (?=(?:[^\[]*\[[^\[]*\])*[^\]]*$)', s)
	return len(lista) > 1


def execSimulation((execName, parameters, nprocs)):
	#Create the parameter file
	with open("params" + str(mp.current_process().pid) + ".input", "w") as newFile:
	    newFile.write(parameters)
	#Execute mono or multiprocessor
	if nprocs > 1:
		call(["mpirun", "-np", str(nprocs), "./" + execName, "params" + str(mp.current_process().pid) + ".input"])
	else:
		call(["./" + execName, "params" + str(mp.current_process().pid) + ".input"])
	#Remove the parameter file
	call(["rm", "params" + str(mp.current_process().pid) + ".input"])

def parallelizeParameters(paramFile):
	parameters = []

	#Open the original parameter file
	original = paramFile.get('Execution', 'param-file')
	with open (original, "r") as originalFile:
		pFile=originalFile.read()
	lists = []
	replacements = []
	#Read parallel section
	for metrics_par in paramFile.options('Parallel'):
		if metrics_par.count('#'):
			value = paramFile.get('Parallel' , metrics_par)
			#Parse range
			if value.count('..'):
				values = value.split('..')
				init = eval(values[0])
				end = eval(values[1])
				if len(values) > 2:
					step = eval(values[2])
				else:
					step = 1
				lists.append(frange(init, end, step))
			#Parse list
			else:
				values = value.split(' ')
				lists.append(values)
			replacements.append('#' + metrics_par)

	#Load extra files if set
	extrafiles = {}
	if (paramFile.has_section('Extra-Files')):
		for efi in paramFile.options('Extra-Files'):
			ef = paramFile.get('Extra-Files' , efi)
			with open (ef, "r") as originalFile:
				eFile=originalFile.read()
			extrafiles[ef] = eFile

	#Generate all combinations
	combinations = list(itertools.product(*lists))
	for comb in combinations:
		#Create a new parameter file
		newParams = pFile
		for rep in xrange(len(replacements)):
			newParams = newParams.replace(replacements[rep], str(comb[rep]))
		parameters.append(newParams)
		#Process extra files if available
		for fname in extrafiles:
			for rep in xrange(len(replacements)):
				fname = fname.replace(replacements[rep], str(comb[rep]))
				extrafiles[ef] = extrafiles[ef].replace(replacements[rep], str(comb[rep]))
			with open(fname, "w") as newFile:
			    newFile.write(extrafiles[ef])

	return parameters

def main(argv):
	#Script usage
    	try:
        	opts, args = getopt.getopt(argv,"hp:",["help", "parameter-file="])
    	except getopt.GetoptError:
        	print 'USAGE: python exec_parallel.py -p <parameter-file>'
        	sys.exit(2)
    	for opt, arg in opts:
        	if opt == '-h':
            		print 'USAGE: python exec_parallel.py -p <parameter-file>'
            		sys.exit()
        	elif opt in ("-p", "--parameter-file"):
            		paramFile = arg


	#Read parameter file
	parameters = ConfigParser.RawConfigParser()
	parameters.optionxform=str
    	try:
		parameters.read(paramFile)
    	except:
		print 'ERROR: The parameter file is not correct'
		sys.exit(2)

	procs = parameters.getint('Parallel', 'nprocs-reps')
	procs_exec = parameters.getint('Parallel', 'nprocs-exec')
	exe = parameters.get('Execution', 'exe')

	#Parallel processing
    	pool = mp.Pool(processes=procs)
	pool.map(execSimulation, itertools.izip(itertools.repeat(exe), parallelizeParameters(parameters), itertools.repeat(procs_exec)))
	pool.close()
	pool.join()


if __name__ == "__main__":
	main(sys.argv[1:])
