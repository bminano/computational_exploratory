#!/usr/bin/python

import numpy as np
import entropy_shannon as shannon
import itertools

def calculate(pdf, variable_a, variable_b, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variable_a              variable a. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        variable_b              variable b. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 mutual information
    """
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    np.seterr(all="ignore")
    """Get log proper function"""
    log = getattr(np, logbase)

    labels_a = pdf.get_labels(variable_a)
    labels_b = pdf.get_labels(variable_b)

    assert len(labels_a) == len(labels_b), "There have to be the same number of variables for A " + str(labels_a) + " and B " + str(labels_b)

    """Combination of all labels"""
    label_combinations = [l for l in itertools.product(labels_a, labels_b)]

    """Calculation of MI"""
    mi = np.ndarray(shape=(len(label_combinations)))
    for i, labels in enumerate(label_combinations):
        if labels[0] != labels[1]:
            marginals_a = pdf.shrink_dimensions_to(labels[0]).joint_probabilities
            marginals_b = pdf.shrink_dimensions_to(labels[1]).joint_probabilities
            joint_pdf = pdf.shrink_dimensions_to(list(labels))
            joint_pdf.reorder_dimensions(labels)
            joint_pdf = joint_pdf.joint_probabilities
            logs = 0
            for nbA in xrange(marginals_a.shape[0]):
                for nbB in xrange(marginals_b.shape[0]):
                    if marginals_a[nbA] * marginals_b[nbB] > 0 and joint_pdf[nbA, nbB] > 0:
                        logs += joint_pdf[nbA, nbB] * log(joint_pdf[nbA, nbB]/(marginals_a[nbA] * marginals_b[nbB]))
            mi[i] = logs
        else:
            marginals = pdf.shrink_dimensions_to(labels[0]).joint_probabilities
            logs = marginals * log(1.0/marginals)
            logs[np.isnan(logs)] = 0.0
            logs[np.isinf(logs)] = 0.0
            mi[i] = np.sum(logs)

    np.seterr(all="warn")
    return mi


def entropies(pdf, variable, conditional_variable, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variable                the variable to calculate the entropy. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        conditional_variable    conditional variable
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 mutual information based on conditional entropy
    """

    return shannon.calculate(pdf, variable, logbase) - shannon.conditional(pdf, variable, conditional_variable, logbase)

