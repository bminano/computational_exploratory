#!/usr/bin/python
# Filename: entropy_shannon.py
'''
Shannon entropy metrics.
'''

import numpy as np
import sys, getopt

def calculate(pdf, logbase="log2"):
    '''
    Shannon entropy

    Input:
        pdf         probability variable NxB
                        N = elements
                        B = bins
        logbase     Base for the logarithm ("log2", "log", "log10")

    Returns:
                    entropy N
                        N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    log = getattr(np, logbase)
    #Ignore warning from log2(0). It is quicker to compute over all probabilities and correct after that than search positive probability.
    np.seterr(all="ignore")
    logs = log(pdf) * pdf
    norm = log(pdf.shape[1])
    logs[np.isnan(logs)] = 0.0
    np.seterr(all="warn")
    logsAcc = -np.sum(logs, axis=1)/norm
    return logsAcc

def conditional(pdf, pdf_cond, logbase="log2"):
    '''
    Conditional shannon entropy

    Input:
        pdf         probability variable NxB
                        N = elements
                        B = bins A
        pdf_cond    conditional probability variable NxBAxBB
                        N = elements
                        BA = bins A
                        BB = bins B
        logbase     Base for the logarithm ("log2", "log", "log10")

    Returns:
                    entropy N
                        N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    log = getattr(np, logbase)
    #Ignore warning from log2(0). It is quicker to compute over all probabilities and correct after that than search positive probability.
    np.seterr(all="ignore")
    logs_cond = log(pdf_cond) * pdf_cond
    logs_cond[np.isnan(logs_cond)] = 0.0
    np.seterr(all="warn")
    logs_condAcc = np.sum(logs_cond, axis=2)*pdf
    acc = -np.sum(logs_condAcc, axis=1)
    return acc
