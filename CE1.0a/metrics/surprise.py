#!/usr/bin/python
# Filename: surprise.py
'''
Surprise metrics.
'''

import numpy as np

def calculate(p, logbase="log2"):
    '''
    Surprise metric.

    Input:
        p           probabiliy variable with any shape

    Returns: 
                    surprise
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    log = getattr(np, logbase)
    #Ignore warning from log2(0) and zero division. It is quicker to compute over all probabilities and correct after that than search positive probability.
    np.seterr(all="ignore")
    inverse = 1.0/p
    s = log(inverse)
    s[np.isnan(s)] = 0.0
    s[np.isinf(s)] = 0.0
    np.seterr(all="warn")
    return s
