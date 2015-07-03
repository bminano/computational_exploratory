"""
Script executing the integrated metric tool of the Computational Exploratory.
"""

import sys, getopt
import os, os.path
sys.path.append('./metrics')
sys.path.append('./tools')
import numpy as np
import ConfigParser
import StringIO
import h5py
import re
import itertools
from multiprocessing import Pool, Manager
import pygraphviz as pgv
#tools
import graph_tools as gt
import mesh_tools as mt
import meshless_tools as pt
import ce_data_tools as ce
#metrics
import PDF as PDF
import MI as MI
import entropy_shannon as shannon
import kullback_leibler_divergence as kullback
import surprise as surprise
import IDT as IDT
import MultiInfo as multi
import reductions as red
import Information_integration as II
import hellinger_distance as hellinger
import deft
import fisher as fis
import Early_warning as ew

import time

def getTyped(s):
    '''
    Gets the type of the variable

    Input:
        s       variable
    Returns:
                type
    '''
    if s.count('.') > 0:
            return float(s)
    else:
            return int(s)

def isNum(s):
    '''
    Checks if the variable is a number

    Input:
        s       variable
    Returns:
                true if number
    '''
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
    '''
    Checks if the variable is a string

    Input:
        s       variable
    Returns:
                true if string
    '''
    if re.match(r'"[^"]+"', s) != None:
        return True
    return False

def isList (s):
    '''
    Checks if the variable is a list

    Input:
        s       variable
    Returns:
                true if list
    '''
    lista = re.split(r' (?=(?:[^\[]*\[[^\[]*\])*[^\]]*$)', s)
    return len(lista) > 1

def createList(s):
    '''
    Creates a list from the values of a variable

    Input:
        s       variable
    Returns:
                list
    '''
    listRange = []
    for elem in s.split():
        listRange.append(getTyped(elem))
    return listRange

def checkArray(data):
    '''
    Checks if the data is an array type and fixes when the dimensions are not the same length.

    Input:
        data    data to check
    Returns:
                data fixed if is an array with different dimensions in its content.
    '''
    if data.dtype == 'object':
        maxIndex = 0
        for index, val in np.ndenumerate(data):
            if len(data[index]) > maxIndex:
                maxIndex = len(data[index])
        temporal = np.ndarray(shape=(data.shape + (maxIndex,)))
        for index, val in np.ndenumerate(data):
            tmp = np.resize(np.array(data[index]), maxIndex)
            tmp[len(data[index]):] = np.nan
            temporal[index] = tmp
        return temporal
    else:
        return data


def readData(parameters, variable):
    '''
    Reads data from CE variable

    Input:
        parameters  configParser parameters
        variable    CE variable to read
    Returns:
                data
    '''
    #Graph field
    if (gt.isGraph(parameters, variable)):
        return gt.readGraphData(parameters, variable)
    elif (mt.isMesh(parameters, variable)):
        return mt.readMeshData(parameters, variable)
    elif (pt.isMeshless(parameters, variable)):
        return pt.readMeshlessData(parameters, variable)
    elif (ce.isCEData(parameters, variable)):
        return ce.readCEData(parameters, variable)
    else:
        print 'ERROR: Input data origin not recognized/supported. Variable: ', variable, '.'
        raise Exception()

