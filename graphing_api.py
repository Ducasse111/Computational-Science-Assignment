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

    ##################################
    # Opening file & Extracting data #
    ##################################

    def open_file(self, file):
        renamed_file = file.split('/')
        file_path = renamed_file[:-1]
        file_name = renamed_file[-1]

        path = ''.join(x + platform_filename for x in file_path)
        original_path = os.getcwd()

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

    ######################
    # Graphing functions #
    ######################

    # y-axis = amplitude of stimulus
    # x-axis = time (t)
    def get_graph(self, trial):
        index = trial
        if index == "1":
            mpl.cla()
            for x in self.trialled_firing[int(index)-1]:
                mpl.plot([x, x], [0, 10], "r-")

            mpl.plot(self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1],
                     self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1], 'ko', ms=6)

            for i, x in enumerate(self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i], x),
                             xytext=(self.stimuli_time[i], 10.2), color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=0, xmax=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[1]])

            mpl.xlabel("Time (s)")
            mpl.ylabel("Amplitude of Stimuli")
        else:
            mpl.cla()

            for x in self.trialled_firing[int(index)-1]:
                mpl.plot([x, x], [0, 10], "r-")

            mpl.plot(self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(index)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(index)]+1],
                     self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[int(index)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(index)]+1],
                     'ko', ms=6)

            for i, x in enumerate(self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[int(index)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(index)]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i+self.dictionary_marking_0s_index_in_stimuli_lists[int(index)-1]], x),
                             xytext=(self.stimuli_time[i+self.dictionary_marking_0s_index_in_stimuli_lists[int(index)-1]], 10.2),
                             color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(index)-1]],
                     xmax=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(index)]])

            mpl.xlabel("Time (s)")
            mpl.ylabel("Amplitude of Stimuli")

        fig = mpl.gcf()

        sio = io.BytesIO()
        fig.savefig(sio, format='png')
        return sio.getvalue()

    # Uses 1 ms bins to plot the histogram
    # Also plots when a stimulus is applied (annotates amplitude of stimulus)
    # y-axis = Frequency of firings (kHz)
    # x-axis = Time (s)
    def get_frequency_histogram_graph(self, trial):
        trial = int(trial)

        baseline_bins, \
        stimulus_ms_bins_dictionary, \
        stimulied_firing, \
        stimulus_time_dictionary, \
        baseline_firings, \
        firings_during_stimulus, \
        ms_time_dictionary = self.all_stimulus_in_specific_trial(trial)

        if trial == 1:
            x_bar = ms_time_dictionary[0]
            y_bar = stimulus_ms_bins_dictionary[0]
            for x in self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]]:
                x_bar.extend(ms_time_dictionary[x])
                y_bar.extend(stimulus_ms_bins_dictionary[x])

            mpl.cla()
            for x in self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1]:
                mpl.plot([x, x], [0, 3], "r-")

            mpl.bar(left=x_bar,height=y_bar,width=0.001)

            for i, x in enumerate(self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i], 3),
                             xytext=(self.stimuli_time[i], 3.05), color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=0, xmax=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[1]])
            mpl.ylim(ymin=0, ymax=3)

            mpl.xlabel("Time (s)")
            mpl.ylabel("Frequency of Neuron firings (kHz)")
        else:
            mpl.cla()

            x_bar = []
            y_bar = []
            for x in self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]]:
                x_bar.extend(ms_time_dictionary[x])
                y_bar.extend(stimulus_ms_bins_dictionary[x])

            for x in self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]+1]:
                mpl.plot([x, x], [0, 3], "r-")

            mpl.bar(left=x_bar,height=y_bar,width=0.001)

            for i, x in enumerate(self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i+self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]], 3),
                             xytext=(self.stimuli_time[i+self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]], 3.05),
                             color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]],
                     xmax=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]])
            mpl.ylim(ymin=0, ymax=3)

            mpl.xlabel("Time (s)")
            mpl.ylabel("Frequency of Neuron firings (kHz)")

        fig = mpl.gcf()

        sio = io.BytesIO()
        fig.savefig(sio, format='png')
        return sio.getvalue()

    # Same as get_frequency_histogram_graph, but uses 10 ms bins to plot the histogram
    # y-axis = Frequency of firings (100 hz's)
    def get_frequency_histogram_graph_per_10ms(self, trial):
        trial = int(trial)

        baseline_bins, \
        stimulus_ms_bins_dictionary, \
        stimulied_firing, \
        stimulus_time_dictionary, \
        baseline_firings, \
        firings_during_stimulus, \
        ms_time_dictionary = self.all_stimulus_in_specific_trial_per_10ms(trial)

        if trial == 1:
            x_bar = ms_time_dictionary[0]
            y_bar = stimulus_ms_bins_dictionary[0]
            for x in self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]]:
                x_bar.extend(ms_time_dictionary[x])
                y_bar.extend(stimulus_ms_bins_dictionary[x])

            mpl.cla()
            for x in self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1]:
                mpl.plot([x, x], [0, 5], "r-")

            mpl.bar(left=x_bar,height=y_bar,width=0.01)

            for i, x in enumerate(self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i], 5),
                             xytext=(self.stimuli_time[i], 5.05), color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=0, xmax=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[1]])
            mpl.ylim(ymin=0, ymax=5)

            mpl.xlabel("Time (s)")
            mpl.ylabel("Frequency of Neuron firings (Hundred Hz)")
        else:
            mpl.cla()

            x_bar = []
            y_bar = []
            for x in self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]]:
                x_bar.extend(ms_time_dictionary[x])
                y_bar.extend(stimulus_ms_bins_dictionary[x])

            for x in self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]+1]:
                mpl.plot([x, x], [0, 5], "r-")

            mpl.bar(left=x_bar,height=y_bar,width=0.01)

            for i, x in enumerate(self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]:self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]+1]):
                mpl.annotate(s=str(x), xy=(self.stimuli_time[i+self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]], 5),
                             xytext=(self.stimuli_time[i+self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]], 5.05),
                             color='0.2', size=13, weight="bold")

            mpl.xlim(xmin=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)-1]],
                     xmax=self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[int(trial)]])
            mpl.ylim(ymin=0, ymax=5)

            mpl.xlabel("Time (s)")
            mpl.ylabel("Frequency of Neuron firings (Hundred Hz)")

        fig = mpl.gcf()

        sio = io.BytesIO()
        fig.savefig(sio, format='png')
        return sio.getvalue()

    ######################
    # 10ms bins analysis #
    ######################

    # Create 10ms bins for the baseline
    def baseline_statistics_per_10ms(self, trial):
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
            for x in self.trialled_firing[trial-1]:
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
        while counter != 20:
            false_flag = True
            while false_flag:
                if item >= start_baseline and item < (start_baseline+0.01):
                    total += 1
                    try:
                        item = random_list.pop(0)
                    except IndexError:
                        false_flag = False
                else:
                    false_flag = False
            baseline_ms_bins.append(total)
            start_baseline+=0.01
            total = 0
            counter += 1
        return stimulied_firing, baseline_ms_bins, baseline_firings

    # Create 10ms bins for the interval before the first stimulus is applied
    def creating_stimulus_bins_before_first_stimulus_per_10ms(self, stimulied_firing, stimtime_sliced, first_trial=False):
        if first_trial:
            initial_stimulus = 0
        else:
            initial_stimulus = stimtime_sliced[0]
        next_stimulus = stimtime_sliced[1]
        total = 0
        ms_bin = []
        ms_time = [initial_stimulus]
        random_list = stimulied_firing[0].copy()
        item = random_list.pop(0)
        while initial_stimulus <= next_stimulus:
            false_flag = True
            while false_flag:
                if item >= initial_stimulus and item < (initial_stimulus+0.01):
                    total += 1
                    try:
                        item = random_list.pop(0)
                    except IndexError:
                        false_flag = False
                else:
                    false_flag = False
            ms_bin.append(total)
            initial_stimulus+=0.01
            ms_time.append(initial_stimulus)
            total = 0
        del random_list
        return ms_bin, stimtime_sliced[0], stimulied_firing[0], ms_time

    # Create 10ms bins for a specific stimulus
    def creating_stimulus_bins_per_10ms(self, stimulied_firing, stimtrig_sliced, stimtime_sliced, stimulus_selection = 0):
        initial_stimulus = stimtime_sliced[stimulus_selection]
        next_stimulus = stimtime_sliced[stimulus_selection+1]
        total = 0
        ms_bin = []
        ms_time = [initial_stimulus]
        random_list = stimulied_firing[stimulus_selection+1].copy()
        item = random_list.pop(0)
        while initial_stimulus <= next_stimulus:
            false_flag = True
            while false_flag:
                if item >= initial_stimulus and item < (initial_stimulus+0.01):
                    total += 1
                    try:
                        item = random_list.pop(0)
                    except IndexError:
                        false_flag = False
                else:
                    false_flag = False
            ms_bin.append(total)
            initial_stimulus+=0.01
            ms_time.append(initial_stimulus)
            total = 0
        del random_list
        return stimtrig_sliced[stimulus_selection], ms_bin, stimtime_sliced[stimulus_selection], stimulied_firing[stimulus_selection+1], ms_time

    # Creating 10ms bins for all stimuli in a trial
    # Stimulus 10ms bin refers to binning the firings in 10ms intervals from the stimulus until the next
    def all_stimulus_in_specific_trial_per_10ms(self, trial):
        trial = int(trial)
        stimulied_firing, baseline_bins, baseline_firings = self.baseline_statistics_per_10ms(trial)
        stimulus_ms_bins_dictionary = {}
        stimulus_time_dictionary = {}
        firings_during_stimulus = {}
        ms_time_dictionary = {}
        for x in range(0,10):
            stimulus_type, bin, type_time, stimulus_firings_list, ms_time = self.creating_stimulus_bins_per_10ms(stimulied_firing, self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-10:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-10:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], x)
            bin.append(0)
            stimulus_ms_bins_dictionary[stimulus_type] = bin
            stimulus_time_dictionary[stimulus_type] = type_time
            firings_during_stimulus[stimulus_type] = stimulus_firings_list
            ms_time_dictionary[stimulus_type] = ms_time
        if trial == 1:
            ms_bin_initial,start,firings_during_initial,ms_time_initial = self.creating_stimulus_bins_before_first_stimulus_per_10ms(stimulied_firing, self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], True)
        else:
            ms_bin_initial,start,firings_during_initial,ms_time_initial = self.creating_stimulus_bins_before_first_stimulus_per_10ms(stimulied_firing, self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1])
        ms_bin_initial.append(0)
        stimulus_ms_bins_dictionary[0] = ms_bin_initial
        stimulus_time_dictionary[0] = start
        firings_during_stimulus[0] = firings_during_initial
        ms_time_dictionary[0] = ms_time_initial
        return baseline_bins, \
               stimulus_ms_bins_dictionary, \
               stimulied_firing, \
               stimulus_time_dictionary, \
               baseline_firings, \
               firings_during_stimulus, \
               ms_time_dictionary

    # Identify when after a stimulus is applied that the responses are statistically significant
    def statistical_analysis_specific_stimulus_per_10ms(self, stimulus_index, trial, stimtrig_sliced):
        file_mean, file_std = self.baseline_statistics_all_trials_per_10ms()
        baseline_bins, \
        stimulus_ms_bins_dictionary, \
        stimulied_firing, \
        stimulus_time_dictionary, \
        baseline_firings, \
        firings_during_stimulus, \
        ms_time_dictionary = self.all_stimulus_in_specific_trial_per_10ms(trial)
        trial_mean, trial_std = np.mean(baseline_bins), np.std(baseline_bins)

        specific_stimulus_type = stimtrig_sliced[stimulus_index]

        file_baseline_statistically_significant = 0
        file_flag = True
        trial_baseline_statistically_significant = 0
        trial_flag = True

        for i,x in enumerate(stimulus_ms_bins_dictionary[specific_stimulus_type]):
            if x > (file_mean + (1.64 * file_std)) and file_flag:
                file_baseline_statistically_significant = ms_time_dictionary[specific_stimulus_type][i]
                file_flag = False
            if x > (trial_mean + (1.64 * trial_std)) and trial_flag:
                trial_baseline_statistically_significant = ms_time_dictionary[specific_stimulus_type][i]
                trial_flag = False

        return file_baseline_statistically_significant, trial_baseline_statistically_significant, specific_stimulus_type
        # return time value of when responses (ms bin) are statistically significant
        # file refers to using average baseline from all trials
        # trial refers to using only baseline from the selected trial

    # Statistically analyze all the stimuli in a trial, returning a dictionary
    def statistical_analysis_all_stimulus_in_trial_per_10ms(self, trial):
        trial = int(trial)
        dictionary_when_firings_are_statistically_significant_after_stimulus_application = {}
        if trial == 1:
            for x in range(0,10):
                a,b,c=self.statistical_analysis_specific_stimulus_per_10ms(x, trial, self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]])
                dictionary_when_firings_are_statistically_significant_after_stimulus_application[c] = [a,b]
        else:
            for x in range(0,10):
                a,b,c=self.statistical_analysis_specific_stimulus_per_10ms(x, trial, self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[trial-1]+1:self.dictionary_marking_0s_index_in_stimuli_lists[trial]])
                dictionary_when_firings_are_statistically_significant_after_stimulus_application[c] = [a,b]
        return dictionary_when_firings_are_statistically_significant_after_stimulus_application

    # Average baseline of whole file (all trials baseline's averaged)
    def baseline_statistics_all_trials_per_10ms(self):
        mean_list = []
        std_list = []
        for x in range(1, self.number_trials+1):
            temp_baseline_ms_list,b,c,d,e,f,g = self.all_stimulus_in_specific_trial_per_10ms(x)
            mean_list.append(np.mean(temp_baseline_ms_list))
            std_list.append(np.std(temp_baseline_ms_list))
        return np.mean(mean_list), np.std(std_list)

    ####################
    # ms bins analysis #
    ####################

    # Functions are same as the 10 ms bins analysis functions, but these create & use 1 ms bin functions

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
            for x in self.trialled_firing[trial-1]:
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

    def creating_stimulus_bins_before_first_stimulus(self, stimulied_firing, stimtime_sliced, first_trial=False):
        if first_trial:
            initial_stimulus = 0
        else:
            initial_stimulus = stimtime_sliced[0]
        next_stimulus = stimtime_sliced[1]
        total = 0
        ms_bin = []
        ms_time = [initial_stimulus]
        random_list = stimulied_firing[0].copy()
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
            ms_time.append(initial_stimulus)
            total = 0
        del random_list
        return ms_bin, stimtime_sliced[0], stimulied_firing[0], ms_time

    def creating_stimulus_bins(self, stimulied_firing, stimtrig_sliced, stimtime_sliced, stimulus_selection = 0):
        initial_stimulus = stimtime_sliced[stimulus_selection]
        next_stimulus = stimtime_sliced[stimulus_selection+1]
        total = 0
        ms_bin = []
        ms_time = [initial_stimulus]
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
            ms_time.append(initial_stimulus)
            total = 0
        del random_list
        return stimtrig_sliced[stimulus_selection], ms_bin, stimtime_sliced[stimulus_selection], stimulied_firing[stimulus_selection+1], ms_time

    def all_stimulus_in_specific_trial(self, trial):
        trial = int(trial)
        stimulied_firing, baseline_bins, baseline_firings = self.baseline_statistics(trial)
        stimulus_ms_bins_dictionary = {}
        stimulus_time_dictionary = {}
        firings_during_stimulus = {}
        ms_time_dictionary = {}
        for x in range(0,10):
            stimulus_type, bin, type_time, stimulus_firings_list, ms_time = self.creating_stimulus_bins(stimulied_firing, self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-10:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-10:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], x)
            bin.append(0)
            stimulus_ms_bins_dictionary[stimulus_type] = bin
            stimulus_time_dictionary[stimulus_type] = type_time
            firings_during_stimulus[stimulus_type] = stimulus_firings_list
            ms_time_dictionary[stimulus_type] = ms_time
        if trial == 1:
            ms_bin_initial,start,firings_during_initial,ms_time_initial = self.creating_stimulus_bins_before_first_stimulus(stimulied_firing, self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1], True)
        else:
            ms_bin_initial,start,firings_during_initial,ms_time_initial = self.creating_stimulus_bins_before_first_stimulus(stimulied_firing, self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11:self.dictionary_marking_0s_index_in_stimuli_lists[trial]+1])
        ms_bin_initial.append(0)
        stimulus_ms_bins_dictionary[0] = ms_bin_initial
        stimulus_time_dictionary[0] = start
        firings_during_stimulus[0] = firings_during_initial
        ms_time_dictionary[0] = ms_time_initial
        return baseline_bins, \
               stimulus_ms_bins_dictionary, \
               stimulied_firing, \
               stimulus_time_dictionary, \
               baseline_firings, \
               firings_during_stimulus, \
               ms_time_dictionary

    # stimtrig_sliced needs to be first actual stimulus to last actual stimulus
    # stimtrig_sliced doesn't include 0's
    # stimulus_index refers to which stimulus in the trial to look at (0 meaning the first, not including 0 stimulus (reset stimulus))
    # stimulus_index is an element of [0,9]
    def statistical_analysis_specific_stimulus(self, stimulus_index, trial, stimtrig_sliced):
        file_mean, file_std = self.baseline_statistics_all_trials()
        baseline_bins, \
        stimulus_ms_bins_dictionary, \
        stimulied_firing, \
        stimulus_time_dictionary, \
        baseline_firings, \
        firings_during_stimulus, \
        ms_time_dictionary = self.all_stimulus_in_specific_trial(trial)
        trial_mean, trial_std = np.mean(baseline_bins), np.std(baseline_bins)

        specific_stimulus_type = stimtrig_sliced[stimulus_index]

        file_baseline_statistically_significant = 0
        file_flag = True
        trial_baseline_statistically_significant = 0
        trial_flag = True

        for i,x in enumerate(stimulus_ms_bins_dictionary[specific_stimulus_type]):
            if x > (file_mean + (1.64 * file_std)) and file_flag:
                file_baseline_statistically_significant = ms_time_dictionary[specific_stimulus_type][i]
                file_flag = False
            if x > (trial_mean + (1.64 * trial_std)) and trial_flag:
                trial_baseline_statistically_significant = ms_time_dictionary[specific_stimulus_type][i]
                trial_flag = False

        return file_baseline_statistically_significant, trial_baseline_statistically_significant, specific_stimulus_type
        # return time value of when responses (ms bin) are statistically significant
        # file refers to using average baseline from all trials
        # trial refers to using only baseline from the selected trial

    def statistical_analysis_all_stimulus_in_trial(self, trial):
        trial = int(trial)
        dictionary_when_firings_are_statistically_significant_after_stimulus_application = {}
        if trial == 1:
            for x in range(0,10):
                a,b,c=self.statistical_analysis_specific_stimulus(x, trial, self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[1]])
                dictionary_when_firings_are_statistically_significant_after_stimulus_application[c] = [a,b]
        else:
            for x in range(0,10):
                a,b,c=self.statistical_analysis_specific_stimulus(x, trial, self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[trial-1]+1:self.dictionary_marking_0s_index_in_stimuli_lists[trial]])
                dictionary_when_firings_are_statistically_significant_after_stimulus_application[c] = [a,b]
        return dictionary_when_firings_are_statistically_significant_after_stimulus_application

    def baseline_statistics_all_trials(self):
        mean_list = []
        std_list = []
        for x in range(1, self.number_trials+1):
            temp_baseline_ms_list,b,c,d,e,f,g = self.all_stimulus_in_specific_trial(x)
            mean_list.append(np.mean(temp_baseline_ms_list))
            std_list.append(np.std(temp_baseline_ms_list))
        return np.mean(mean_list), np.std(std_list)

    ############################
    # Show general information #
    ############################

    # No. of firings, length of experiment (s), average frequency of firings (Hz)
    def give_statistics_all_trials(self):
        return len(self.firing), \
               self.firing[-1]-float(3e-6), \
               len(self.firing)/(self.firing[-1]-float(3e-6))

    # No. of firings, start of trial (s), end of trial(s), length of trial (s), average freqeuncy of firings (Hz)
    # Time_value of when stimulus was applied (list of 10 values, doesn't include 0's)
    # Stimulus_code of the order of stimulus application (list of 10 values), corresponds to Time_value, doesn't include 0's
    def give_statistics_for_specific_trial(self, trial):
        trial = int(trial)
        if trial == 1:
            return len(self.trialled_firing[trial-1]), \
                   float(3e-6), \
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]], \
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-float(3e-6), \
                   len(self.trialled_firing[trial-1])/(self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-float(3e-6)), \
                   self.stimuli_time[0:self.dictionary_marking_0s_index_in_stimuli_lists[trial]], \
                   self.stimuli_code[0:self.dictionary_marking_0s_index_in_stimuli_lists[trial]]
        else:
            return len(self.trialled_firing[trial-1]), \
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11], \
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]], \
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11], \
                   len(self.trialled_firing[trial-1])/(self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]]-self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial]-11]), \
                   self.stimuli_time[self.dictionary_marking_0s_index_in_stimuli_lists[trial-1]+1:self.dictionary_marking_0s_index_in_stimuli_lists[trial]], \
                   self.stimuli_code[self.dictionary_marking_0s_index_in_stimuli_lists[trial-1]+1:self.dictionary_marking_0s_index_in_stimuli_lists[trial]]
