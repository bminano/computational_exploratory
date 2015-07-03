#!/usr/bin/python

import numpy as np

def calculate(pdf, variables, dPar, dVal, logbase="log2", periodical=False):
    """
    Input:
        pdf                     joint pdf class
        variables               variables for the derivative. Could fit multiple labels (e.g. "var" fits "var_1", "var_2", "var_3",...)
        dPar                    increment of discrete parameter
        dVal                    increment of binned values
        logbase                 Base for the logarithm ("log2", "log", "log10")

        returns                 fisher metrics for the variables derivatives, integrated by theirs marginals.
    """

    np.seterr(all="ignore")
    """Get log proper function"""
    log = getattr(np, logbase)

    labels = pdf.get_labels(variables)
    """Shrink to variables selected"""
    shrink = pdf.shrink_dimensions_to(labels)
    """Concatenate marginals"""
    marginals = np.ndarray((len(labels), shrink.get_num_bins()[0]))
    for i,l in enumerate(labels):
        assert shrink.get_num_bins()[0] == shrink.get_num_bins()[i], "Number of bins of all variables must be the same"  
        """Marginalize each variable independently"""
        marginals[i, :] = shrink.shrink_dimensions_to([l]).joint_probabilities

    """Fisher calculation"""
    logs = ((log(np.roll(marginals, -1, axis=0)) - log(np.roll(marginals, 1, axis=0)))/(2*dPar))**2 * marginals
    logs[np.isnan(logs)] = 0.0
    logs[np.isinf(logs)] = 0.0
    np.seterr(all="warn")
    fisher = np.sum(logs, axis=1) * dVal

    """Extreme values are only valid for periodical calculation"""
    if not periodical:
        return fisher[1:len(fisher) - 1]
    return fisher