def readmetricParameters(metric_parameters, metric_name, time, global_variable_dic):
    '''
    Reads parameters used in a metric.

    Input:
        metric_parameters   string with the parameters
        metric_name         the metric
        time                when the metric uses temporal parameters, this is the time index
        global_variable_dic variable dictionary
    Returns:
                            parameter values
    '''
    param_vals = []
    if metric_parameters != '':
        try:
            for par in re.split(r',(?=(?:[^\[\]]*\[[^\[\]]*\])*[^\[\]]*$)', metric_parameters):
                par = par.strip()
                #numerical constant
                if isNum(par):
                    param_vals.append(getTyped(par))
                #boolean constant
                elif par.lower() == 'true' or par.lower() == 'false':
                    if par.lower() == 'true':
                        param_vals.append(True)
                    else:
                        param_vals.append(False)
                #String
                elif isString(par):
                    param_vals.append(par[1:len(par)-1])
                #numerical list
                elif isList(par):
                    param_vals.append(createList(par))
                #variable slice
                elif par.count('['):
                    #variable slice temporal
                    if par.count('{'):
                        par = par[1:len(par) - 1]
                        slices = re.findall(r'\[.*\]', par)
                        if len(global_variable_dic[par[:par.index('[')]].shape) != 3:
                            print 'ERROR: {Variables} must come from statistical_temporal variables or derivatives. Location: ', metric_name, '. Variable: ', par, '.'
                            raise Exception()
                        tmp = eval("global_variable_dic[par[:par.index('[')]][" + str(time) + "]" + slices[0])
                        param_vals.append(tmp)
                    else:
                        slices = re.findall(r'\[.*\]', par)
                        tmp = eval("global_variable_dic[par[:par.index('[')]]" + slices[0])
                        param_vals.append(tmp)
                #variable
                else:
                    try:
                        if par.count('{'):
                            par = par[1:len(par) - 1]
                            if len(global_variable_dic[par].shape) != 3:
                                print 'ERROR: {Variables} must come from statistical_temporal variables or derivatives. Location: ', metric_name, '. Variable: ', par, '.'
                                raise Exception()
                            param_vals.append(global_variable_dic[par][time, ...])
                        else:
                            param_vals.append(global_variable_dic[par])
                    except KeyError:
                        print 'ERROR: Error in ', metric_name, '. Variable ', par, ' does not exist.'
                        raise Exception()        
        except:
            print 'ERROR: Error in ', metric_name, ', parameter ' + par + ' is not correct.'
            raise Exception()
    return param_vals

def getTime(metric_parameters, global_variable_dic):
    '''
    Reads temporal parameters from a metric.

    Input:
        metric_parameters   string with the parameters
        global_variable_dic variable dictionary
    Returns:
                            time slices
    '''
    for par in re.split(r',(?=(?:[^\[]*\[[^\[]*\])*[^\]]*$)', metric_parameters):
        par = par.strip()
        if par.count('{'):
            par = par[1:par.index('}')]
            if par.count('['):
                par = par[:par.index('[')]
            return global_variable_dic[par].shape[0]        

