import numpy as np
import networkx as nx
import sys, getopt

def main(argv):

	#Script usage
    	try:
        	opts, args = getopt.getopt(argv,"ha:b:c:",["help", "fileName=", "field=", "type="])
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
        	elif opt in ("-c", "--type"):
            		fieldType = arg

	g=nx.DiGraph(nx.read_dot(fileName))
	if fieldType == 'edge':
		aux_init_data = np.ndarray(len(g.edges()), dtype='float')
		indexE = 0
		for e in g.edges():
			aux_init_data[indexE] = g.edge[e[0]][e[1]][field]
			indexE = indexE + 1
	elif fieldType == 'node':
		aux_init_data = np.ndarray(len(g.nodes()), dtype='float')
		for v in g.nodes():	
			aux_init_data[int(v[1:])] = g.node[v][field]
	g.clear()

	np.save(field, aux_init_data)

if __name__ == "__main__":
	main(sys.argv[1:])
