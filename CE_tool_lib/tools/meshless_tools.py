import Silo
import numpy as np
import os, os.path
import ConfigParser
import math
import sys
import itertools
import utils as u

def isMeshless(parameters, variable):
	try:
		fileName = parameters.get(variable, 'input_files')
		popType = parameters.get(variable, 'population_type')
		dims = parameters.getint(variable, 'dimensions')
		if dims < 2 or dims > 4:
			print 'ERROR: Number of dimensions ' + dims + ' for variable ' + variable + ' is incorrect. It should be 2, 3, or 4.'
			
		if popType != 'statistical' and popType != 'spatial':
			print 'ERROR: Population type ' + popType + ' for variable ' + variable + ' incorrect.'
			
		if popType == 'spatial':
			if dims >= 3:
				time_from = eval(parameters.get(variable, 'time_from'))
				fileName = fileName.replace('[T]', str(time_from))
			if dims == 4:
				group_from = eval(parameters.get(variable, 'group_from'))
				fileName = fileName.replace('[G]', str(group_from))
			return os.path.isfile(os.path.join(fileName, 'summary'))
		elif popType == 'statistical':
			stat_from = eval(parameters.get(variable, 'stat_from'))
			fileName = fileName.replace('[P]', str(stat_from))
			if dims >= 3:
				time_from = eval(parameters.get(variable, 'time_from'))
				fileName = fileName.replace('[T]', str(time_from))
			if dims == 4:
				group_from = eval(parameters.get(variable, 'group_from'))
				fileName = fileName.replace('[G]', str(group_from))
			return os.path.isfile(os.path.join(fileName, 'summary'))
	except:
		return False

def readMeshlessData(parameters, variable):
	try:
		fileName = parameters.get(variable, 'input_files')
		field = parameters.get(variable, 'field')
		popType = parameters.get(variable, 'population_type')
		dims = parameters.getint(variable, 'dimensions')
		if popType != 'statistical' and popType != 'spatial':
			print 'ERROR: Population type ' + popType + ' for field ' + field + ' incorrect.'
			
		if dims < 2 or dims > 4:
			print 'ERROR: Number of dimensions ' + dims + ' for field ' + field + ' is incorrect. It should be 2, 3, or 4.'
			
		if dims == 2:
			if popType == 'spatial':
				return np.array(readSpatialData(fileName, field, parameters, variable))
			if popType == 'statistical':
				if fileName.count('[P]') != 1:
					print 'ERROR: Statistical population for variable ' + variable + ' must have "[P]" wildcard.'
					 
				try:
					stat_from = eval(parameters.get(variable, 'stat_from'))
					stat_to = eval(parameters.get(variable, 'stat_to'))
					stat_step = 1
					if parameters.has_option(variable, 'stat_step'):
						stat_step = eval(parameters.get(variable, 'stat_step'))
					initial = True
					i = 0
					for index_stat in u.frange(stat_from, stat_to + stat_step, stat_step):
						fName = fileName.replace('[P]', str(index_stat))
						var = readField (fName, field)
						if initial:
							aux_init_data = np.ndarray(shape=(var.shape[0], round((stat_to - stat_from)/stat_step + 1)), dtype='float')
							initial = False
						aux_init_data[:, i] = np.resize(var, var.size)
						i = i + 1
			
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Statistical population must have stat_from and stat_to configurations.'
						
		if dims == 3:
			if popType == 'spatial':
				if fileName.count('[T]') != 1:
					print 'ERROR: Spatial population for variable ' + variable + ' must have "[T]" wildcard.'
					 
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
						tmp = readSpatialData(fName, field, parameters, variable)
						if initial:
							aux_init_data = np.ndarray(shape=(round((time_to - time_from)/time_step + 1), len(tmp)), dtype=object)
							initial = False
						aux_init_data[i, :] = tmp[:]
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Spatial population must have time_from and time_to configurations.'
					
			if popType == 'statistical':
				if fileName.count('[P]') != 1 or fileName.count('[T]') != 1:
					print 'ERROR: Statistical population for variable ' + variable + ' must have "[P]" and "[T]" wildcard.'
					 
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
					for index_time in u.frange(time_from, time_to + time_step, time_step):
						j = 0
						for index_stat in u.frange(stat_from, stat_to + stat_step, stat_step):
							fName = fileName.replace('[P]', str(index_stat)).replace('[T]', str(index_time))
							var = readField (fName, field)
							if initial:
								aux_init_data = np.ndarray(shape=(round((time_to - time_from)/time_step + 1), var.shape[0], round((stat_to - stat_from)/stat_step + 1)), dtype='float')
								initial = False
							aux_init_data[i, :, j] = np.resize(var, var.size)
							j = j + 1
						i = i + 1
			
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Statistical population must have time_from, time_to, stat_from and stat_to configurations.'
						
		if dims == 4:
			if popType == 'spatial':
				if fileName.count('[T]') != 1 or fileName.count('[G]') != 1:
					print 'ERROR: Spatial population for variable ' + variable + ' must have "[T]" and "[G]" wildcard.'
					 
				try:
					group_from = eval(parameters.get(variable, 'group_from'))
					group_to = eval(parameters.get(variable, 'group_to'))
					group_step = 1
					if parameters.has_option(variable, 'group_step'):
						group_step = eval(parameters.get(variable, 'group_step'))
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
					time_step = 1
					if parameters.has_option(variable, 'time_step'):
						time_step = eval(parameters.get(variable, 'time_step'))
					initial = True
					i = 0
					for index_group in u.frange(group_from, group_to + group_step, group_step):
						j = 0
						for index_time in u.frange(time_from, time_to + time_step, time_step):
							fName = fileName.replace('[T]', str(index_time)).replace('[G]', str(index_group))
							tmp = readSpatialData(fName, field, parameters, variable)
							if initial:
								aux_init_data = np.ndarray(shape=(round((group_to - group_from)/group_step + 1), round((time_to - time_from)/time_step + 1), len(tmp)), dtype=object)
								initial = False
							aux_init_data[i, j, :] = tmp[:]
							j = j + 1
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Spatial population must have group_from, group_to, time_from and time_to configurations.'
					
			if popType == 'statistical':
				if fileName.count('[P]') != 1 or fileName.count('[T]') != 1 or fileName.count('[G]') != 1:
					print 'ERROR: Statistical population for variable ' + variable + ' must have "[P]", "[G]" and "[T]" wildcard.'
					 
				try:
					group_from = eval(parameters.get(variable, 'group_from'))
					group_to = eval(parameters.get(variable, 'group_to'))
					group_step = 1
					if parameters.has_option(variable, 'group_step'):
						group_step = eval(parameters.get(variable, 'group_step'))
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
					for index_group in u.frange(group_from, group_to + group_step, group_step):
						j = 0
						for index_time in u.frange(time_from, time_to + time_step, time_step):
							k = 0
							for index_stat in u.frange(stat_from, stat_to + stat_step, stat_step):
								fName = fileName.replace('[P]', str(index_stat)).replace('[T]', str(index_time)).replace('[G]', str(index_group))
								var = readField (fName, field)
								if initial:
									aux_init_data = np.ndarray(shape=(round((group_to - group_from)/group_step + 1), round((time_to - time_from)/time_step + 1), var.shape[0], round((stat_to - stat_from)/stat_step + 1)), dtype='float')
									initial = False
								aux_init_data[i, j, :, k] = np.resize(var, var.size)
								k = k + 1
							j = j + 1
						i = i + 1
				except ValueError as e:
					print 'ERROR: ', e
					

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Statistical population must have stat_from and stat_to configurations.'
						

		return aux_init_data
	except Exception as e:
		print 'ERROR: ', e