def calculateMetric(metric_name, param_vals):
    '''
    Calculates a metric.

    Input:
        metric_name     metric name
        param_vals      metric parameters
    Returns:
                        result of the metric
    '''
    if metric_name == 'count':
        if len(param_vals)!= 1:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be count(data)'
            raise Exception()
        return red.count(*param_vals)
    elif metric_name == 'pdf':
        if len(param_vals)!= 3:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be pdf(data, bin_values, continuous_bins)'
            raise Exception()
        return PDF.single(*param_vals)
    elif metric_name == 'deft':
        if len(param_vals) < 4 or len(param_vals) > 5:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be deft(data, g, minLimit, maxLimit, alpha=2)'
            raise Exception()
        return deft.deft(*param_vals)
    elif metric_name == 'deft_joint':
        if len(param_vals) < 7 or len(param_vals) > 8:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be deft_joint(dataA, dataB, g, minLimitA, maxLimitA, minLimitB, maxLimitB, alpha=2)'
            raise Exception()
        return deft.deft(*param_vals)
    elif metric_name == 'pdf_joint':
        if len(param_vals)!= 6:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be pdf_joint(dataA, bin_valuesA, continuous_binsA, dataB, bin_valuesB, continuous_binsB)'
            raise Exception()
        return PDF.joint(*param_vals)
    elif metric_name == 'mutual_information':
        if len(param_vals) < 3 or len(param_vals) > 4:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be mutual_information(pdfA, pdfB, joint_pdf, logbase="log2")'
            raise Exception()
        return MI.calculate(*param_vals)
    elif metric_name == 'shannon':
        if len(param_vals) < 1 or len(param_vals) > 2:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be shannon(pdf, logbase="log2")'
            raise Exception()
        return shannon.calculate(*param_vals)
    elif metric_name == 'kullback-leibler':
        if len(param_vals) < 2 or len(param_vals) > 3:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be kullback-leibler(pdf_p, pdf_q, logbase="log2")'
            raise Exception()
        return kullback.calculate(*param_vals)
    elif metric_name == 'fisher':
        if len(param_vals) < 2 or len(param_vals) > 3:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be fisher(pdf, eps, logbase="log2")'
            raise Exception()
        return fis.calculate(*param_vals)
    elif metric_name == 'hellinger-distance':
        if len(param_vals) != 2:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be hellinger-distance(pdf_p, pdf_q)'
            raise Exception()
        return hellinger.calculate(*param_vals)
    elif metric_name == 'surprise':
        if len(param_vals)!= 1:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be surprise(prob)'
            raise Exception()
        return surprise.calculate(*param_vals)
    elif metric_name == 'idt':
        if len(param_vals) < 6 or len(param_vals) > 7:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be idt(initial, time_series, epsilon, dt, bin_values, continuous_bins, logbase="log2")'
            raise Exception()
        return IDT.system(*param_vals)
    elif metric_name == 'idt_individual':
        if len(param_vals) < 8 or len(param_vals) > 9:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be idt_individual(initial, time_series, dt, bin_values, continuous_bins, sample_state_0, sample_state_t, sample_time, logbase="log2")'
            raise Exception()
        return IDT.individual(*param_vals)
    elif metric_name == 'information_integration':
        if len(param_vals) < 9 or len(param_vals) > 10:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be information_integration(initial, group, dt, bin_values, continuous_bins, sample_N1, sample_N2, sample_G, sample_t, logbase="log2")'
            raise Exception()
        return II.calculate(*param_vals)
    elif metric_name == 'multi_information':
        if len(param_vals) < 6 or len(param_vals) > 7:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be multi_information(data, bin_values, continuous_bins, sample_var, sample_elems, sample_pop, logbase="log2")'
            raise Exception()
        return multi.calculate(*param_vals)
    elif metric_name == 'early_warning_difference':
        if len(param_vals) < 4 or len(param_vals) > 5:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be early_warning_difference(time_series_ref, time_series_comp, change_values, warning_values, histogram_limit=50)'
            raise Exception()
        return ew.early_warning_difference(*param_vals)
    elif metric_name == 'early_warning_flips':
        if len(param_vals) != 2:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be early_warning_flips(time_series, change_values)'
            raise Exception()
        return ew.early_warning_flips(*param_vals)
    elif metric_name == 'add_dimension':
        if len(param_vals)!= 2:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be add_dimension(data, dimNumber)'
            raise Exception()
        return  np.expand_dims(*param_vals)
    elif metric_name == 'join_dimensions':
        if len(param_vals)!= 3:
            print 'ERROR:Error in ', metric_name, ', number of parameters incorrect. It must be join_dimensions(data, dimNumberA, dimNumberB)'
            raise Exception()
        return  red.join(*param_vals)
    else :
        # Try to get a numpy function
        try :
            func = getattr(np, metric_name)
            return func(*param_vals)
        except:
            print 'ERROR:Metric ', metric_name, ' does not exist'
            raise Exception()

def processSimpleWorkflow(parameters):
    '''
    Performs an uniprocessor execution.

    Input:
        parameters     parameter file for this execution
    '''
    try:
        global_variable_dic = {}

        #Read data
        for data in parameters.sections():
            if data != 'Metrics' and data != 'Parallel' and data != 'Config':
                start = time.clock()
                global_variable_dic[data] = readData(parameters, data)
                end = time.clock()
        #Output file
        if (parameters.has_section('Config')):
            outputFile = parameters.get('Config' , "output_fileName")
        else:
            outputFile = "output.h5"
        
        results = {}
        #Metrics
        for metrics_par in parameters.options('Metrics'):
            try:
                str_aux = parameters.get('Metrics' , metrics_par)
                metric_loop = str_aux.count('{') > 0
                start = time.clock()
                #It is a metric
                if str_aux.count('('):
                    metric_name = str_aux[:str_aux.index('(')]
                    metric_parameters = str_aux[str_aux.index('(') + 1:str_aux.index(')')]
                    if metric_loop:
                        #Get parameters for the metric
                        time2 = getTime(metric_parameters, global_variable_dic)
                        first = True
                        for t in xrange(time2):
                            param_vals = readmetricParameters(metric_parameters, str_aux, t, global_variable_dic)
                            if first:
                                tmp = calculateMetric(metric_name, param_vals)
                                axislen = len(tmp.shape)
                                tmp = np.expand_dims(tmp, axis=0)
                                first = False
                            else:
                                result = calculateMetric(metric_name, param_vals)
                                result = np.expand_dims(result, axis=0)
                                tmp = np.append(tmp, result, axis=0)
                        
                        global_variable_dic[metrics_par] = tmp
                    else:
                        #Get parameters for the metric
                        param_vals = readmetricParameters(metric_parameters, str_aux, 0, global_variable_dic)
                        #Call the metric and save results
                        global_variable_dic[metrics_par] = calculateMetric(metric_name, param_vals)
                #It is a field
                else:
                    if str_aux.count('['):
                        metric_name = str_aux[:str_aux.index('[')]
                    else:
                        metric_name = str_aux
                    if parameters.has_section(metric_name):
                        if str_aux.count('['):
                            slices = re.findall(r'\[.*\]', str_aux)
                            global_variable_dic[metrics_par] = checkArray(np.array(eval("global_variable_dic[metric_name]" + slices[0])))
                        else:
                            global_variable_dic[metrics_par] = checkArray(np.array(global_variable_dic[metric_name]))
                    else:
                        print 'ERROR: Metric ', str_aux, ' does not exist'
                        raise Exception()
                end = time.clock()
                print "Metric", metrics_par, (end - start)
        
                results[metrics_par] = global_variable_dic[metrics_par][:]
            except Exception,e:
                print 'ERROR: Metric ', str_aux, ' failed:' + str(e)
                raise Exception()

        #Write output file
        try:
            hdf = h5py.File(outputFile, mode='a')
            for metrics_par in parameters.options('Metrics'):
                #Delete existing keys with the same name 
                if metrics_par in hdf.keys():
                    del hdf[metrics_par]
                dset = hdf.require_dataset(metrics_par, results[metrics_par].shape, dtype='f')
                dset[:] = results[metrics_par][:]
            hdf.close()
        except Exception,e:
            print 'ERROR: Problem writing results failed:' + str(e)
            raise Exception()
    except KeyboardInterrupt:
        return


