import os
import sys

import scipy.io as scio
import matplotlib.pyplot as mpl






# Changes the directory that is being worked in. This allows loadmat to access files in the Data folder
# loadmat only looks in the current directory, thus this function changes the current directory to the Data folder
if sys.platform == ("win32" or "cygwin"):
    os.chdir(os.getcwd()+"\\Data_Input")
elif sys.platform == "darwin":
    os.chdir(os.getcwd()+"/Data_Input")

# Function task the name of the MatLab files (including the .mat at the end)
# Error catching
def open_matlab_file(matlab_filename):
    try:
        mat = scio.loadmat(matlab_filename, appendmat=True)
    except:
        try:
            mat = scio.loadmat(matlab_filename, appendmat=False)
        except FileNotFoundError:
            print("File not found")
            quit()
    b = scio.whosmat(matlab_filename)[0][0]

    stim_time = []
    stim_code = []
    firing = []
    separate_dictionary = {}
    trialled_firing = []
    for x in mat['StimTrig'][0][0][4]:
        stim_time.append(x[0])
    for x in mat['StimTrig'][0][0][5]:
        if x[0] != 62:
            stim_code.append(x[0])
        else:
            stim_code.append(0)
    for x in mat[b][0][0][4]:
        firing.append(x[0])
    counter = 1
    for i,x in enumerate(stim_code):
        if x == 0:
            separate_dictionary[counter] = i
            counter += 1
    Temporary_List = []
    Temporary_Key = 1
    for x in firing:
        try:
            if x <= stim_time[separate_dictionary[Temporary_Key]]:
                Temporary_List.append(x)
            else:
                trialled_firing.append(Temporary_List)
                Temporary_List = []
                Temporary_Key += 1
        except KeyError:
            break
    return stim_code, stim_time, firing, separate_dictionary, trialled_firing

# Function to find frequency of firing 200 milliseconds before stimuli applied
# Iterate through firing list by popping items off
def freqeuncy_before_stimulus(firing_stamp, stimulus_type, stim_timestamp):
    results = [[],[],[],[],[],[],[],[],[],[]]
    total = 0
    neuron_iterate = firing_stamp.pop(0)
    for i,x in enumerate(stimulus_type):
        if x != 0:
            n = stim_timestamp[i]
            while firing_stamp:
                if neuron_iterate >= n:
                    results[x-1].append(total/0.2)
                    total = 0
                    break
                elif neuron_iterate >= (n-0.2):
                    total += 1
                neuron_iterate = firing_stamp.pop(0)
    return results

# Error catching
def trial_graphs(sch_wav_trials, stimuli, stimuli_time, dictionary_trial, user_selection = "1"):
    user_selection = str(user_selection)
    mpl.ioff()
    if user_selection == "break":
        return
    elif user_selection == "quit":
        quit()
    elif user_selection == "1":
        mpl.figure(num="Trial", figsize=[14,7])
        for x in sch_wav_trials[int(user_selection)-1]:
            mpl.plot([x,x], [0,10], "r-")
        mpl.plot(stimuli_time[0:dictionary_trial[1]+1], stimuli[0:dictionary_trial[1]+1], 'ko', ms=6)
        for i,x in enumerate(stimuli[0:dictionary_trial[1]+1]):
            mpl.annotate(s=str(x), xy=(stimuli_time[i],x), xytext=(stimuli_time[i],10.2), color='0.2', size=13, weight="bold")
        mpl.xlim(xmin=0, xmax=stimuli_time[dictionary_trial[1]])
        mpl.draw()
        mpl.show(block=False)
    else:
        mpl.figure(num="Trial", figsize=[14,7])
        for x in sch_wav_trials[int(user_selection)-1]:
            mpl.plot([x,x], [0,10], "r-")
        mpl.plot(stimuli_time[dictionary_trial[int(user_selection)-1]:dictionary_trial[int(user_selection)]+1],
                 stimuli[dictionary_trial[int(user_selection)-1]:dictionary_trial[int(user_selection)]+1],
                 'ko', ms=6)
        for i,x in enumerate(stimuli[dictionary_trial[int(user_selection)-1]:dictionary_trial[int(user_selection)]+1]):
            mpl.annotate(s=str(x), xy=(stimuli_time[i+dictionary_trial[int(user_selection)-1]],x), xytext=(stimuli_time[i+dictionary_trial[int(user_selection)-1]],10.2), color='0.2', size=13, weight="bold")
        mpl.xlim(xmin=stimuli_time[dictionary_trial[int(user_selection)-1]], xmax=stimuli_time[dictionary_trial[int(user_selection)]])
        mpl.draw()
        mpl.show(block=False)

StimTrig_Stimuli, StimTrig_Time, Sch_wav_Time, trial_dictionary, Sch_wav_Time_Trialled = open_matlab_file('660806_rec03_all')
print(len(Sch_wav_Time))
# the extra 50 comes from all the 0's (reset stimuli)

# a = freqeuncy_before_stimulus(Sch_wav_Time, StimTrig_Stimuli, StimTrig_Time)
# print(a[9][0], a[7][0])

# trial_graphs(Sch_wav_Time_Trialled, StimTrig_Stimuli, StimTrig_Time, trial_dictionary)

# total = 0
# restriction = 0
# show_list = []
# for x in Sch_wav_Time:
#     if x >= restriction and x < (restriction + 0.001):
#         total += 1
#     else:
#         restriction += 0.001
#         show_list.append(total)
#         total = 1
# show_list.append(total)
# print(show_list)
# total = 0
# highest = 0
# for x in show_list:
#     if x > highest:
#         highest = x
#     total += x
# print(total)
# print(len(Sch_wav_Time))
# print(highest)

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