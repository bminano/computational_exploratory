#!/usr/bin/python
'''
Information integration metrics.
'''

import numpy as np
import random
import sys, getopt
import PDF as PDF
import MI as MI
import itertools
import math

def calculate(initial, group, dt, bin_values, continuous_bins, sample_N1, sample_N2, sample_G, sample_t, logbase="log2"):
    '''
    Information integration metric

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
        sample_G        percentage of elements to choose as a sample for groups
        sample_time     percentage of elements to choose as a sample for time series
        logbase         Base for the logarithm ("log2", "log", "log10")
    Returns:
                        Information integration TxN
                            T = time series (sampled)
                            N = elements (sampled)
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    assert 0 < sample_N1 <= 1, "Sample for N1 must be within (0, 1]"
    assert 0 < sample_N2 <= 1, "Sample for N2 must be within (0, 1]"
    assert 0 < sample_t <= 1, "Sample for time must be within (0, 1]"
    assert 0 < sample_G <= 1, "Sample for groups must be within (0, 1]"

    number_of_bins = len(bin_values)
    #Select samples
    sample_elements_1 = np.arange(group.shape[2])
    sample_elements_2 = np.arange(len(initial))
    sample_time = np.arange(group.shape[1])
    sample_group = np.arange(group.shape[0])
    np.random.shuffle(sample_elements_1)
    np.random.shuffle(sample_elements_2)
    np.random.shuffle(sample_time)
    np.random.shuffle(sample_group)
    sample_elements_1 = sample_elements_1[:group.shape[2]*sample_N1]
    sample_elements_2 = sample_elements_2[:len(initial)*sample_N2]
    sample_time = sample_time[:group.shape[1]*sample_t]
    sample_group = sample_group[:group.shape[0]*sample_G]
    sample_time = np.sort(sample_time)
    group_sampled = group[sample_group][:, sample_time,...][:, :, sample_elements_1,...]
    initial_sampled = initial[sample_elements_2,...]

    sample_time_len = len(sample_time)
    sample_elements_2_len = len(sample_elements_2)
    initial_sampled_len = len(initial_sampled[0])
    group_sampled_len = len(group_sampled[0])

    #Temporal pdf
    #Grouping experiments
    states_t = np.resize(group_sampled[0], (group_sampled.shape[1], group_sampled.shape[2], group_sampled.shape[3]))
    for g_i in xrange(group_sampled.shape[0] - 1):
        states_t = np.append(states_t, np.resize(group_sampled[g_i], (group_sampled.shape[1], group_sampled.shape[2], group_sampled.shape[3])), axis=2)
    pdf_t = np.ndarray((sample_time_len, group_sampled.shape[2], number_of_bins),dtype='float')
    for t in xrange(0, sample_time_len):
        pdf_t[t] = PDF.single(np.resize(states_t[t], (states_t.shape[1], states_t.shape[2])), bin_values, continuous_bins)
    #Initial states pdf
    pdf_initial = PDF.single(initial_sampled, bin_values, continuous_bins)

    #Calculate IDT in each element (sample)
    II_var = np.ndarray((sample_time_len, len(sample_elements_1)),dtype='float')
    for i in xrange(len(sample_elements_1)):
        print "loop i: ", i, " de ", len(sample_elements_1)
        #Calculate I(Si^T:{Sj^0}j)
        #Calculate joint probability p(Si^T, {Sj^0}j)
        comb_idx = 0
        population = initial_sampled_len
        pdf_init = np.zeros(shape=(initial_sampled_len),dtype='float')
        pdf_joint_init = np.zeros(shape=(sample_time_len, number_of_bins, initial_sampled_len),dtype='float')
        #Loop over all the initial states (one each group). It is supposed all possible combinations are available
        for state_initial_group_index in xrange(initial_sampled_len):
            initial_state = initial_sampled[:, state_initial_group_index]
            if np.array_equal(comp, initial_state):
                for group_index in xrange(group_sampled_len):
                    for t_index in xrange(sample_time_len):
                        for pop_T_index in xrange(group_sampled.shape[3]):
                            for nb in xrange(number_of_bins):
                                if continuous_bins:
                                    if group_sampled[group_index, t_index, i, pop_T_index] >= bin_values[nb] and group_sampled[group_index, t_index, i, pop_T_index] < bin_values[nb + 1]:
                                        pdf_joint_init[t_index, nb, comb_idx] = pdf_joint_init[t_index, nb, comb_idx] + 1
                                else:
                                    if group_sampled[group_index, t_index, i, pop_T_index] == bin_values[nb]:
                                        pdf_joint_init[t_index, nb, comb_idx] = pdf_joint_init[t_index, nb, comb_idx] + 1
                    #Initial state pdf
                    pdf_init[comb_idx] = pdf_init[comb_idx] + 1
            comb_idx = comb_idx + 1
        pdf_joint_init = np.divide(pdf_joint_init, population)
        pdf_init = np.divide(pdf_init, initial_sampled_len)
        MI_i_t = np.ndarray(sample_time_len,dtype='float')
        for t_index in xrange(sample_time_len):
            MI_i_t[t_index] = MI.calculate(pdf_t[t_index, i, :].reshape(1, number_of_bins), pdf_init.reshape(1, comb_len), pdf_joint_init[t_index].reshape(1, number_of_bins, comb_len), logbase)

        #Calculate all the I(Si^T:Sj^0)
        MI_i_tAcc = 0
        MI_i_tAcc = np.ndarray(sample_time_len,dtype='float')
        for t_index in xrange(sample_time_len):
            for j in xrange(sample_elements_2_len):
                initial_grouped_sample = np.zeros(shape=(group_sampled.shape[0]*group_sampled.shape[3]),dtype='int')
                for g_i in xrange(group_sampled.shape[0]):
                    for reps in xrange(group_sampled.shape[3]):
                        initial_grouped_sample[reps + g_i*group_sampled.shape[3]] = initial_sampled[j, g_i]
                pdf_joint = PDF.joint(np.resize(states_t[t, i], (1, states_t.shape[2])), bin_values, continuous_bins, initial_grouped_sample.reshape(1, group_sampled.shape[0]*group_sampled.shape[3]), bin_values, continuous_bins)

                tmp = MI.calculate(pdf_t[t_index, i, :].reshape(1, number_of_bins), pdf_initial[j].reshape(1, number_of_bins), pdf_joint.reshape(1, number_of_bins, number_of_bins), logbase)
                MI_i_tAcc[t_index] = MI_i_tAcc[t_index] + MI.calculate(pdf_t[t_index, i, :].reshape(1, number_of_bins), pdf_initial[j].reshape(1, number_of_bins), pdf_joint.reshape(1, number_of_bins, number_of_bins))
            II_var[t_index, i] = MI_i_t[t_index] - MI_i_tAcc[t_index]

    return II_var

