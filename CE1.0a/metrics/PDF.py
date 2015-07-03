#!/usr/bin/python
'''
Probability Density Function (PDF) calculations.
'''

import numpy as np


def single(data, bin_values, continuous_bins):
    '''
    Marginal PDF calculation.

    Input:
        data            data variable NxP
                            N = elements
                            P = population
        bin_values      values of the bins
        continuous_bins true if the values of the bins are continuous

    Returns:
                        pdf NxB
                            N = elements
                            B = Bin index
    '''
    number_of_bins = len(bin_values)
    if continuous_bins:
        number_of_bins = number_of_bins - 1
    elements = len(data)
    pdf = np.ndarray(shape=(elements, number_of_bins),dtype='float')

    population = np.repeat(np.array(map(len, data)).reshape((elements, 1)), number_of_bins, axis=1)
    for elem in xrange(elements):
        for nb in xrange(number_of_bins):
            if continuous_bins:
                pdf[elem, nb] = np.sum((bin_values[nb] <= data[elem]) & (data[elem] < bin_values[nb + 1]))
            else:
                pdf[elem, nb] = np.sum((bin_values[nb] == data[elem]))
    np.seterr(all="ignore")
    pdf = pdf/population
    pdf[np.isnan(pdf)] = 0.0
    pdf[np.isinf(pdf)] = 0.0
    np.seterr(all="warn")

    return pdf

def joint(data_a, bin_values_a, continuous_bins_a, data_b, bin_values_b, continuous_bins_b):
    '''
    Joint PDF calculation.

    Input:
        data_a              data variable A NxP
                                N = elements
                                P = population
        bin_values_a        values of the bins
        continuous_bins_a   true if the values of the bins are continuous
        data_b              data variable B NxP
                                N = elements
                                P = population
        bin_values_b        values of the bins
        continuous_bins_b   true if the values of the bins are continuous

    Returns:
                        joint pdf NxBAxBB
                            N = elements
                            BA = bin index A
                            BB = bin index B
    '''
    assert len(data_a) == len(data_b), "The data parameters A and B must have the same number of elements"

    number_of_binsA = len(bin_values_a)
    if continuous_bins_a:
        number_of_binsA = number_of_binsA - 1
    number_of_binsB = len(bin_values_b)
    if continuous_bins_b:
        number_of_binsB = number_of_binsB - 1

    elements = len(data_a)
    j_pdf = np.zeros(shape=(elements, number_of_binsA, number_of_binsB),dtype='float')
    population = np.repeat(np.repeat((np.array(map(len, data_a))).reshape((elements, 1, 1)), number_of_binsA, axis=1), number_of_binsB, axis=2)
    for elem in xrange(elements):
        for nbA in xrange(number_of_binsA):
            if continuous_bins_a:
                boolsA = ((bin_values_a[nbA] <= data_a[elem]) & (data_a[elem] < bin_values_a[nbA + 1]))
            else:
                boolsA = ((bin_values_a[nbA] == data_a[elem]))
            for nbB in xrange(number_of_binsB):
                if continuous_bins_b:
                    boolsB = ((bin_values_b[nbB] <= data_b[elem]) & (data_b[elem] < bin_values_b[nbB + 1]))
                else:
                    boolsB = ((bin_values_b[nbB] == data_b[elem]))

                j_pdf[elem, nbA, nbB] = np.sum(boolsA*boolsB)

    np.seterr(all="ignore")
    j_pdf = j_pdf/population
    j_pdf[np.isnan(j_pdf)] = 0.0
    j_pdf[np.isinf(j_pdf)] = 0.0
    np.seterr(all="warn")
    
    return j_pdf
    
def conditional(data_a, bin_values_a, continuous_bins_a, data_b, bin_values_b, continuous_bins_b):
    '''
    Joint PDF calculation.

    Input:
        data_a              data variable A NxP
                                N = elements
                                P = population
        bin_values_a        values of the bins
        continuous_bins_a   true if the values of the bins are continuous
        data_b              data variable B NxP
                                N = elements
                                P = population
        bin_values_b        values of the bins
        continuous_bins_b   true if the values of the bins are continuous

    Returns:
                        conditional pdf NxBAxBB
                            N = elements
                            BA = bin index A
                            BB = bin index B
    '''
    assert len(data_a) == len(data_b), "The data parameters A and B must have the same number of elements"

    number_of_binsA = len(bin_values_a)
    if continuous_bins_a:
        number_of_binsA = number_of_binsA - 1
    number_of_binsB = len(bin_values_b)
    if continuous_bins_b:
        number_of_binsB = number_of_binsB - 1

    j_pdf = np.zeros(shape=(elementsA, number_of_binsA, number_of_binsB),dtype='float')
    population = np.repeat(np.repeat((np.array(map(len, data_a))*np.array(map(len, data_b))).reshape((elementsA, 1, 1)), number_of_binsA, axis=1), number_of_binsB, axis=2)
    for elem in xrange(elementsA):
        for nbA in xrange(number_of_binsA):
            if continuous_bins_a:
                boolsA = ((bin_values_a[nbA] <= data_a[elem]) & (data_a[elem] < bin_values_a[nbA + 1]))
            else:
                boolsA = ((bin_values_a[nbA] == data_a[elem]))
            for nbB in xrange(number_of_binsB):
                if continuous_bins_b:
                    boolsB = ((bin_values_b[nbB] <= data_b[elem]) & (data_b[elem] < bin_values_b[nbB + 1]))
                else:
                    boolsB = ((bin_values_b[nbB] == data_b[elem]))

                acc = 0
                for index in xrange(len(boolsA)):
                    acc = acc + np.sum(boolsA[index]*boolsB)
                j_pdf[elem, nbA, nbB] = acc

    np.seterr(all="ignore")
    j_pdf = j_pdf/population
    j_pdf[np.isnan(j_pdf)] = 0.0
    j_pdf[np.isinf(j_pdf)] = 0.0
    np.seterr(all="warn")
    
    return j_pdf
