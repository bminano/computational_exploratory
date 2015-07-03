import numpy as np

"""
Input:
    data            data variable NxP
                    N = elements
                    P = population

    returns            population counter N
                    N = elements

"""
def count(data):
    return np.array(map(len, data))

"""
Joins the data from two different axis.
Input:
    data            data variable with 2 or more dimensions

    returns            reduced array

"""
def join(data, axisA, axisB):
    if axisA == axisB:
        print 'ERROR: Join axes must be different.'
        sys.exit()
    shape = list(data.shape)
    if axisA > len(shape) or axisB > len(shape):
        print 'ERROR: Join axis must be lower than number of data dimensions.'
        sys.exit()
    newAxis = shape[axisA] * shape[axisB]
    shape[axisB] = newAxis
    del shape[axisA]
    return data.reshape(shape)
    
