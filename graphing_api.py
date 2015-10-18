import os
import sys
import io

import scipy.io as sc_io
import matplotlib.pyplot as mpl

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

        self.dictionary = {}

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
                self.dictionary[counter] = i
                counter += 1

        temp_list = []
        temp_key = 1
        for x in self.firing:
            try:
                if x <= self.stimuli_time[self.dictionary[temp_key]]:
                    temp_list.append(x)
                else:
                    self.trialled_firing.append(temp_list)
                    temp_list = []
                    temp_key += 1
            except KeyError:
                break

    def get_graph(self, trial):
        print(trial)
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