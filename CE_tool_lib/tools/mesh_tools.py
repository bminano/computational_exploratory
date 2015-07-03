import h5py
import numpy as np
import os, os.path
import ConfigParser
import sys
import utils as u

def isMesh(parameters, variable):
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
			return os.path.isfile(os.path.join(fileName, 'summary.samrai'))
		if popType == 'statistical':
			stat_from = eval(parameters.get(variable, 'stat_from'))
			fileName = fileName.replace('[P]', str(stat_from))
			if dims >= 3:
				time_from = eval(parameters.get(variable, 'time_from'))
				fileName = fileName.replace('[T]', str(time_from))
			if dims == 4:
				group_from = eval(parameters.get(variable, 'group_from'))
				fileName = fileName.replace('[G]', str(group_from))
			return os.path.isfile(os.path.join(fileName, 'summary.samrai'))
	except:
		return False


def readMeshData(parameters, variable):
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
				aux_init_data = readSpatialData(fileName, field, parameters, variable)
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
							aux_init_data = np.ndarray(shape=(var.size, round((stat_to - stat_from)/stat_step + 1)), dtype='float')
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
					print 'ERROR: Statistical population for variable ' + variable + ' must have "[P]" and "[T]" wildcards.'
					 
				try:
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
					time_step = 1
					if parameters.has_option(variable, 'time_step'):
						time_step = eval(parameters.get(variable, 'time_step'))
					stat_from = eval(parameters.get(variable, 'stat_from'))
					stat_to = eval(parameters.get(variable, 'stat_to'))
					stat_step = 1
					if parameters.has_option(variable, 'stat_step'):
						stat_step = eval(parameters.get(variable, 'stat_step'))
					initial = True
					i = 0
					for index_time in u.frange(time_from, time_to + time_step, time_step):
						j = 0
						for index_stat in u.frange(stat_from, stat_to + stat_step, stat_step):
							fName = fileName.replace('[P]', str(index_stat)).replace('[T]', str(index_time))
							var = readField (fName, field)
							if initial:
								aux_init_data = np.ndarray(shape=(round((time_to - time_from)/time_step + 1), var.size, round((stat_to - stat_from)/stat_step + 1)), dtype='float')
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
					print 'ERROR: Spatial population for variable ' + variable + ' must have "[T]" and "[G]" wildcards.'
					 
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
					print 'ERROR: Statistical population for variable ' + variable + ' must have "[P]", "[G]" and "[T]" wildcards.'
					 
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
					stat_from = eval(parameters.get(variable, 'stat_from'))
					stat_to = eval(parameters.get(variable, 'stat_to'))
					stat_step = 1
					if parameters.has_option(variable, 'stat_step'):
						stat_step = eval(parameters.get(variable, 'stat_step'))
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
									aux_init_data = np.ndarray(shape=(round((group_to - group_from)/group_step + 1), round((time_to - time_from)/time_step + 1), var.size, round((stat_to - stat_from)/stat_step + 1)), dtype='float')
									initial = False
								aux_init_data[i, j, :, k] = np.resize(var, var.size)
								k = k + 1
							j = j + 1
						i = i + 1
			
				except ValueError as e:
					print 'ERROR: ', e

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Statistical population must have group_from, group_to, time_from, time_to, stat_from and stat_to configurations.'
	
		return aux_init_data
	except Exception as e:
		print 'ERROR: ', e

def readSpatialData(fileName, field, parameters, variable):
	periodical = parameters.getboolean(variable, 'periodical')
	stencil = parameters.getint(variable, 'stencil')
	var = readField (fileName, field)
	aux_init_data = []
	for (i, j, k), val in np.ndenumerate(var):
		i_min = i - stencil
		i_max = i + stencil + 1
		j_min = j - stencil
		j_max = j + stencil + 1
		k_min = k - stencil
		k_max = k + stencil + 1
		if not periodical:
			i_min = max(i_min, 0)
			i_max = min(i_max, var.shape[0])
			j_min = max(j_min, 0)
			j_max = min(j_max, var.shape[1])
			k_min = max(k_min, 0)
			k_max = min(k_max, var.shape[2])
		pop = np.empty(((i_max-i_min) * (j_max-j_min) * (k_max-k_min)))
		index = 0
		for ni in xrange(i_min,i_max):
			for nj in xrange(j_min,j_max):
				for nk in xrange(k_min,k_max):
					if periodical:
						ni = ni % var.shape[0]
						nj = nj % var.shape[1]
						nk = nk % var.shape[2]
					pop[index] = var[ni, nj, nk]
					index = index + 1
		aux_init_data.append(np.array(pop))
	return aux_init_data

def readField (folder, field):
	#Read mesh information
	f_sum = h5py.File(folder + '/summary.samrai', "r")
	nProcessors  = f_sum['/BASIC_INFO/number_processors']
	nPatches     = f_sum['/BASIC_INFO/number_patches_at_level']
	patchExtents = f_sum['/extents/patch_extents']
	patchMap     = f_sum['/extents/patch_map']
	varNames = f_sum['/BASIC_INFO/var_names']
	
	maximum = [0, 0, 0]
	minimum = [999999, 999999, 999999]
	for i in xrange(len(patchExtents)):
		maximum[0] = max(maximum[0], patchExtents[i][1][0])
		maximum[1] = max(maximum[1], patchExtents[i][1][1])
		maximum[2] = max(maximum[2], patchExtents[i][1][2])
		minimum[0] = min(minimum[0], patchExtents[i][0][0])
		minimum[1] = min(minimum[1], patchExtents[i][0][1])
		minimum[2] = min(minimum[2], patchExtents[i][0][2])
	size = [(maximum[0] - minimum[0]) + 1 ,(maximum[1] - minimum[1]) + 1 ,(maximum[2] - minimum[2]) + 1]

	data = np.zeros(shape=(size[0], size[1], size[2]))

	for iPatch in xrange(nPatches[0]):
    		iProc     = patchMap[iPatch][0]
		iProcStr = str(iProc).zfill(5)
		iPatchStr = str(iPatch).zfill(5)
		rangeX = (patchExtents[iPatch][0][0], patchExtents[iPatch][1][0]+1)
		rangeY = (patchExtents[iPatch][0][1], patchExtents[iPatch][1][1]+1)
		rangeZ = (patchExtents[iPatch][0][2], patchExtents[iPatch][1][2]+1)
    		sizeX = patchExtents[iPatch][1][0] - patchExtents[iPatch][0][0] + 1;
    		sizeY = patchExtents[iPatch][1][1] - patchExtents[iPatch][0][1] + 1;
    		sizeZ = patchExtents[iPatch][1][2] - patchExtents[iPatch][0][2] + 1;
		f_data = h5py.File(folder + '/processor_cluster.' + iProcStr + '.samrai', "r")
		tmp = f_data['/processor.' + iProcStr + '/level.00000/patch.' + iPatchStr + '/' + field]
		tmp = np.reshape(tmp, (sizeX,sizeY,sizeZ), order="F")
		data[rangeX[0]:rangeX[1],rangeY[0]:rangeY[1],rangeZ[0]:rangeZ[1]] = tmp[:,:,:]
		f_data.close()
	f_sum.close()

	return data
