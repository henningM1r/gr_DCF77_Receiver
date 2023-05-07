# this module will be imported in the into your flowgraph


import math


f1 = -math.pi
f2 = +math.pi

f = 0


def shift_freq(weighted_trigger):
    global f1, f2, f

    if weighted_trigger:
        f = f - weighted_trigger

    if f <= f1:
        f = f2

    return f
