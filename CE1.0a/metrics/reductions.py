'''
Utilities for the data management.
'''

import numpy as np

def count(data):
    '''
    Counts the number of population in a NxP matrix.

    Input:
        data            data variable NxP
                            N = elements
                            P = population

        returns         population counter N
                            N = elements

    '''
    return np.array(map(len, data))

def join(data, axisA, axisB):
    '''
    Joins the data from two different axis.

    Input:
        data            data variable with 2 or more dimensions

        returns         reduced array
    '''
    assert axisA != axisB, "Join axes must be different"
    shape = list(data.shape)
    assert axisA < len(shape) and axisB < len(shape), "Join axis must be lower than number of data dimensions"

    newAxis = shape[axisA] * shape[axisB]
    shape[axisB] = newAxis
    del shape[axisA]
    return data.reshape(shape)
    
