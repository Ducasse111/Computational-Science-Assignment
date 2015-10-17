# File Reference Number: 00
import os
import sys
import io

import scipy.io as scio
import matplotlib.pyplot as mpl
import matplotlib.mlab as mlab
import numpy as np

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

    # Variable Declaration
    b = scio.whosmat(matlab_filename)[0][0]
    number_trials = 0
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
            number_trials += 1
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
    return stim_code, stim_time, firing, separate_dictionary, trialled_firing, number_trials

def trial_mean_sd(trialled_sch_wav, stimtrig, stimtime, stim_dictionary, trial_selection = 1):
    trial_selection = int(trial_selection)
    stimulied_firing = []
    temporary_list = []
    if trial_selection == 1:
        counter = 0
        for x in trialled_sch_wav[trial_selection-1]:
            if x <= stimtime[0:stim_dictionary[trial_selection]+1][counter]:
                temporary_list.append(x)
            else:
                stimulied_firing.append(temporary_list)
                temporary_list = [x]
                counter += 1
    else:
        counter = 1
        for x in trialled_sch_wav[trial_selection-1]:
            if x <= stimtime[stim_dictionary[trial_selection-1]:stim_dictionary[trial_selection]+1][counter]:
                temporary_list.append(x)
            else:
                stimulied_firing.append(temporary_list)
                temporary_list = [x]
                counter += 1
    stimulied_firing.append(temporary_list)
    
    if trial_selection == 1:
        start_baseline = stimtime[0]-0.2
    else:
        start_baseline = stimtime[stim_dictionary[trial_selection-1]+1]-0.2

    temp_slice = 0
    for i,x in enumerate(stimulied_firing[0]):
        if x >= start_baseline:
            temp_slice = i
            break
    random_list = stimulied_firing[0][temp_slice:]
    
    total = 0
    counter = 0
    ms_bin = []
    item = random_list.pop(0)
    while counter != 200:
        false_flag = True
        while false_flag:
            if item >= start_baseline and item < (start_baseline+0.001):
                total += 1
                try:
                    item = random_list.pop(0)
                except IndexError:
                    false_flag = False
            else:
                false_flag = False
        ms_bin.append(total)
        start_baseline+=0.001
        total = 0
        counter += 1

    return stimulied_firing, ms_bin
    
def probability_density_function_graph(firing_list, mean, sd):
    time_interval = firing_list[-1] - firing_list[0]
    a, b, c = mpl.hist(x=firing_list, bins=(int(time_interval/0.001)), normed=1)
    pdf = mlab.normpdf(b, mean, sd)
    mpl.plot(b, pdf, "b-")
    mpl.show()
    return

def trial_graphs(sch_wav_trials, stimuli, stimuli_time, dictionary_trial, user_selection = "1"):
    user_selection = str(user_selection)

    mpl.ioff()
    mpl.figure(num="Trial", figsize=[14,7])
    # mpl.show(block=False)

    if user_selection == "1":
        mpl.cla()

        for x in sch_wav_trials[int(user_selection)-1]:
            mpl.plot([x,x], [0,10], "r-")
        mpl.plot(stimuli_time[0:dictionary_trial[1]+1], stimuli[0:dictionary_trial[1]+1], 'ko', ms=6)
        for i,x in enumerate(stimuli[0:dictionary_trial[1]+1]):
            mpl.annotate(s=str(x), xy=(stimuli_time[i],x), xytext=(stimuli_time[i],10.2), color='0.2', size=13, weight="bold")
        mpl.xlim(xmin=0, xmax=stimuli_time[dictionary_trial[1]])

        mpl.xlabel("Time (s)")
        mpl.ylabel("Amplitude of Stimuli")

        fig = mpl.gcf()

        sio = io.BytesIO()
        fig.savefig(sio, format='png')
        return sio.getvalue()

    else:
        mpl.cla()

        for x in sch_wav_trials[int(user_selection)-1]:
            mpl.plot([x,x], [0,10], "r-")

        mpl.plot(stimuli_time[dictionary_trial[int(user_selection)-1]:dictionary_trial[int(user_selection)]+1],
                 stimuli[dictionary_trial[int(user_selection)-1]:dictionary_trial[int(user_selection)]+1],
                 'ko', ms=6)

        for i,x in enumerate(stimuli[dictionary_trial[int(user_selection)-1]:dictionary_trial[int(user_selection)]+1]):
            mpl.annotate(s=str(x), xy=(stimuli_time[i+dictionary_trial[int(user_selection)-1]],x), xytext=(stimuli_time[i+dictionary_trial[int(user_selection)-1]],10.2), color='0.2', size=13, weight="bold")
        mpl.xlim(xmin=stimuli_time[dictionary_trial[int(user_selection)-1]], xmax=stimuli_time[dictionary_trial[int(user_selection)]])

        mpl.xlabel("Time (s)")
        mpl.ylabel("Amplitude of Stimuli")

        fig = mpl.gcf()

        sio = io.BytesIO()
        fig.savefig(sio, format='png')
        return sio.getvalue()

StimTrig,StimTrigTime,SchWav,DictionaryMarkingResetStimuli,SchWavSplitIntoTrials,NotImportant = open_matlab_file("660809_rec03_all")

TrialSelect = 1
TestResult, b = trial_mean_sd(SchWavSplitIntoTrials, StimTrig, StimTrigTime, DictionaryMarkingResetStimuli, TrialSelect)
print(len(TestResult[0]), TestResult[0][-16])
print(len(b), b)
counting = 0
for x in b:
    counting += x
print(counting)
# pdf = TestResult[1]
# probability_density_function_graph(pdf, np.mean(pdf), np.std(pdf))