#!/usr/bin/python
'''
Information Dissipation Time (IDT) metrics.
'''

import numpy as np
import random
import numpy as np
import sys, getopt
import os, os.path
sys.path.append(os.getcwd() + '/metrics')
import entropy_shannon as shannon
import PDF as PDF
import MI as MI
import time
import deft as deft

def system(initial, times, epsilon, dt, bin_values, continuous_bins, logbase="log2"):
    '''
    IDT system metric

    Input:
        initial         Initial data NxP
                            N = elements
                            P = population
        times           Time state data TxNxP
                            T = time series 
                            N = elements
                            P = population
        epsilon         epsilon parameter
        dt              Number of timesteps between time series
        bin_values      values of the bins
        continuous_bins true if the values of the bins are continuous
        logbase         Base for the logarithm ("log2", "log", "log10")
    Returns:
                        IDT N
                            N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"

    numTime = len(times)
    numElems = len(times[0])

    #Initial entropy
    h_initial = shannon.calculate(PDF.single(initial, bin_values, continuous_bins), logbase)

    #Temporal entropy
    h_t = np.ndarray((numTime, numElems),dtype='float')
    for t in xrange(numTime):
        h_t[t] = shannon.calculate(PDF.single(times[t], bin_values, continuous_bins), logbase)

    IDT_var = np.ndarray(numElems,dtype='float')
    for i in xrange(numElems):
        h_target = h_initial[i]

        if h_target - epsilon > 0:
            h_target = h_target - epsilon

        found = False
        for t in xrange(numTime):
            if h_target - h_t[t, i] < 0:
                t1 = t - 1
                t2 = t
                found = True
                break

        if found:
            if t1 < 0:
                h1 = 0
            else:
                h1 = h_t[t1, i]
            h2 = h_t[t2, i]
            x1 = t1 + 1
            x2 = t2 + 1
            if h2 - h1 == 0:
                IDT_var[i] = 0
            else:
                IDT_var[i] = (x1 + (x2-x1)*(h_target - h1) /(h2-h1)) * dt
        else:
            IDT_var[i] = numTime * dt

    return IDT_var

'''IDT metric

Input:
    initial            Initial state data NxP
                    N = elements
                    P = population
    times            Time state data TxNxP
                    T = time series 
                    N = elements
                    P = population
    dt            Number of timesteps between time series
    bin_values        values of the bins
    continuous_bins     true if the values of the bins are continuous
    sample_N1        percentage of elements to choose as a sample for state 0
    sample_N2        percentage of elements to choose as a sample for state t
    sample_time        percentage of elements to choose as a sample for time series
    logbase            Base for the logarithm ("log2", "log", "log10")

    returns            IDT N
                    N = elements

