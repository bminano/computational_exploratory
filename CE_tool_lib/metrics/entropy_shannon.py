#!/usr/bin/python

import numpy as np


def calculate(pdf, variable=None, logbase="log2"):
    """
    Input:
        pdf         joint pdf class
        variable    the variable to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        logbase     Base for the logarithm ("log2", "log", "log10")

    returns     variable entropy
    """
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"

    """Get log proper function"""
    log = getattr(np, logbase)

    np.seterr(all="ignore")

    if variable == None:
        marginals = pdf.joint_probabilities
        logs = log(marginals) * marginals
        logs[np.isnan(logs)] = 0.0
        return -np.sum(logs) 


    labels = pdf.get_labels(variable)
    shannon = np.ndarray((len(labels)))
    """Obtain all the labels of the variable"""
    for i, l in enumerate(labels):
        """To obtain the marginals, shrink to the variable"""
        marginals_pdf = pdf.shrink_dimensions_to([l])
        marginals = marginals_pdf.joint_probabilities
        logs = log(marginals) * marginals
        norm = log(marginals_pdf.get_num_bins()[0])
        logs[np.isnan(logs)] = 0.0
        shannon[i] = -np.sum(logs)/norm
    np.seterr(all="warn")
    return shannon


def conditional(pdf, variable, conditional_variable, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variable                the variable to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        conditional_variable    conditional variable
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 conditional shannon entropy
    """
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"

    """Get log proper function"""
    log = getattr(np, logbase)

    np.seterr(all="ignore")
    labels = pdf.get_labels(variable)
    shannon = np.ndarray((len(labels)))
    """Obtain all the labels of the variable"""
    for i, l in enumerate(labels):
        """To obtain the marginals, shrink to the variable"""
        marginals = pdf.shrink_dimensions_to([l]).joint_probabilities
        labels_cond = pdf.get_labels(conditional_variable)
        """Get conditional probabilities"""
        condPDF = pdf2.calculate_conditional_probabilities([labels_cond]).joint_probabilities
        conditional = condPDF.remove_dimensions([l]).joint_probabilities
        """Calculate entropy"""
        logs = log(conditional) * conditional
        logs[np.isnan(logs_cond)] = 0.0
        logs_condAcc = np.sum(logs)*pdf
        shannon[i] = -np.sum(logs_condAcc)
    np.seterr(all="warn")
    return shannon
