import tkinter as tk
from tkinter import filedialog

import Graph


class Application(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.activefile = "Unloaded"
        self.NumberOfTrials = "Unknown"
        self.add_widgets()

    def add_widgets(self):
        self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
        self.Graphbutton = tk.Button(self, text = "Graph selected trial", command = self.Create_Graph)
        self.BrowseButton = tk.Button(self, text = "Browse", command = self.Browse)
        self.statustext = tk.Text(self, width = 30, height = 5)
        self.Trialtext = tk.Text(self, width = 30, height = 1)
        self.TrialEntry = tk.Entry(self)
        self.TrialEntry.bind('<Return>', self.Create_Graph)
        self.TrialLabel = tk.Label(self, text = "Trial Number:")
        self.Graphbutton.grid(column = 0, row = 0)
        self.TrialLabel.grid(column = 0, row = 1)
        self.TrialEntry.grid(column = 0, row = 2)
        self.BrowseButton.grid(column = 0, row = 3)
        self.Trialtext.grid(column = 0, row = 4)
        self.statustext.grid(column = 0, row = 5)
        self.quitButton.grid(column = 0, row = 6)
        self.statustext.insert("1.0","Waiting for input.\n")
        self.Trialtext.insert("1.0","Number of trials: " + self.NumberOfTrials + "\n")

    def Browse(self):
        self.activefile = filedialog.askopenfilename()
        self.activefile = self.activefile.split("/")
        self.activefile = self.activefile[len(self.activefile)-1]
        if self.activefile != "":
            self.statustext.insert("1.0","Opened file: \n\"" + self.activefile + "\"\n")
            self.StimTrig_Stimuli, self.StimTrig_Time, self.Sch_wav_Time, self.trial_dictionary,\
                self.Sch_wav_Time_Trialled, self.number_of_trials = Graph.open_matlab_file(self.activefile)
            self.Trialtext.insert("1.0","Number of trials: " + str(self.number_of_trials) + "\n")

    def Create_Graph(self, event):
        TrialNum = self.TrialEntry.get()
        self.statustext.insert("1.0","Attempting to graph trial "+TrialNum+" \nof file " + self.activefile + "\n")
        if self.activefile != None:

            try:
                Graph.trial_graphs(self.Sch_wav_Time_Trialled, self.StimTrig_Stimuli, self.StimTrig_Time, self.trial_dictionary, TrialNum)
            except IndexError:
                self.statustext.insert("1.0", "No such trial.\n")

        else:
            self.statustext.insert("1.0","No File Selected\n")

app = Application()
app.master.title("Tkinter GUI V0.5")
app.master.minsize(217,217)
app.mainloop()