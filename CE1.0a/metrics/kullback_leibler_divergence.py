#!/usr/bin/python
# Filename: kullback-leibler_divergence.py
'''
Kullback-Leibler divergence metrics
'''

import numpy as np

def calculate(pdf_p, pdf_q, logbase="log2"):
    '''
    Kullback-Leibler divergence metric.

    Input:
        pdf_p       probability p variable NxB
                        N = elements
                        B = bins
        pdf_q       probability q variable NxB
                        N = elements
                        B = bins
        logbase        Base for the logarithm ("log2", "log", "log10")
    Returns:
                    entropy N
                        N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    log = getattr(np, logbase)
    #Ignore warning from log2(0). It is quicker to compute over all probabilities and correct after that than search positive probability.
    np.seterr(all="ignore")
    div = pdf_p/pdf_q
    logs = log(div) * pdf_p
    logs[np.isnan(logs)] = 0.0
    logs[np.isinf(logs)] = 0.0
    np.seterr(all="warn")
    logsAcc = np.sum(logs, axis=1)
    return logsAcc
