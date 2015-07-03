#!/usr/bin/python
'''
Multi-information metrics
'''

import numpy as np
import itertools
import random

def calculate(data, bin_values, continuous_bins, sample_var, sample_elems, sample_pop, logbase="log2"):
    '''
    Multi-information metric.

    Input:
        data            data variable VxNxP
                            V = variables
                            N = elements
                            P = population
        bin_values      values of the bins
        continuous_bins true if the values of the bins are continuous
        sample_var      percentage of variables to choose as a sample
        sample_elems    percentage of elements to choose as a sample
        logbase         base for the logarithm ("log2", "log", "log10")
    Returns:
                    multi-information N
                        N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    log = getattr(np, logbase)

    number_of_bins = len(bin_values)
    if continuous_bins:
        number_of_bins = number_of_bins - 1
    number_of_vars = int(data.shape[0]*sample_var)
    number_of_elements = int(data.shape[1]*sample_elems)


    #Select samples
    sampleVar = np.arange(data.shape[0])
    np.random.shuffle(sampleVar)
    sampleVar = sampleVar[:data.shape[0]*sample_var]
    sampleElem = np.arange(data.shape[1])
    np.random.shuffle(sampleElem)
    sampleElem = sampleElem[:data.shape[1]*sample_elems]

    #Generate all combinations
    states = [p for p in itertools.product(xrange(number_of_bins), repeat=number_of_vars)]

    multi = np.ndarray(shape=(number_of_elements),dtype='float')
    init = time.clock()
    for elem in xrange(number_of_elements):
        # Population could be different for each element, so sampling must be done here
        population = int(len(data[0][elem])*sample_pop)
        samplePop = np.arange(len(data[0][elem]))
        np.random.shuffle(samplePop)
        samplePop = samplePop[:data.shape[2]*sample_pop]
        acc = 0
        for comb in states:
            number_of_pop_joint = 0
            #Calculate probabilities
            prob = np.zeros(shape=(number_of_vars),dtype='float')
            for pop in xrange(population):
                joint = True
                for var in xrange(number_of_vars):
                    if continuous_bins:
                        if bin_values[comb[var] + 1] > data[sampleVar[var]][sampleElem[elem]][samplePop[pop]] >= bin_values[comb[var]]:
                            prob[var] = prob[var] + 1
                        else:
                            joint = False
                    else:
                        if data[sampleVar[var]][sampleElem[elem]][samplePop[pop]] == bin_values[comb[var]]:
                            prob[var] = prob[var] + 1
                        else:
                            joint = False
                if joint:
                    number_of_pop_joint = number_of_pop_joint + 1
            if population == 0:
                pdf_joint = 0
                prob = 0
            else:
                pdf_joint = float(number_of_pop_joint)/population
                prob = np.divide(prob, population)
            prod = np.prod(prob)
            if prod > 0 and pdf_joint > 0:
                acc = acc + pdf_joint * log(pdf_joint/prod)
        multi[elem] = acc

    #print "sqalida" ,multi.shape

    return multi

