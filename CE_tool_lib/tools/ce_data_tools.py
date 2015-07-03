import h5py
import numpy as np
import os, os.path
import ConfigParser
import sys
import scipy.ndimage as ndimage
import utils as u

def isCEData(parameters, variable):
	try:
		fileName = parameters.get(variable, 'input_files')
		popType = parameters.get(variable, 'population_type')
		dims = parameters.getint(variable, 'dimensions')
		if dims < 1 or dims > 4:
			print 'ERROR: Number of dimensions ' + dims + ' for variable ' + variable + ' is incorrect. It should be from 1 up to 4.'
		if popType != 'statistical' and popType != 'spatial':
			print 'ERROR: Population type ' + popType + ' for variable ' + variable + ' incorrect.'
		if popType == 'spatial':
			if dims == 1:
				print 'ERROR: Variable ' + variable + ' should have more than one dimension to use spatial population_type.'
		if parameters.has_option(variable, 'stat_from'):
			stat_from = eval(parameters.get(variable, 'stat_from'))
			fileName = fileName.replace('[P]', str(stat_from))
		if parameters.has_option(variable, 'time_from'):
			time_from = eval(parameters.get(variable, 'time_from'))
			fileName = fileName.replace('[T]', str(time_from))
		if parameters.has_option(variable, 'group_from'):
			group_from = eval(parameters.get(variable, 'group_from'))
			fileName = fileName.replace('[G]', str(group_from))

		hdf = h5py.File(fileName, mode='r')
		hdf.close()
		return True
	except:
		return False

def readCEData(parameters, variable):
	try:
		fileName = parameters.get(variable, 'input_files')
		field = parameters.get(variable, 'field')
		popType = parameters.get(variable, 'population_type')
		dims = parameters.getint(variable, 'dimensions')
		if popType != 'statistical' and popType != 'spatial':
			print 'ERROR: Population type ' + popType + ' for field ' + field + ' incorrect.'
		if dims < 1 or dims > 4:
			print 'ERROR: Number of dimensions ' + dims + ' for field ' + field + ' is incorrect. It should be from 1 up to 4.'

		stat_from = ""
		time_from = ""
		group_from = ""
		if parameters.has_option(variable, 'stat_from'):
			stat_from = eval(parameters.get(variable, 'stat_from'))
			stat_to = eval(parameters.get(variable, 'stat_to'))
			stat_step = 1
			if parameters.has_option(variable, 'stat_step'):
				stat_step = eval(parameters.get(variable, 'stat_step'))
		if parameters.has_option(variable, 'time_from'):
			time_from = eval(parameters.get(variable, 'time_from'))
			time_to = eval(parameters.get(variable, 'stat_to'))
			time_step = 1
			if parameters.has_option(variable, 'time_step'):
				time_step = eval(parameters.get(variable, 'time_step'))
		if parameters.has_option(variable, 'group_from'):
			group_from = eval(parameters.get(variable, 'group_from'))
			group_to = eval(parameters.get(variable, 'group_to'))
			group_step = 1
			if parameters.has_option(variable, 'group_step'):
				group_step = eval(parameters.get(variable, 'group_step'))

		#Read actual dimensions in the field
		fName = fileName.replace('[P]', str(stat_from)).replace('[T]', str(time_from)).replace('[G]', str(group_from))
		fileDims = getDataDims(fName, field)
		dimesionsToAdd = dims - fileDims

		if dims < fileDims:
			print 'ERROR: Variable ' + variable + ' has more dimensions than specified.'	

		if dims == 1:
			if popType == 'spatial':
				print 'ERROR: Variable ' + variable + ' should have more than one dimension to use spatial population_type.'
		if dimesionsToAdd == 0:
			if popType == 'spatial':
				aux_init_data = readSpatialData(fileName, field, parameters, variable)
			if popType == 'statistical':
				aux_init_data = readField(fileName, field)
		if dimesionsToAdd == 1:
			if popType == 'spatial':
				if fileName.count('[T]') != 1:
					print 'ERROR: Spatial population for variable ' + variable + ' must have "[T]" wildcard.'
				try:
					time_from = eval(parameters.get(variable, 'time_from'))
					time_to = eval(parameters.get(variable, 'time_to'))
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
							aux_init_data = np.ndarray(shape=(var.shape + (round((stat_to - stat_from)/stat_step + 1),)), dtype='float')
							initial = False
						aux_init_data[..., i] = var
						i = i + 1
				except ValueError as e:
					import traceback
					print traceback.format_exc()
					print 'ERROR: ', e

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Statistical population must have stat_from and stat_to configurations.'	
		if dimesionsToAdd == 2:
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
								aux_init_data = np.ndarray(shape=((round((time_to - time_from)/time_step + 1),) + var.shape + (round((stat_to - stat_from)/stat_step + 1),)), dtype='float')
								initial = False
							aux_init_data[i, ..., j] = var
							j = j + 1
						i = i + 1
			
				except ValueError as e:
					print 'ERROR: ', e

				except ConfigParser.NoOptionError:
					print 'ERROR: Error in ', variable, '. Statistical population must have time_from, time_to, stat_from and stat_to configurations.'
		if dimesionsToAdd == 3:
			if popType == 'spatial':
				print 'ERROR: Error in ', variable, '. Cannot add more than 2 extra dimensions to the spatial data provided.'
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
									aux_init_data = np.ndarray(shape=((round((group_to - group_from)/group_step + 1), round((time_to - time_from)/time_step + 1),) + var.shape + (round((stat_to - stat_from)/stat_step + 1),)), dtype='float')
									initial = False
								aux_init_data[i, j, ..., k] = var
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


def neighboursFilter(arr, **kwargs):
	return arr.tolist()

def readSpatialData(fileName, field, parameters, variable):
	periodical = parameters.getboolean(variable, 'periodical')
	stencil = parameters.getint(variable, 'stencil')
	var = readField (fileName, field)
	aux_init_data = ndimage.generic_filter(var, neighboursFilter, size=stencil, mode='wrap')
	return aux_init_data

def readField (folder, field):
	#Read mesh information
	hdf = h5py.File(folder, mode='r')
	data = hdf[field][()]
	hdf.close()
	return data

def getDataDims (folder, field):
	hdf = h5py.File(folder, mode='r')
	data = hdf[field][()]
	hdf.close()
	return len(data.shape)

