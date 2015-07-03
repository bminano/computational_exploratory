import numpy as np
import networkx as nx
import os, os.path
import ConfigParser
from subprocess import call
import pygraphviz as pgv
import sys
import utils as u

def isGraph(parameters, variable):
	return parameters.has_option(variable, 'field_type')

def readGraphData(parameters, variable):
	try:
		fieldType = parameters.get(variable, 'field_type')
		fileName = parameters.get(variable, 'input_files')
		field = parameters.get(variable, 'field')
		popType = parameters.get(variable, 'population_type')
		dims = parameters.getint(variable, 'dimensions')
		if popType != 'statistical' and popType != 'spatial':
			print 'ERROR: Population type ' + popType + ' for field ' + field + ' incorrect.'
			
		if fieldType != 'edge' and fieldType != 'node':
			print 'ERROR: Field type' + fieldType + ' for field ' + field + ' incorrect.'
			
		if dims < 2 or dims > 4:
			print 'ERROR: Number of dimensions ' + dims + ' for field ' + field + ' is incorrect. It should be 2, 3, or 4.'
			
		if dims == 2:
			if popType == 'spatial':
				if fieldType == 'edge':
					print 'ERROR: Edge, ' + field + ', population cannot be spatial.'
					
				aux_init_data = readGraphFieldSpatial(fileName, field)
			if popType == 'statistical':
				if fileName.count('[P]') != 1:
					print 'ERROR: Statistical population for bidimensional variable ' + variable + ' must have "[P]" wildcard. E.g: ./output_[P]/result.dot'
					 
				try:
					stat_from = eval(parameters.get(variable, 'stat_from'))
					stat_to = eval(parameters.get(variable, 'stat_to'))
					stat_step = 1
					if parameters.has_option(variable, 'stat_step'):
						stat_step = eval(parameters.get(variable, 'stat_step'))
					initial = True
					i = 0
					for index in u.frange(stat_from, stat_to + stat_step, stat_step):
						print stat_from, index
						fName = fileName.replace('[P]', str(index))
						g = readGraphField(fName, field, fieldType)
						if initial:
							aux_init_data = np.ndarray(shape=(len(g), round((stat_to - stat_from)/stat_step + 1)), dtype='float')
							initial = False
						aux_init_data[:, i] = g[:]
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Bidimensional statistical population must have stat_from and stat_to configurations.'
					
		if dims == 3:
			if popType == 'spatial':
				if fileName.count('[T]') != 1:
					print 'ERROR: Spatial population for tridimensional variable ' + variable + ' must have "[T]" wildcard. E.g: ./output_[T]/result.dot'
					 
				aux_init_data = []
				if fieldType == 'edge':
					print 'ERROR: Edge, ' + field + ', population cannot be spatial.'
					
				try:
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
					time_step = 1
					if parameters.has_option(variable, 'time_step'):
						time_step = eval(parameters.get(variable, 'time_step'))
					initial = True
					i = 0
					for index in u.frange(time_from, time_to + time_step, time_step):
						fName = fileName.replace('[T]', str(index))
						tmp = readGraphFieldSpatial(fName, field)
						if initial:
							aux_init_data = np.ndarray(shape=(round((time_to - time_from)/time_step + 1), len(tmp)), dtype=object)
							initial = False
						aux_init_data[i, :] = tmp[:]
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					
				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Tridimensional spatial population must have time_from and time_to configurations.'
						
			if popType == 'statistical':
				if fileName.count('[P]') != 1 or fileName.count('[T]') != 1:
					print 'ERROR: Statistical population for tridimensional variable ' + variable + ' must have "[P]" and "[T]" wildcards. E.g: ./output_[P]/result[T].dot'
					 
				try:
					stat_from = eval(parameters.get(variable, 'stat_from'))
					stat_to = eval(parameters.get(variable, 'stat_to'))
					stat_step = 1
					if parameters.has_option(variable, 'stat_step'):
						stat_step = eval(parameters.get(variable, 'stat_step'))
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
					time_step = 1
					if parameters.has_option(variable, 'time_step'):
						time_step = eval(parameters.get(variable, 'time_step'))
					initial = True
					i = 0
					for index_t in u.frange(time_from, time_to + time_step, time_step):
						j = 0
						for index_s in u.frange(stat_from, stat_to + stat_step, stat_step):
							fName = fileName.replace('[P]', str(index_s)).replace('[T]', str(index_t))
							g = readGraphField(fName, field, fieldType)
							if initial:
								aux_init_data = np.ndarray(shape=(round((time_to - time_from)/time_step + 1), len(g), round((stat_to - stat_from)/stat_step + 1)), dtype='float')
								initial = False
							aux_init_data[i, :, j] = g[:]
							j = j + 1
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Tridimensional statistical population must have time_from, time_to, stat_from and stat_to configurations.'
							
		if dims == 4:
			if popType == 'spatial':
				if fileName.count('[T]') != 1 or fileName.count('[G]') != 1:
					print 'ERROR: Spatial population for 4-dimensional variable ' + variable + ' must have "[T]" and "[G]" wildcards. E.g: ./output_[T]_[G]/result.dot'
					 
				aux_init_data = []
				if fieldType == 'edge':
					print 'ERROR: Edge, ' + field + ', population cannot be spatial.'
					
				try:
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
					time_step = 1
					if parameters.has_option(variable, 'time_step'):
						time_step = eval(parameters.get(variable, 'time_step'))
					group_from = eval(parameters.get(variable, 'group_from'))
					group_to = eval(parameters.get(variable, 'group_to'))
					group_step = 1
					if parameters.has_option(variable, 'group_step'):
						group_step = eval(parameters.get(variable, 'group_step'))
					initial = True
					i = 0
					for index_g in u.frange(group_from, group_to + group_step, group_step):
						j = 0
						for index_t in u.frange(time_from, time_to + time_step, time_step):
							fName = fileName.replace('[T]', str(index_t)).replace('[G]', str(index_g))
							tmp = readGraphFieldSpatial(fName, field)
							if initial:
								aux_init_data = np.ndarray(shape=(round((group_to - group_from)/group_step + 1), round((time_to - time_from)/time_step + 1), len(tmp)), dtype=object)
								initial = False
							aux_init_data[i, j, :] = tmp[:]
							j = j + 1
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					
				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. 4-dimensional spatial population must have group_from, group_to, time_from and time_to configurations.'
					
			if popType == 'statistical':
				if fileName.count('[P]') != 1 or fileName.count('[T]') != 1 or fileName.count('[G]') != 1:
					print 'ERROR: Statistical population for 4-dimensional variable ' + variable + ' must have "[P]" and "[T]" and "[G]" wildcards. E.g: ./output_[P]_[G]/result[T].dot'
					 
				try:
					stat_from = eval(parameters.get(variable, 'stat_from'))
					stat_to = eval(parameters.get(variable, 'stat_to'))
					stat_step = 1
					if parameters.has_option(variable, 'stat_step'):
						stat_step = eval(parameters.get(variable, 'stat_step'))
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
					time_step = 1
					if parameters.has_option(variable, 'time_step'):
						time_step = eval(parameters.get(variable, 'time_step'))
					group_from = eval(parameters.get(variable, 'group_from'))
					group_to = eval(parameters.get(variable, 'group_to'))
					group_step = 1
					if parameters.has_option(variable, 'group_step'):
						group_step = eval(parameters.get(variable, 'group_step'))
					initial = True
					i = 0
					for index_g in u.frange(group_from, group_to + group_step, group_step):
						j = 0
						for index_t in u.frange(time_from, time_to + time_step, time_step):
							k = 0
							for index_s in u.frange(stat_from, stat_to + stat_step, stat_step):
								fName = fileName.replace('[P]', str(index_s)).replace('[T]', str(index_t)).replace('[G]', str(index_g))
								g = readGraphField(fName, field, fieldType)
								if initial:
									aux_init_data = np.ndarray(shape=(round((group_to - group_from)/group_step + 1), round((time_to - time_from)/time_step + 1), var.shape[0], round((stat_to - stat_from)/stat_step + 1)), dtype='float')
									initial = False
								aux_init_data[i, j, :, k] = g[:]
								k = k + 1
							j = j + 1
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Tridimensional statistical population must have group_from, group_to, time_from, time_to, stat_from and stat_to configurations.'
					

		return aux_init_data
	except Exception as e:
		print 'ERROR: ', e

def readGraphField(fileName, field, fieldType):
	Gtmp = pgv.AGraph(fileName)
	g = nx.DiGraph(Gtmp)
	if fieldType == 'edge':
		tmp = np.ndarray(g.number_of_edges(), dtype='float')
		indexE = 0
		for e, d in g.edges_iter(data=True):
			tmp[indexE] = d[field]
			indexE = indexE + 1
	elif fieldType == 'node':
		tmp = np.ndarray(g.number_of_nodes(), dtype='float')
		for v, d in g.nodes_iter(True):
			tmp[int(v[1:])] = d[field]
	g.clear()
	Gtmp.close()
	return tmp

def readGraphFieldSpatial(fileName, field):
	Gtmp = pgv.AGraph(fileName)
	g = nx.DiGraph(Gtmp)
	tmp = [None] * g.number_of_nodes()
	for v in g.nodes():
		pop = np.ndarray(g.out_degree(v), dtype='float')
		index = 0
		for vn in g.neighbors(v):
			pop[index] = g.node[vn][field]
			index = index + 1
		tmp[int(v[1:])] = pop
	g.clear()
	Gtmp.close()
	return tmp
	
