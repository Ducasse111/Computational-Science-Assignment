# Scipy is necessry for opening the MatLab files
# MatPlotLib is not used yet, but may be used to plot the data
# CSV is so that the data could be written to excel
import scipy.io as scio
import matplotlib.pyplot as mpl
import csv

# Function task the name of the MatLab files (including the .mat at the end)
def open_matlab_file(matlab_filename):
    # headers of relevant data = 'StimTrig', b
    mat = scio.loadmat(matlab_filename)
    stim_trig_raw = mat['StimTrig']
    for x in mat.keys():
        # I assumed that Sch_wav and Schmitt would be used interchangebly thoughout the files
        if x not in ("__version__", "__globals__", "StimTrig", "__header__"):
            b = x
    return [stim_trig_raw, mat[b]]
# Returns a list with 2 elements
# Element [0] is the StimTrig dictionary entry
# Element [1] is the Sch_wav (or Schmitt for file 1) dictionary entry

StimTrig_Time = []
StimTrig_Stimuli = []
Sch_wav_Time = []

file_name = '654508_rec02_f05.mat'

# Pulls the timestamps in StimTrig into a list
for x in open_matlab_file(file_name)[0][0][0][4]:
    StimTrig_Time.append(x[0])

# Pulls the order of stimuli from StimTrif into a list
for x in open_matlab_file(file_name)[0][0][0][5]:
    StimTrig_Stimuli.append(x[0])

# Pulls the timestamps of Sch_wav into a list
for x in open_matlab_file(file_name)[1][0][0][4]:
    Sch_wav_Time.append(x[0])

print(StimTrig_Time)
print(StimTrig_Stimuli)
print(Sch_wav_Time)

# This commented section was used to pull the data into excel
# It will write into a csv file (which can be converted to excel externally)
# It writes the first column of the csv file to contain the Sch_wav timestamps
# There is then a 2 column break following this
# It then writes the StimTrig timestamps into a column, and the StimTrig stimuli into the next

# writing_file = open("test_graph.csv", "r+", newline='')
# john_cena = csv.writer(writing_file)
# counter = 0
# for x in Sch_wav_Time:
#     try:
#         john_cena.writerow([x, "", "", StimTrig_Time[counter], StimTrig_Stimuli[counter]])
#     except IndexError:
#         john_cena.writerow([x])
#     counter += 1