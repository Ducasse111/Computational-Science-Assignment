import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as mpl

import Graph

##bullsshit to make it commit

class Application(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.activefile = None
        self.statustext = "Waiting"
        self.add_widgets()


    def add_widgets(self):
        self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
        self.Graphbutton = tk.Button(self, text = "Graph selected trial", command = self.Create_Graph)
        self.BrowseButton = tk.Button(self, text = "Browse", command = self.Browse)
        self.statuslabel = tk.Label(self, text = self.statustext)
        self.TrialEntry = tk.Entry(self)
        self.TrialLabel = tk.Label(self, text = "Trial Number:")
        self.quitButton.grid(column=0, row=0)
        self.Graphbutton.grid(column=0, row=1)
        self.TrialLabel.grid(column=0, row=2)
        self.TrialEntry.grid(column=1, row=2)
        self.BrowseButton.grid(column = 0, row = 3)
        self.statuslabel.grid(column = 0, row = 4)

    def UpdateStatus(self):
        self.statuslabel = tk.Label(self, text = self.statustext)
        self.statuslabel.grid(column = 0, row = 4)

    def Browse(self):
        self.activefile = filedialog.askopenfilename()
        self.statustext = "Opened file : \"" + self.activefile + "\""
        self.UpdateStatus()

    def Create_Graph(self):
        TrialNum = self.TrialEntry.get()
        print(TrialNum)
        mpl.close()
        if self.activefile != None:
            StimTrig_Stimuli, StimTrig_Time, Sch_wav_Time, trial_dictionary, Sch_wav_Time_Trialled = Graph.open_matlab_file(self.activefile)
            Graph.trial_graphs(Sch_wav_Time_Trialled, StimTrig_Stimuli, StimTrig_Time, trial_dictionary, TrialNum)
            self.statustext = "Graphing"
            self.UpdateStatus()
        else:
            self.statustext = "No File Selected"
            self.UpdateStatus()


app = Application()
app.master.title("Tkinter GUI V0.1")
app.mainloop()