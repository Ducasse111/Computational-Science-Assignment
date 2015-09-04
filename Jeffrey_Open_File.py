import scipy.io as scio
import matplotlib.pyplot as mpl
mat = scio.loadmat('654508_rec02.mat')

# Keys: '__header__', 'Schmitt', 'StimTrig', '__globals__', '__version__'

StimTrig_Raw = mat['StimTrig']
StimTrig_Data = []
Schmitt_Raw = mat['Schmitt']
Schmitt_Data = []
print(StimTrig_Raw)
print(Schmitt_Raw)

for x in StimTrig_Raw:
    print(x[0][5])
    for x_in in x[0][4]:
        StimTrig_Data.append(x_in.tolist()[0])
    for x_in in x[0][5]:
        for x_in_in in x_in:
            StimTrig_Data.append(x_in_in.tolist())
print(StimTrig_Data)
print(len(StimTrig_Data))

for x in Schmitt_Raw:
    for x_in in x[0][4]:
        Schmitt_Data.append(x_in.tolist()[0])
print(Schmitt_Data)
print(len(Schmitt_Data))