#!/usr/bin/python
# Filename: hellinger_distance.py
'''
Hellinger distance metric.
'''

import numpy as np


def calculate(pdf_p, pdf_q):
    '''
    Hellinger distance metric.

    Input:
        pdf_p       probability p variable NxB
                        N = elements
                        B = bins
        pdf_q       probability q variable NxB
                        N = elements
                        B = bins
    Returns:
                    entropy N
                        N = elements
    '''
    return 1.0/np.sqrt(2) * np.sqrt(np.sum(np.power(np.sqrt(pdf_p) - np.sqrt(pdf_q), 2), axis=1))
