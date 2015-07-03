import numpy as np
import networkx as nx
import sys, getopt

def main(argv):

	#Script usage
    	try:
        	opts, args = getopt.getopt(argv,"ha:b:",["help", "fileName=", "field="])
    	except getopt.GetoptError:
        	print 'USAGE: python workflow_graph.py -p <parameter-file>'
        	sys.exit(2)
    	for opt, arg in opts:
        	if opt == '-h':
            		print 'USAGE: python workflow_graph.py -p <parameter-file>'
            		sys.exit()
        	elif opt in ("-a", "--fileName"):
            		fileName = arg
        	elif opt in ("-b", "--field"):
            		field = arg

	g=nx.DiGraph(nx.read_dot(fileName))
	aux_init_data = [None] * len(g.nodes())
	for v in g.nodes():
		pop = np.ndarray(g.out_degree(v), dtype='float')
		index = 0
		for vn in g.neighbors(v):
			pop[index] = g.node[vn][field]
			index = index + 1
		aux_init_data[int(v[1:])] = pop
	g.clear()

	np.save(field, aux_init_data)

if __name__ == "__main__":
	main(sys.argv[1:])
