__author__ = 'Ben'

import scipy.io as sio

contents = sio.loadmat("Test")
trig = contents["StimTrig"]
print(trig[0])