def readSpatialData(fileName, field, parameters, variable):
	periodical = parameters.getboolean(variable, 'periodical')
	radius = parameters.getfloat(variable, 'radius')
	radius2 = radius*radius
	aux_init_data = []
	var = readField (fileName, field)
	coords = particlesToMesh(fileName, field, radius)
	ndims = len(coords) - 1
	domainSize = coords[0].shape
	index = 0
	for i_cell, val in np.ndenumerate(coords[0]):
		particles = coords[ndims][i_cell]
		for i_part in xrange(len(particles)):
			pop = []
			xa = coords[0][i_cell][i_part]
			if ndims >= 2:
				ya = coords[1][i_cell][i_part]
				if ndims == 3:
					za = coords[2][i_cell][i_part]
			iterator = itertools.product(xrange(-1,2), repeat=ndims)
			for addend in iterator:
				ni_cell = tuple((a + b) % c for a, b, c in zip(i_cell, addend, domainSize))
				nparticles = coords[ndims][ni_cell]
				if len(nparticles) > 0:
					npparticles = np.array(nparticles)
					indices = np.where(npparticles != particles[i_part])
					lisx = np.array(coords[0][ni_cell])
					xb = lisx[indices[0]]
					dist = xb-xa
					indices2 = np.where(dist < 0)
					dist[indices2[0]] = -dist[indices2[0]]
					#periodic considerations. Allways pick the nearest distance
					if periodical:
						indices2a = np.where(dist > domainSize[0] * 0.5)
						dist[indices2a[0]] = domainSize[0] - dist[indices2a[0]]
					dist = dist * dist
					if ndims >= 2:
						lisy = np.array(coords[1][ni_cell])
						yb = lisy[indices[0]]
						dy = yb-ya
						indices3 = np.where(dy < 0)
						dy[indices3[0]] = -dy[indices3[0]]
						#periodic considerations. Allways pick the nearest distance
						if periodical:
							indices3a = np.where(dy > domainSize[1] * 0.5)
							dy[indices3a[0]] = domainSize[1] - dy[indices3a[0]]
						dist = dist + dy * dy
						if ndims == 3:
							lisz = np.array(coords[2][ni_cell])
							zb = lisz[indices[0]]
							dz = zb-za
							indices4 = np.where(dz < 0)
							dz[indices4[0]] = -dz[indices4[0]]
							#periodic considerations. Allways pick the nearest distance
							if periodical:
								indices4a = np.where(dz > domainSize[2] * 0.5)
								dz[indices4a[0]] = domainSize[2] - dz[indices4a[0]]
							dist = dist + dz * dz
					indices5 = np.where(dist <= radius2)
					pop.extend(var[npparticles[indices[0]][indices5[0]]])
			index = index + 1
			aux_init_data.append(np.array(pop))
	return aux_init_data

