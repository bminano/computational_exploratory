#!/usr/bin/python

import numpy as np
import random
import entropy_shannon as shannon
import MI
import pdfClass

def system(pdf, variable_time, variables_idt, epsilon, dt, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variable_time           variable identifying the time series (time 0 must be included). 
                                Must be ordered, since the first index is used to calculate the entropy used to intersect the entropy curve.
        variables_idt           variables to calculate their idt. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        epsilon                 epsilon parameter
        dt                      Number of timesteps between time series
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 idt calculated on the variables_idt.
    """
    assert np.isscalar(variable_time), "Only one time variable can be specified"

    labels_idt = pdf.get_labels(variables_idt)
    num_time_series = pdf.get_num_bins_of(variable_time)
    num_vars = len(labels_idt)

    """Calculate entropies"""
    h_t = np.ndarray((num_time_series, num_vars))
    for t in xrange(num_time_series):
        """Obtain entropy at time t"""
        """Filtering time"""
        joint_time_t = pdf.filter_joint_probabilities([variable_time], [t])
        joint_time_t.normalize()
        h_t[t, :] = shannon.calculate(joint_time_t, variables_idt)

    """IDT calculation"""
    IDT_var = np.ndarray((num_vars))
    for i, l in enumerate(labels_idt):
        """Set target entropy"""
        h_target = h_t[0, i]
        if h_target - epsilon > 0:
            h_target = h_target - epsilon

        """Search intersection with entropy time curve"""
        found = False
        for t in xrange(1, num_time_series):
            if h_target - h_t[t, i] < 0:
                t1 = t - 1
                t2 = t
                found = True
                break

        """Interpolate value"""
        if found:
            h1 = h_t[t1, i]
            h2 = h_t[t2, i]
            x1 = t1 + 1
            x2 = t2 + 1
            if h2 - h1 == 0:
                IDT_var[i] = 0
            else:
                IDT_var[i] = (x1 + (x2-x1)*(h_target - h1) /(h2-h1)) * dt
        else:
            IDT_var[i] = num_time_series * dt

    return IDT_var

def individual(pdf, variable_time, variables_idt, dt, sample_N=1, sample_T=1, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variable_time           variable identifying the time series (time 0 must be included). 
                                Must be ordered, since the first index is used to calculate the entropy used to intersect the entropy curve.
        variables_idt           variables to calculate their idt. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        dt                      Number of timesteps between time series
        sample_N                sample percentage for the idt variables
        sample_T                sample percentage for the time variable
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 idt calculated on the variables_idt.
    """
    assert np.isscalar(variable_time), "Only one time variable can be specified"

    """Sample variables"""
    labels_idt = pdf.get_labels(variables_idt)
    sampled_pdf = pdf.sample_variables(labels_idt, sample_N)
    sampled_labels_idt = sampled_pdf.get_labels(variables_idt)

 #   labels_initial_idt = pdf_initial.get_labels(variables_idt)
 #   sampled_initial_pdf = pdf_initial.sample_variables(labels_initial_idt, sample_N)

    """Before sampling time, calculate entropy at time 0"""
    joint_time_0 = sampled_pdf.filter_joint_probabilities([variable_time], [0])
    joint_time_0.normalize()
    h_initial = shannon.calculate(joint_time_0, sampled_labels_idt)

    """Sample time"""
    sampled_pdf = sampled_pdf.sample_values([variable_time], [sample_T], True)
    num_time_series = sampled_pdf.get_num_bins_of(variable_time)

    """Maximum value for IDT when there is no enough decay"""
    IDT_max = num_time_series * dt

    num_variables = len(sampled_labels_idt)
    IDT_var = np.ndarray((num_variables))
    IDT_var[:] = IDT_max
    """Calculate IDT for each element"""
    for i, l_i in enumerate(sampled_labels_idt):
        """Target decay limit"""
        h_target = h_initial[i]/2

        """Maximum mutual information variable"""
        max_I = np.ndarray((num_time_series))

        """Time series mutual information"""
        for t in xrange(num_time_series - 1):
            """Filter combination with time t"""
            pdf_t = sampled_pdf.filter_joint_probabilities([variable_time], [[t+1]])
            pdf_t.normalize()
            mi = np.ndarray((num_variables))
            """Mutual information in time t"""
            for j, l_j in enumerate(sampled_labels_idt):
                """Joint pdf with var i from initial state and var j from time t"""
                """Mutual information"""
                if t == 0 and i == 0 and j == 1:
                    print joint_time_0.shrink_dimensions_to([l_i]).joint_probabilities, pdf_t.shrink_dimensions_to([l_j]).joint_probabilities
                mi[j] = MI.calculate(pdf_t, l_i, l_j, logbase)
            max_I[t] = np.amax(mi)
        print max_I[1]
        """Find t crossing target decay"""
        for t in xrange(num_time_series - 1):
            """Interpolate when found"""
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
    
    return IDT_var



