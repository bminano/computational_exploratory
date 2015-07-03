'''
Graph reader.
Implements the reader for Boost's DOT output.
'''

import numpy as np
import networkx as nx
import os, os.path
import ConfigParser
from subprocess import call
import pygraphviz as pgv
import utils as u

def isGraph(parameters, variable):
    '''
    Checks the format.

    Input:
        parameters  configParser parameters
        variable    CE variable to read
    Returns:
                    True if the format is correct
    '''
    try:
        reader = parameters.get(variable, 'reader')
        return reader == 'graph'
    except:
        return False

def readGraphData(parameters, variable):
    '''
    Reads the variable.

    Input:
        parameters  configParser parameters
        variable    CE variable to read
    Returns:
                    CE variable with an specified shape
    '''
    try:
        fieldType = parameters.get(variable, 'field_type')
        fileName = parameters.get(variable, 'input_files')
        field = parameters.get(variable, 'field')
        popType = parameters.get(variable, 'population_type')
        dims = parameters.getint(variable, 'dimensions')
        assert 2 <= dims <= 4, 'ERROR: Number of dimensions ' + dims + ' for variable ' + variable + ' is incorrect. It should be 2, 3, or 4.'
        assert popType == 'statistical' or popType == 'spatial', 'ERROR: Population type ' + popType + ' for variable ' + variable + ' incorrect.'
        assert fieldType == 'edge' or fieldType == 'node', 'ERROR: Field type ' + fieldType + ' for field ' + field + ' incorrect.'

        if dims == 2:
            if popType == 'spatial':
                assert fieldType == 'node', 'ERROR: Edge, ' + field + ', population cannot be spatial.'
                aux_init_data = readGraphFieldSpatial(fileName, field)
            if popType == 'statistical':
                assert fileName.count('[P]') == 1, 'ERROR: Statistical population for variable ' + variable + ' must have "[P]" wildcard.'
                try:
                    stat_from = eval(parameters.get(variable, 'stat_from'))
                    stat_to = eval(parameters.get(variable, 'stat_to'))
                    stat_step = 1
                    if parameters.has_option(variable, 'stat_step'):
                        stat_step = eval(parameters.get(variable, 'stat_step'))
                    initial = True
                    i = 0
                    for index in np.arange(stat_from, stat_to + stat_step, stat_step):
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
                assert fieldType == 'node', 'ERROR: Edge, ' + field + ', population cannot be spatial.'
                assert fileName.count('[T]') == 1, 'ERROR: Spatial population for variable ' + variable + ' must have "[T]" wildcard.'
                aux_init_data = []
                try:
                    time_from = eval(parameters.get(variable, 'time_from'))
                    time_to = eval(parameters.get(variable, 'time_to'))
                    time_step = 1
                    if parameters.has_option(variable, 'time_step'):
                        time_step = eval(parameters.get(variable, 'time_step'))
                    initial = True
                    i = 0
                    for index in np.arange(time_from, time_to + time_step, time_step):
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
                assert fileName.count('[P]') == 1, 'ERROR: Statistical population for variable ' + variable + ' must have "[P]" wildcard.'
                assert fileName.count('[T]') == 1, 'ERROR: Statistical population for variable ' + variable + ' must have "[T]" wildcard.'    
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
                    for index_t in np.arange(time_from, time_to + time_step, time_step):
                        j = 0
                        for index_s in np.arange(stat_from, stat_to + stat_step, stat_step):
                            fName = fileName.replace('[P]', str(index_s)).replace('[T]', str(index_t))
                            print fName
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
                assert fieldType == 'node', 'ERROR: Edge, ' + field + ', population cannot be spatial.'
                assert fileName.count('[T]') == 1, 'ERROR: Spatial population for variable ' + variable + ' must have "[T]" wildcard.'
                assert fileName.count('[G]') == 1, 'ERROR: Spatial population for variable ' + variable + ' must have "[G]" wildcard.'
                aux_init_data = []
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
                    for index_g in np.arange(group_from, group_to + group_step, group_step):
                        j = 0
                        for index_t in np.arange(time_from, time_to + time_step, time_step):
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
                assert fileName.count('[P]') == 1, 'ERROR: Statistical population for variable ' + variable + ' must have "[P]" wildcard.'
                assert fileName.count('[T]') == 1, 'ERROR: Statistical population for variable ' + variable + ' must have "[T]" wildcard.'
                assert fileName.count('[G]') == 1, 'ERROR: Statistical population for variable ' + variable + ' must have "[G]" wildcard.'
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
                    for index_g in np.arange(group_from, group_to + group_step, group_step):
                        j = 0
                        for index_t in np.arange(time_from, time_to + time_step, time_step):
                            k = 0
                            for index_s in np.arange(stat_from, stat_to + stat_step, stat_step):
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
    '''
    Reads a field from the file.

    Input:
        folder      data folder name
        field       field to read
        fieldType   the field type
    Returns:
                    the field of each node
    '''
    Gtmp = pgv.AGraph(fileName)
    if fieldType == 'edge':
        tmp = np.ndarray(Gtmp.number_of_edges(), dtype='float')
        indexE = 0
        for e in Gtmp.edges_iter():
            tmp[indexE] = e.attr[field]
            indexE = indexE + 1
    elif fieldType == 'node':
        tmp = np.ndarray(Gtmp.number_of_nodes(), dtype='float')
        for n in Gtmp.nodes_iter():
            tmp[int(n[1:])] = n.attr[field]
    Gtmp.close()
    return tmp

def readGraphFieldSpatial(fileName, field):
    '''
    Reads a field from the file spatially.
    The neighbours field values of a node N are stored in a list.

    Input:
        fileName    data file name
        field       field to read
    Returns:
                    list of values of every node
    '''
    Gtmp = pgv.AGraph(fileName)
    tmp = [None] * Gtmp.number_of_nodes()
    for v in Gtmp.nodes_iter():
        pop = np.ndarray(Gtmp.degree(v), dtype='float')
        index = 0
        for vn in Gtmp.iterneighbors(v):
            pop[index] = vn.attr[field]
            index = index + 1
        tmp[int(v[1:])] = pop
    Gtmp.close()
    return tmp
    
