#!/usr/bin/python
import numpy as np

def calculate(pdf, variable, values):
    """
    Input:
        pdf         joint pdf class
        variable    the variable to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        values       the indices of the values to get surprise

    returns         surprise of the specified values
    """

    np.seterr(all="ignore")

    if np.isscalar(values):
        values = [values] 

    labels = pdf.get_labels(variable)
    surprise = np.ndarray((len(labels), len(values)))
    """Obtain all the labels of the variable"""
    for i, l in enumerate(labels):
        marginals = pdf.shrink_dimensions_to([l])
        vals = marginals.shrink_values_to([l], [values]).joint_probabilities
        inverse = 1.0/vals
        s = np.log2(inverse)
        s[np.isnan(s)] = 0.0
        s[np.isinf(s)] = 0.0
        surprise[i, :] = s
    np.seterr(all="warn")
    return surprise
