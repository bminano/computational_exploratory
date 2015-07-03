#!/usr/bin/python

import numpy as np
import entropy_shannon as shannon

"""
Input:
    pdf_a            pdf variable A 
                    N = elements
                    B = bins
    pdf_b            pdf variable B
                    N = elements
                    B = bins
    joint_pdf        joint pdf
                    N = elements
                    BA = bins A
                    BB = bins B
    logbase            Base for the logarithm ("log2", "log", "log10")

    returns            mutual information N
                    N = elements

"""
def calculate(pdf_a, pdf_b, joint_pdf, logbase="log2"):
    '''
    Mutual information metric.

    Input:
        pdf_a       probability A variable NxB
                        N = elements
                        B = bins
        pdf_b       probability B variable NxB
                        N = elements
                        B = bins
        joint_pdf   joint pdf
                        N = elements
                        BA = bins A
                        BB = bins B
        logbase        Base for the logarithm ("log2", "log", "log10")
    Returns:
                    mutual information N
                        N = elements
    '''
    assert logbase in ["log2", "log", "log10"], "Logbase parameter must be one of (\"log2\", \"log\", \"log10\")"
    assert len(pdf_a) == len(pdf_b), "The mutual information parameters A and B must have the same number of elements"
    assert len(pdf_a) == len(joint_pdf), "The mutual information parameters A and Joint PDF must have the same number of elements"
    log = getattr(np, logbase)

    number_of_binsA = pdf_a.shape[1]
    number_of_binsB = pdf_b.shape[1]

    elements = len(pdf_a)

    mi = np.ndarray(shape=(elements),dtype='float')
    for elem in xrange(elements):
        acc = 0
        for nbA in xrange(number_of_binsA):
            for nbB in xrange(number_of_binsB):
                if pdf_a[elem][nbA] * pdf_b[elem][nbB] > 0 and joint_pdf[elem, nbA, nbB] > 0:
                    acc = acc + joint_pdf[elem, nbA, nbB] * log(joint_pdf[elem, nbA, nbB]/(pdf_a[elem][nbA] * pdf_b[elem][nbB]))
        mi[elem] = acc
    return mi

def entropies(pdf, cond_pdf, logbase="log2"):
    '''
    Mutual information metric based on entropies.

    Input:
        pdf_a       probability A variable NxB
                        N = elements
                        B = bins
        cond_pdf    conditional probability NxBAxBB
                        N = elements
                        BA = bins A
                        BB = bins B
        logbase        Base for the logarithm ("log2", "log", "log10")
    Returns:
                    mutual information N
                        N = elements
    '''

    return shannon.calculate(pdf, logbase) - shannon.conditional(pdf, cond_pdf, logbase)