'''
def individual(initial, times, dt, bin_values, continuous_bins, sample_N1, sample_N2, sample_t, logbase="log2"):
    '''
    IDT individual metric

    Input:
        initial         Initial data NxP
                            N = elements
                            P = population
        times           Time state data TxNxP
                            T = time series 
                            N = elements
                            P = population
        dt              Number of timesteps between time series
        bin_values      values of the bins
        continuous_bins true if the values of the bins are continuous
        sample_N1       percentage of elements to choose as a sample for state 0
        sample_N2       percentage of elements to choose as a sample for state t
        sample_time     percentage of elements to choose as a sample for time series
        logbase         Base for the logarithm ("log2", "log", "log10")
    Returns:
                        IDT N
                            N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    assert 0 < sample_N1 <= 1, "Sample for N1 must be within (0, 1]"
    assert 0 < sample_N2 <= 1, "Sample for N2 must be within (0, 1]"
    assert 0 < sample_time <= 1, "Sample for time must be within (0, 1]"

    number_of_bins = len(bin_values)
    if continuous_bins:
        number_of_bins = number_of_bins - 1
    #Sampling input data
    sample_elements_1 = np.arange(len(initial))
    sample_elements_2 = np.arange(len(initial))
    sample_time = np.arange(len(times))
    np.random.shuffle(sample_elements_1)
    np.random.shuffle(sample_elements_2)
    np.random.shuffle(sample_time)
    sample_elements_1 = sample_elements_1[:len(initial)*sample_N1]
    sample_elements_2 = sample_elements_2[:len(initial)*sample_N2]
    sample_time = sample_time[:len(times)*sample_t]
    sample_time = np.sort(sample_time)
    times_sampled = times[sample_time]
    initial_sampled = initial[sample_elements_1]
    initial_sampled_2 = initial[sample_elements_2]
    initial_sampled_len = len(initial_sampled)
    initial_sampled_len_2 = len(initial_sampled_2)
    times_sampled_len = len(times_sampled)

    #Maximum value for IDT when there is no enough decay
    IDT_max = len(times) * dt
    
    #Initial marginals pdf
    pdf_initial = PDF.single(initial_sampled, bin_values, continuous_bins)
    pdf_initial_2 = PDF.single(initial_sampled_2, bin_values, continuous_bins)
    #Initial entropy
    h_initial = shannon.calculate(pdf_initial, logbase)
    #Temporal marginals pdf
    pdf_t = np.ndarray((len(sample_time), len(sample_elements_2), number_of_bins),dtype='float')
    for t in xrange(len(sample_time)):
        pdf_t[t] = PDF.single(times_sampled[t][sample_elements_2, ...], bin_values, continuous_bins)

    #Calculate IDT for each element (sample)
    IDT_var = np.ndarray(initial_sampled_len,dtype='float')
    init = time.clock()
    for i in xrange(initial_sampled_len):
        #Target decay limit
        h_target = h_initial[i]/2

        #Maximum mutual information 
        max_I = np.ndarray(times_sampled_len + 1,dtype='float')
        initial_sampled_i_len = len(initial_sampled[i])

        found = False
        #Initial mutual information
        mi_init = np.ndarray((len(times_sampled[t][sample_elements_2])),dtype='float')
        for j in xrange(len(times_sampled[t][sample_elements_2])):
            initial_sampled_i_len_2 = len(initial_sampled_2[j])
            #Calculate joint pdf from initial state
            pdf_joint = PDF.joint(initial_sampled[i].reshape(1, initial_sampled_i_len), bin_values, continuous_bins, initial_sampled_2[j].reshape(1, initial_sampled_i_len_2), bin_values, continuous_bins)
            #Mutual information
            mi_init[j] = MI.calculate(pdf_initial[i].reshape(1, number_of_bins), pdf_initial_2[j].reshape(1, number_of_bins), pdf_joint, logbase)
        max_I[0] = np.amax(mi_init)

        #Time series mutual information
        for t in xrange(times_sampled_len):
            mi = np.ndarray((len(times_sampled[t][sample_elements_2])),dtype='float')
            #Mutual information in time t
            for j in xrange(len(times_sampled[t][sample_elements_2])):
                #Calculate joint pdf from initial state and time t
                pdf_joint = PDF.joint(initial_sampled[i].reshape(1, initial_sampled_i_len), bin_values, continuous_bins, times_sampled[t][sample_elements_2][j].reshape(1, len(times_sampled[t][sample_elements_2][j])), bin_values, continuous_bins)
                #Mutual information
                mi[j] = MI.calculate(pdf_initial[i].reshape(1, number_of_bins), pdf_t[t, j, :].reshape(1, number_of_bins), pdf_joint, logbase)
            max_I[t + 1] = np.amax(mi)

        #Find t crossing target decay
        for t in xrange(times_sampled_len):
            #Interpolate when found
            if max_I[t + 1] - h_target < 0:
                t1 = t
                t2 = t + 1
                found = True
                h1 = max_I[t1]
                h2 = max_I[t2]

                if h2 - h1 == 0:
                    IDT_var[i] = 0
                else:
                    IDT_var[i] = (t1 + (t2-t1)*(h_target - h1) /(h2-h1)) * dt
                break
        #Setting maximum IDT value when not found
        if not found:
            IDT_var[i] = IDT_max
    
    return IDT_var



