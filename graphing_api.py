import os
import sys
import io

import scipy.io as sc_io
import matplotlib.pyplot as mpl
import numpy as np

platform_filename = ''
if sys.platform == ("win32" or "cygwin"):
    os.chdir(os.getcwd()+"\\Data_Input")
    platform_filename = '\\'

elif sys.platform == "darwin":
    os.chdir(os.getcwd()+"/Data_Input")
    platform_filename = '/'


class GraphingApplication:
    def __init__(self):
        self.number_trials = 0

        self.stimuli_time = []
        self.stimuli_code = []
        self.firing = []
        self.trialled_firing = []

        self.dictionary_marking_0s_index_in_stimuli_lists = {}

        self.mat = None

    def open_file(self, file):
        renamed_file = file.split('/')
        file_path = renamed_file[:-1]
        file_name = renamed_file[-1]

        path = ''
        original_path = os.getcwd()

        for x, keyword in enumerate(file_path):
            path += keyword + platform_filename

        os.chdir(path)

        try:
            self.mat = sc_io.loadmat(file_name, appendmat=True)
        except Exception as e:
            try:
                self.mat = sc_io.loadmat(file_name, appendmat=False)
            except FileNotFoundError:
                print("File not found: ", e)

        temp_var = sc_io.whosmat(file)[0][0]
        os.chdir(original_path)

        for x in self.mat['StimTrig'][0][0][4]:
            self.stimuli_time.append(x[0])
        for x in self.mat['StimTrig'][0][0][5]:
            if x[0] != 62:
                self.stimuli_code.append(x[0])
            else:
                self.stimuli_code.append(0)
                self.number_trials += 1
        for x in self.mat[temp_var][0][0][4]:
            self.firing.append(x[0])
        counter = 1
        for i, x in enumerate(self.stimuli_code):
            if x == 0:
                self.dictionary_marking_0s_index_in_stimuli_lists[counter] = i
                counter += 1

        temp_list = []
        temp_key = 1
        for x in self.firing:
            try:
                if x <= self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[temp_key]]:
                    temp_list.append(x)
                else:
                    self.trialled_firing.append(temp_list)
                    temp_list = []
                    temp_key += 1
            except KeyError:
                break

    def get_graph(self, trial):
        index = trial
        if index == "1":
            mpl.cla()
            for x in self.trialled_firing[int(index)-1]:
                mpl.plot([x, x], [0, 10], "r-")

            mpl.plot(self.stimuli_time[0:self.dictionary[1]+1],
                     self.stimuli_code[0:self.dictionary[1]+1], 'ko', ms=6)

            for i, x in enumerate(self.stimuli_code[0:self.dictionary[1]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i], x),
                             xytext=(self.stimuli_time[i], 10.2), color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=0, xmax=self.stimuli_time[self.dictionary[1]])

            mpl.xlabel("Time (s)")
            mpl.ylabel("Amplitude of Stimuli")
        else:
            mpl.cla()

            for x in self.trialled_firing[int(index)-1]:
                mpl.plot([x, x], [0, 10], "r-")

            mpl.plot(self.stimuli_time[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1],
                     self.stimuli_code[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1],
                     'ko', ms=6)

            for i, x in enumerate(self.stimuli_code[self.dictionary[int(index)-1]:self.dictionary[int(index)]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i+self.dictionary[int(index)-1]], x),
                             xytext=(self.stimuli_time[i+self.dictionary[int(index)-1]], 10.2),
                             color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=self.stimuli_time[self.dictionary[int(index)-1]],
                     xmax=self.stimuli_time[self.dictionary[int(index)]])

            mpl.xlabel("Time (s)")
            mpl.ylabel("Amplitude of Stimuli")

        fig = mpl.gcf()

        sio = io.BytesIO()
        fig.savefig(sio, format='png')
        return sio.getvalue()

    def baseline_statistics(self, trial):
        trial = int(trial)
        temporary_list = []
        stimulied_firing = []
        baseline_ms_bins = []
        if trial == 1:
            counter = 0
            for x in self.trialled_firing[trial-1]:
                if x <= self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1][counter]:
                    temporary_list.append(x)
                else:
                    stimulied_firing.append(temporary_list)
                    temporary_list = [x]
                    counter += 1
        else:
            counter = 1
            for x in self.trialled_firing[trial_selection-1]:
                if x <= self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial-1]:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1][counter]:
                    temporary_list.append(x)
                else:
                    stimulied_firing.append(temporary_list)
                    temporary_list = [x]
                    counter += 1
        stimulied_firing.append(temporary_list)

        if trial == 1:
            start_baseline = self.stimuli_time[0]-0.2
        else:
            start_baseline = self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial-1]+1]-0.2

        temp_slice = 0
        for i,x in enumerate(stimulied_firing[0]):
            if x >= start_baseline:
                temp_slice = i
                break
        random_list = stimulied_firing[0][temp_slice:]
        baseline_firings = random_list.copy()
        total = 0
        counter = 0
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
            baseline_ms_bins.append(total)
            start_baseline+=0.001
            total = 0
            counter += 1
        return stimulied_firing, baseline_ms_bins, baseline_firings

    def creating_stimulus_bins(self, stimulied_firing, stimtrig_sliced, stimtime_sliced, stimulus_selection = 0):
        initial_stimulus = stimtime_sliced[stimulus_selection]
        next_stimulus = stimtime_sliced[stimulus_selection+1]
        total = 0
        ms_bin = []
        random_list = stimulied_firing[stimulus_selection+1].copy()
        item = random_list.pop(0)
        while initial_stimulus <= next_stimulus:
            false_flag = True
            while false_flag:
                if item >= initial_stimulus and item < (initial_stimulus+0.001):
                    total += 1
                    try:
                        item = random_list.pop(0)
                    except IndexError:
                        false_flag = False
                else:
                    false_flag = False
            ms_bin.append(total)
            initial_stimulus+=0.001
            total = 0
        del random_list
        return stimtrig_sliced[stimulus_selection], ms_bin, stimtime_sliced[stimulus_selection], stimulied_firing[stimulus_selection+1]

    def all_stimulus_in_specific_trial(self, trial):
        stimulied_firing, baseline_bins, baseline_firings = self.baseline_statistics(trial)
        stimulus_ms_bins_dictionary = {}
        stimulus_time_dictionary = {}
        firings_during_stimulus = {}
        for x in range(0,10):
            stimulus_type, bin, type_time, stimulus_firings_list = self.creating_stimulus_bins(stimulied_firing, self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-10:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-10:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], x)
            stimulus_ms_bins_dictionary[stimulus_type] = bin
            stimulus_time_dictionary[stimulus_type] = type_time
            firings_during_stimulus[stimulus_type] = stimulus_firings_list
        return stimulus_ms_bins_dictionary, stimulied_firing, stimulus_time_dictionary, baseline_firings, firings_during_stimulus

    # No. of firings, length of experiment (s), average frequency of firings (Hz)
    def give_statistics_all_trials(self):
        return len(self.firing),\
               self.firing[-1]-float(3e-6),\
               len(self.firing)/(self.firing[-1]-float(3e-6))

    # No. of firings, start of trial (s), end of trial(s), length of trial (s), average freqeuncy of firings (Hz)
    def give_statistics_for_specific_trial(self, trial):
        trial = int(trial)
        if trial == 1:
            return len(self.trialled_firing[trial-1]),\
                   float(3e-6),\
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]],\
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-float(3e-6),\
                   len(self.trialled_firing[trial-1])/(self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-float(3e-6))
        else:
            return len(self.trialled_firing[trial-1]),\
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11],\
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]],\
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11],\
                   len(self.trialled_firing[trial-1])/(self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11])