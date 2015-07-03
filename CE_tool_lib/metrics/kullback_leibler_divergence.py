#!/usr/bin/python

import numpy as np

def calculate(pdf_p, pdf_q, variable_p, variable_q, logbase="log2"):
    """
    Input:
        pdf_p       joint pdf class P
        pdf_q       joint pdf class Q
        variable_p  the variable P to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        variable_q  the variable Q to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        logbase        Base for the logarithm ("log2", "log", "log10")

    returns         variable divergence
    """

    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"

    np.seterr(all="ignore")

    labels_p = pdf_p.get_labels(variable_p)
    labels_q = pdf_q.get_labels(variable_q)

    assert len(labels_p) == len(labels_q), "There have to be the same number of variables for P " + labels_p + " and Q" + labels_q

    """Get log proper function"""
    log = getattr(np, logbase)

    divergence = np.ndarray((len(labels_p)))
    for i in xrange(len(labels_p)):
        marginals_p = pdf_p.shrink_dimensions_to([labels_p[i]]).joint_probabilities
        marginals_q = pdf_q.shrink_dimensions_to([labels_p[i]]).joint_probabilities
        assert len(marginals_p) == len(marginals_q), "Number of bins for variables for P and Q must be the same"
        div = marginals_p/marginals_q
        logs = log(div) * marginals_p
        logs[np.isnan(logs)] = 0.0
        logs[np.isinf(logs)] = 0.0
        divergence[i] = np.sum(logs)

    np.seterr(all="warn")
    return divergence
