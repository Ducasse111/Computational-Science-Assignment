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

        self.stimulus_time = []
        self.stimulus_code = []
        self.firing = []
        self.trialled_firing = []

        self.separate_dictionary = {}

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
            self.stimulus_time.append(x[0])
        for x in self.mat['StimTrig'][0][0][5]:
            if x[0] != 62:
                self.stimulus_code.append(x[0])
            else:
                self.stimulus_code.append(0)
                self.number_trials += 1
        for x in self.mat[temp_var][0][0][4]:
            self.firing.append(x[0])
        counter = 1
        for i, x in enumerate(self.stimulus_code):
            if x == 0:
                self.separate_dictionary[counter] = i
                counter += 1

        temp_list = []
        temp_key = 1
        for x in self.firing:
            try:
                if x <= self.stimulus_time[self.separate_dictionary[temp_key]]:
                    temp_list.append(x)
                else:
                    self.trialled_firing.append(temp_list)
                    temp_list = []
                    temp_key += 1
            except KeyError:
                break

    def get_graph(self, trial):
        user_selection = trial

        mpl.ioff()
        mpl.figure(num="Trial", figsize=[14, 7])

        mpl.cla()

        for x in self.trialled_firing[int(user_selection)-1]:
            mpl.plot([x, x], [0, 10], "r-")

        mpl.plot(self.stimulus_time[0:self.separate_dictionary[1]+1],
                 self.stimulus_time[0:self.separate_dictionary[1]+1], 'ko', ms=6)

        for i, x in enumerate(self.stimulus_time[0:self.separate_dictionary[1]+1]):
            mpl.annotate(s=str(x), xy=(self.stimulus_time[i], x), xytext=(self.stimulus_time[i], 10.2),
                         color='0.2', size=13, weight='bold')

        mpl.xlim(xmin=0, xmax=self.stimulus_time[self.separate_dictionary[1]])

        mpl.xlabel('Time (s)')
        mpl.ylabel('Amplitude of Stimuli')

        fig = mpl.gcf()

        # Creates a buffer to export the data as bytes which is then used in PIL to draw the image from the bytes
        image_io = io.BytesIO()
        fig.savefig(image_io, format='png')
        return image_io.getvalue()