# Scipy is necessary for opening the MatLab files
# MatPlotLib is not used yet, but may be used to plot the data
# CSV is so that the data could be written to excel

import scipy.io as scio
import matplotlib.pyplot as mpl
import csv
import os

# Changes the directory that is being worked in. This allows loadmat to access files in the Data folder
# loadmat only looks in the current directory, thus this function changes the current directory to the Data folder
os.chdir(os.getcwd()+"\\Data_Input")

# Function task the name of the MatLab files (including the .mat at the end)
def open_matlab_file(matlab_filename):
    # headers of relevant data = 'StimTrig', b
    try:
        mat = scio.loadmat(matlab_filename, appendmat=True)
    except FileNotFoundError:
        # Find better way to deal with errors
        print("File not found")
        quit()
    stim_trig_raw = mat['StimTrig']
    b = scio.whosmat(matlab_filename)[0][0]
    return [stim_trig_raw, mat[b]]
# Returns a list with 2 elements
# Element [0] is the StimTrig dictionary entry
# Element [1] is the Sch_wav (or Schmitt for file 1) dictionary entry

StimTrig_Time = []
StimTrig_Stimuli = []
Sch_wav_Time = []

file_name = '660804_rec03_all'

# Pulls the timestamps in StimTrig into a list
for x in open_matlab_file(file_name)[0][0][0][4]:
    StimTrig_Time.append(x[0])

# Pulls the order of stimuli from StimTrif into a list
for x in open_matlab_file(file_name)[0][0][0][5]:
    StimTrig_Stimuli.append(x[0])

# Pulls the timestamps of Sch_wav into a list
for x in open_matlab_file(file_name)[1][0][0][4]:
    Sch_wav_Time.append(x[0])

print("StimTrig_Time", StimTrig_Time)
print("StimTrig_Stimuli", StimTrig_Stimuli)
print("Sch_wav_Time", Sch_wav_Time)

# Playing around with frequency

# average_frequency = float(len(Sch_wav_Time)/(float(Sch_wav_Time[-1])-float(Sch_wav_Time[1])))
# print(average_frequency)
# print(1/average_frequency)
#
# Total = 0
# for i,x in enumerate(Sch_wav_Time):
#     try:
#         Total += (float(Sch_wav_Time[i+1])-float(x))
#     except IndexError:
#         break
#
# print((Total/(len(Sch_wav_Time)))-(1/average_frequency))
# print((Total/(len(Sch_wav_Time)-1))-(1/average_frequency))

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