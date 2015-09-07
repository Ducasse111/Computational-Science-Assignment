import scipy.io as scio
import matplotlib.pyplot as mpl

def open_matlab_file(matlab_filename):
    # headers of relevant data = 'StimTrig', b
    mat = scio.loadmat(matlab_filename)
    stim_trig_raw = mat['StimTrig']
    for x in mat.keys():
        if x != "__version__" and x != "__globals__" and x != "StimTrig" and x != "__header__":
            b = x
    return [['StimTrig', stim_trig_raw], [b, mat[b]]]

#print(open_matlab_file('654508_rec02.mat')[0][1][0][0][4])
for x in open_matlab_file('654508_rec02.mat')[0][1][0][0][4]:
    print(x[0])