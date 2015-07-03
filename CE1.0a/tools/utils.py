'''
Common utility class.
'''

def frange(x, y, jump):
    '''
    Iterator for floating point numbers.

    Input:
        x       starting number
        y       limit number
        jump    increment
    '''
    while x < y:
        yield x
        x += jump
