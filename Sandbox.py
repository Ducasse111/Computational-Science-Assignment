import scipy.io as scio
import matplotlib.pyplot as mpl

mat = scio.loadmat('654508_rec02.mat')

# Keys: '__header__', 'Schmitt', 'StimTrig', '__globals__', '__version__', ONLY FOR '654508_rec02.mat'

StimTrig_Raw = mat['StimTrig']
StimTrig_Data = []
Schmitt_Raw = mat['Schmitt']
Schmitt_Data = []
print(StimTrig_Raw)
print(StimTrig_Raw[0][0])
#print(Schmitt_Raw)