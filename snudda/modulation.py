import numpy as np


def alpha(parameter=None):

    ht = parameter['ht']
    tstart = parameter['tstart']
    gmax = parameter['gmax']
    tau = parameter['tau']

    mag = list()
    
    '''
    calc and returns a "magnitude" using an alpha function -> used for modulation
        transients

    ht      = simulation time (h.t)
    tstart  = time when triggering the function
    gmax    = maximal amplitude of curve (default 1; transient must lie between 0-1)
    tau     = time constant of alpha function
    '''

    for t_step in ht:

        if t_step >= tstart:
            t = (t_step - tstart) / tau
            e = np.exp(1 - t)
            mag.append(gmax * t * e)

        else:
            mag.append(0)
    return mag


def step(ht, tstart, gmax=None):
    mag = 0

    if ht > tstart:
        mag = gmax

    return mag


def bathapplication(ht, mag=1):
    return mag


def alpha_background(ht, gmax, tau, tonic, tstart=[]):
    mag = 0

    for start in tstart:
        mag = mag + alpha(ht, tstart[index], gmax, tau) + tonic

    return mag


def time_series():
    return array
