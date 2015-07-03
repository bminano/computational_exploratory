#!/usr/bin/python

import numpy as np
import random
import MI

def calculate(pdf, variable_time, variables_state, dt, sample_N=1, sample_T=1, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variable_time           variable identifying the time series (time 0 must be included). 
                                Must be ordered, since the first index is used to calculate the entropy used to intersect the entropy curve.
        variables_state         variables representing the state. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        dt                      Number of timesteps between time series
        sample_N                sample percentage for the variables
        sample_T                sample percentage for the time variable
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 information integration.
    """
    assert np.isscalar(variable_time), "Only one time variable can be specified"
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"

    """Sample variables"""
    labels_state = pdf.get_labels(variables_state)
    sampled_pdf = pdf.sample_variables(labels_state, sample_N)
    sampled_labels_state = sampled_pdf.get_labels(variables_state)
    """Sample time"""
    sampled_pdf = sampled_pdf.sample_values([variable_time], [sample_T])
    num_time_series = sampled_pdf.get_num_bins_of(variable_time)

    """Calculate IDT in each element (sample)"""
    II = np.ndarray((num_time_series, len(sampled_labels_state)))
    for i, l_i in enumerate(sampled_labels_state):
        for t in xrange(num_time_series):
            """Calculate I(Si^T:{Sj^0}j)"""
            """Create joint pdf class with the initial state as a variable"""
            state_vars = sampled_labels_state[:]
            state_vars.remove(l_i)
            joint_i_sj_pdf = sampled_pdf.join_dimensions(state_vars, "initial_state")
            MI_i = MI.calculate(joint_i_sj_pdf, l_i, "initial_state", logbase)

            """I(Si^T:Sj^0) accumulator"""
            MI_i_tAcc = 0
            for j, l_j in enumerate(sampled_labels_state):
                MI_i_tAcc += MI.calculate(sampled_pdf, l_i, l_j, logbase)

            II[t, i] = MI_i - MI_i_tAcc

    return II

