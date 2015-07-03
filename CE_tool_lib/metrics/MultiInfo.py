#!/usr/bin/python

import numpy as np

def calculate(pdf, variables, sample_variables=1, sample_values=1, logbase="log2"):
    """
    Input:
        pdf                     joint pdf class
        variables               variables for the multi-information. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...).
        sample_variables        sample percentage for the variables
        sample_values           sample percentage for the values
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 multi-information.
    """
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"

    labels = pdf.get_labels(variables)

    assert len(labels) > 1, "At least two variables must be specified to calculate multi-information"

    np.seterr(all="ignore")
    """Get log proper function"""
    log = getattr(np, logbase)

    """Sampling data"""
    sampled_pdf = pdf.sample_variables(labels, sample_variables)
    sampled_labels = sampled_pdf.get_labels(labels)
    sample_values = [sample_values] * len(sampled_labels)
    sampled_pdf = sampled_pdf.sample_values(labels, sample_values)
    num_values = sampled_pdf.get_num_bins_of(labels[0])

    """Calculation of MultiInformation"""
    mi = 0
    """Get all possible combinations of values for the dimensions"""
    value_combinations = [range(num_values) for variable in xrange(len(sampled_labels))]
    for i, value_combination in enumerate(value_combinations):
        """Marginals product"""
        marginals = 1
        for value in value_combination:
            marginals *= pdf.shrink_dimensions_to(sampled_labels[i]).joint_probabilities
        """Joint pdf summation"""
        acc = sampled_pdf.joint_probabilities[i] * log(sampled_pdf.joint_probabilities[i]/marginals)
        acc[np.isnan(acc)] = 0.0
        acc[np.isinf(acc)] = 0.0
        mi += np.sum(acc)

    np.seterr(all="warn")
    return mi