def parallelizeParameters(paramFile, original):
    '''
    When a parallel execution is required, this method creates all the parameter input file for the single executions.

    Input:
        paramFile   parameter file content
        original    original parameter file name
    Returns:
                    Array of parameters input
    '''
    parameters = []
    if (paramFile.has_section('Parallel')):
        #Open the original parameter file
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
                    #Include last step
                    lists.append(np.arange(init, end + step, step))
                #Parse list
                else:
                    values = value.split(' ')
                    lists.append(values)
                replacements.append('#' + metrics_par)
        #Generate all combinations
        combinations = list(itertools.product(*lists))
        for comb in combinations:
            newParams = pFile
            for rep in xrange(len(replacements)):
                newParams = newParams.replace(replacements[rep], str(comb[rep]))
            newParParser = ConfigParser.RawConfigParser()
            newParParser.optionxform=str
            newParParser.readfp(StringIO.StringIO(newParams))
            parameters.append(newParParser)

    else:
        parameters.append(paramFile)
    return parameters

def main(argv):
    '''
    Main function. Reads the parameters and create the pool for the parallel processes.

    Input:
        argv    standard arguments
    '''
    start_g = time.clock()
    #Script usage
    try:
        opts, args = getopt.getopt(argv,"hp:",["help", "parameter-file="])
    except getopt.GetoptError:
        print 'USAGE: python workflow_graph.py -p <parameter-file>'
        raise Exception()
    for opt, arg in opts:
        if opt == '-h':
                print 'USAGE: python workflow_graph.py -p <parameter-file>'
                sys.exit()
        elif opt in ("-p", "--parameter-file"):
                paramFile = arg

    #Read parameter file
    parameters = ConfigParser.RawConfigParser()
    parameters.optionxform=str
    try:
        read = parameters.read(paramFile)
        if len(read) == 0:
            print 'ERROR: The parameter file not found'
            raise Exception()
    except:
        print 'ERROR: The parameter file is not correct'
        raise Exception()

    procs = 1
    if (parameters.has_section('Parallel') and parameters.has_option('Parallel', 'nprocs')):
        procs = parameters.getint('Parallel' , 'nprocs')

    #Parallel processing
    processSimpleWorkflow(parameters)
    '''    pool = Pool(processes=procs)
        try:
            pool.map_async(processSimpleWorkflow, parallelizeParameters(parameters, paramFile))
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            print "Caught KeyboardInterrupt, terminating workers"
            pool.terminate()
            pool.join()

        end_g = time.clock()
        print "Total", (end_g - start_g)
    '''
if __name__ == "__main__":
    # making  global dic managed by multiprocessing
    manager = Manager()
    main(sys.argv[1:])
