#!/usr/bin/python
# Filename: fisher.py
'''
Fisher metrics.
'''

import numpy as np
import sys, getopt

def calculate(pdf, dPar, dVal, logbase="log2"):
    '''
    Fisher metric.

    Input:
        pdf             probability variable NxB
                            N = elements
                            B = bins
        dPar            increment of discrete parameter
        dVal            increment of binned values
        logbase         Base for the logarithm ("log2", "log", "log10")

    Returns:
                        entropy N - 2
                            N - 2 = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    log = getattr(np, logbase)
    #Ignore warning from log2(0). It is quicker to compute over all probabilities and correct after that than search positive probability.
    np.seterr(all="ignore")
    logs = ((log(np.roll(pdf, -1, axis=0)) - log(np.roll(pdf, 1, axis=0)))/(2*dPar))**2 * pdf
    logs[np.isnan(logs)] = 0.0
    logs[np.isinf(logs)] = 0.0
    np.seterr(all="warn")
    logsAcc = np.sum(logs, axis=1) * dVal
    return logsAcc[1:len(logsAcc) - 1]