def readField (folder, field):
	first = True
	for file in sorted(listOfFiles(folder)):
		db = Silo.Open(folder + "/" + file)
		db.SetDir("level_00000/patch_" + file[file.find('.') + 1:file.rfind('.')])
		if first:
	       		data = np.array(db.GetVar(field + "__data"))
		else:
	       		data = np.append(data, np.array(db.GetVar(field + "__data")))
		db.Close()
		first = False

	return data

def particlesToMesh(folder, field, radius):
	# Join multiprocessor information
	first = True
	ndims = 1
 	for file in sorted(listOfFiles(folder)):
	 	db = Silo.Open(folder + "/" + file)
		db.SetDir("level_00000/patch_" + file[file.find('.') + 1:file.rfind('.')])
		if first:
			min_extents = np.array(db.GetVar(field + "PointMesh_min_extents"))
			max_extents = np.array(db.GetVar(field + "PointMesh_max_extents"))
			ndims = len(min_extents)
			x_var = np.array(db.GetVar(field + "PointMesh_coord0"))
		else:
			min_extents = np.minimum(min_extents, np.array(db.GetVar(field + "PointMesh_min_extents")))
			max_extents = np.maximum(max_extents, np.array(db.GetVar(field + "PointMesh_max_extents")))
			x_var = np.append(x_var, np.array(db.GetVar(field + "PointMesh_coord0")))
		if ndims >= 2:
			if first:
				y_var = np.array(db.GetVar(field + "PointMesh_coord1"))
			else:
				y_var = np.append(y_var, np.array(db.GetVar(field + "PointMesh_coord1")))
		if ndims == 3:
			if first:
				z_var = np.array(db.GetVar(field + "PointMesh_coord2"))
			else:
				z_var = np.append(z_var, np.array(db.GetVar(field + "PointMesh_coord2")))
		first = False
		db.Close()

	numberOfCells = np.ndarray(shape=(ndims), dtype=int)
	for i in xrange(ndims):
		numberOfCells[i] = math.ceil((max_extents[i] - min_extents[i])/radius)

	particleId = np.ndarray(shape=(numberOfCells), dtype=object)
	x = np.ndarray(shape=(numberOfCells), dtype=object)
	deltax = (max_extents[0] - min_extents[0])/numberOfCells[0]
	if ndims >= 2:
		y = np.ndarray(shape=(numberOfCells), dtype=object)
		deltay = (max_extents[1] - min_extents[1])/numberOfCells[1]
	if ndims == 3:
		z = np.ndarray(shape=(numberOfCells), dtype=object)
		deltaz = (max_extents[2] - min_extents[2])/numberOfCells[2]
	for index, value in np.ndenumerate(x):
		x[index] = list()
		if ndims >= 2:
			y[index] = list()
		if ndims == 3:
			z[index] = list()
		particleId[index] = list()

	#Particle to mesh
	for i in xrange(0,len(x_var)):
		posx = x_var[i]
		mi = int(x_var[i]/deltax)
		if mi == numberOfCells[0]:
			mi = mi-1
		if ndims >= 2:
			posy = y_var[i]
			mj = int(y_var[i]/deltay)
			if mj == numberOfCells[1]:
				mj = mj-1
		if ndims == 3:
			posz = z_var[i]
			mk = int(z_var[i]/deltaz)
	 		if mk == numberOfCells[2]:
				mk = mk-1
		if ndims == 1:			
			x[mi].append(posx)
			particleId[mi].append(i)
		if ndims == 2:			
			x[mi, mj].append(posx)
			y[mi, mj].append(posy)
			particleId[mi, mj].append(i)
		if ndims == 3:			
			x[mi, mj, mk].append(posx)
			y[mi, mj, mk].append(posy)
			z[mi, mj, mk].append(posz)
			particleId[mi, mj, mk].append(i)

	if ndims == 1:			
		return x, particleId
	if ndims == 2:	
		return x, y, particleId
	if ndims == 3:	
 		return x, y, z, particleId


def listOfFiles(directory):
	return [ f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f)) and f.startswith("processor_cluster.") ]
