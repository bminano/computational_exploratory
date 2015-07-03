#!/usr/bin/python

import numpy as np

def calculate(pdf_p, pdf_q, variable_p, variable_q):
    """
    Input:
        pdf_p       joint pdf class P
        pdf_q       joint pdf class Q
        variable_p  the variable P to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        variable_q  the variable Q to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)

    returns     variable entropy
    """

    labels_p = pdf_p.get_labels(variable_p)
    labels_q = pdf_q.get_labels(variable_q)

    assert len(labels_p) == len(labels_q), "There have to be the same number of variables for P " + labels_p + " and Q" + labels_q

    hellinger = np.ndarray((len(labels_p)))
    for i in xrange(len(labels_p)):
        marginals_p = pdf_p.shrink_dimensions_to([labels_p[i]]).joint_probabilities
        marginals_q = pdf_q.shrink_dimensions_to([labels_p[i]]).joint_probabilities
        assert len(marginals_p) == len(marginals_q), "Number of bins for variables for P and Q must be the same"
        hellinger[i] = 1.0/np.sqrt(2) * np.sqrt(np.sum(np.power(np.sqrt(marginals_p) - np.sqrt(marginals_q), 2)))

    return hellinger
