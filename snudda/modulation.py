import numpy as np


def alpha(ht, tstart, gmax, tau):
    '''
    calc and returns a "magnitude" using an alpha function -> used for modulation
        transients

    ht      = simulation time (h.t)
    tstart  = time when triggering the function
    gmax    = maximal amplitude of curve (default 1; transient must lie between 0-1)
    tau     = time constant of alpha function
    '''

    t = (ht - tstart) / tau
    e = np.exp(1 - t)
    mag = gmax * t * e

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
